#!/usr/bin/env python3
"""Collect supported annual ACA parameter tables from official HHS/IRS sources.
No credentials, household data, or third-party estimates are sent to these sources.
"""
import argparse, concurrent.futures, copy, datetime as dt, hashlib, html, json, math, re
from html.parser import HTMLParser
from decimal import Decimal
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen

API='https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/api'
IRS_INDEX='https://www.irs.gov/internal-revenue-bulletins'
REGIONS=('US','AK','HI')
BANDS=((100,133),(133,150),(150,200),(200,250),(250,300),(300,400))
ACA_SECTIONS=('acaPoverty','acaContribution')
SOURCE_HOSTS=('aspe.hhs.gov','www.irs.gov','www.federalregister.gov','www.govinfo.gov')
class NotPublished(ValueError): pass
class ReviewRequired(ValueError): pass

def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def fetch(url):
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.netloc not in SOURCE_HOSTS: raise ReviewRequired('Unapproved data source')
    request=Request(url,headers={'User-Agent':'RonFinanceACAUpdates/1.0 (+https://github.com/ronholl/ronsfinancemodel)','Accept':'application/json,text/html'})
    with urlopen(request,timeout=25) as response:
        if urlparse(response.url).netloc not in SOURCE_HOSTS:raise ReviewRequired('Unapproved source redirect')
        limit=25_000_000 if parsed.netloc=='www.irs.gov' else 1_000_000
        body=response.read(limit+1)
        if len(body)>limit:raise ReviewRequired('Source response too large')
        return body.decode('utf-8')

def integer(value):
    if isinstance(value,bool) or not re.fullmatch(r'\d+',str(value)):raise ReviewRequired('Expected a positive whole number')
    return int(value)

def parse_hhs(payload,year,region,size):
    if isinstance(payload,str):payload=json.loads(payload)
    if not isinstance(payload,dict) or payload.get('status')!=200 or not isinstance(payload.get('data'),dict):raise ReviewRequired('Unsupported HHS response')
    data=payload['data']
    returned=integer(data.get('year'))
    # HHS explicitly defaults an invalid/future year to the current year. Never relabel that as new data.
    if returned<year:raise NotPublished(f'HHS {year} is not published (API returned {returned})')
    if returned!=year or str(data.get('state','')).upper()!=region or integer(data.get('household_size'))!=size:raise ReviewRequired('HHS response year, region, or household size mismatch')
    values=[data[k] for k in ('income','poverty_threshold') if k in data]
    if not values or len({integer(v) for v in values})!=1:raise ReviewRequired('Missing or conflicting HHS income fields')
    amount=integer(values[0])
    if amount<=0 or amount>500000:raise ReviewRequired('HHS guideline is out of range')
    return amount

def collect_fpl(year,get=fetch):
    receipts={}
    def read(region,size):
        url=f'{API}/{year}/{region.lower()}/{size}'
        raw=get(url);amount=parse_hhs(raw,year,region,size)
        return region,size,amount,json.loads(raw) if isinstance(raw,str) else raw
    first=read('US',1);receipts['US-1']=first[3]
    jobs=[(r,n) for r in REGIONS for n in range(1,9) if (r,n)!=('US',1)]
    amounts={('US',1):first[2]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for region,size,amount,raw in pool.map(lambda args:read(*args),jobs):amounts[(region,size)]=amount;receipts[f'{region}-{size}']=raw
    guidelines={}
    for region in REGIONS:
        base=amounts[(region,1)];increment=amounts[(region,2)]-base
        if increment<=0 or any(amounts[(region,n)]!=base+(n-1)*increment for n in range(1,9)):raise ReviewRequired('HHS regional table no longer has the supported uniform increment')
        guidelines[region]=[base,increment]
    return {'id':f'hhs-aca-poverty-{year+1}-'+digest(canonical(guidelines))[:12],'year':year+1,'section':'acaPoverty','title':'ACA poverty guidelines','summary':f'Official HHS {year} poverty guidelines for {year+1} Marketplace coverage; all three regions and household sizes 1–8 verified.','source':{'agency':'HHS','url':f'{API}/{year}/us/1','reference':f'{year} HHS poverty guidelines'},'evidence':{'method':'HHS official API; year/region/size and arithmetic verified','sha256':digest(canonical(receipts))},'values':{'acaPovertyGuidelineYear':year,'acaPovertyGuidelines':guidelines}}

def parse_govinfo_fpl(raw,year,document_number,url):
    text=html.unescape(re.sub(r'<[^>]+>',' ',raw))
    if f'[FR Doc No: {document_number}]' not in text or 'AGENCY: Department of Health and Human Services.' not in text or 'Annual Update of the HHS Poverty Guidelines' not in text:
        raise ReviewRequired('Federal Register document identity or HHS agency mismatch')
    headings=list(re.finditer(r'(20\d{2})\s+Poverty Guidelines for (?:the )?(48 Contiguous States and the District of\s+Columbia|Alaska|Hawaii)',text,re.I))
    if len(headings)!=3 or any(int(m[1])!=year for m in headings):raise ReviewRequired('HHS notice year or regional headings changed')
    guidelines={}
    for i,m in enumerate(headings):
        region='US' if m[2].startswith('48') else {'alaska':'AK','hawaii':'HI'}[m[2].lower()]
        if region in guidelines:raise ReviewRequired('Duplicate HHS regional table')
        block=text[m.end():headings[i+1].start() if i<2 else len(text)]
        rows=re.findall(r'^\s*([1-8])\.{3,}\s*\$?([\d,]+)\s*$',block,re.M)
        if [int(r[0]) for r in rows]!=list(range(1,9)):raise ReviewRequired('HHS notice must contain all eight household sizes')
        amounts=[int(r[1].replace(',','')) for r in rows];base=amounts[0];increment=amounts[1]-base
        extra=re.search(r'more than 8 persons, add \$([\d,]+) for\s+each additional person',block)
        if not extra or int(extra[1].replace(',',''))!=increment or increment<=0 or any(v!=base+n*increment for n,v in enumerate(amounts)):raise ReviewRequired('HHS notice per-person increment or arithmetic changed')
        guidelines[region]=[base,increment]
    u={'id':f'hhs-aca-poverty-{year+1}-'+digest(canonical(guidelines))[:12],'year':year+1,'section':'acaPoverty','title':'ACA poverty guidelines','summary':f'Official HHS {year} poverty guidelines for {year+1} Marketplace coverage; all three regions and household sizes 1–8 verified.','source':{'agency':'HHS','url':url,'reference':f'{year} HHS poverty guidelines, Federal Register {document_number}'},'evidence':{'method':'Official HHS Federal Register notice on GovInfo; document identity, year, regions, sizes and arithmetic verified','sha256':digest(raw)},'values':{'acaPovertyGuidelineYear':year,'acaPovertyGuidelines':guidelines}}
    validate_update(u)
    return u

def collect_fpl_register(year,get=fetch):
    params={'conditions[term]':'"Annual Update of the HHS Poverty Guidelines"','conditions[agencies][]':'health-and-human-services-department','conditions[type][]':'NOTICE','conditions[publication_date][gte]':f'{year}-01-01','conditions[publication_date][lte]':f'{year}-12-31','per_page':100,'order':'newest'}
    data=json.loads(get('https://www.federalregister.gov/api/v1/documents.json?'+urlencode(params)))
    # Official API omits results/total_pages entirely for a successful zero-match query.
    if isinstance(data,dict) and data.get('count')==0 and isinstance(data.get('description'),str) and 'results' not in data:data['results']=[]
    if not isinstance(data,dict) or not isinstance(data.get('results'),list) or not isinstance(data.get('count'),int) or data.get('total_pages',0)>1 or data['count']!=len(data['results']):raise ReviewRequired('Incomplete Federal Register discovery response')
    docs=[d for d in data['results'] if d.get('title')=='Annual Update of the HHS Poverty Guidelines' and d.get('type')=='Notice' and any(a.get('slug')=='health-and-human-services-department' for a in d.get('agencies',[]))]
    if not docs:raise NotPublished(f'HHS {year}: no annual guidelines notice published in Federal Register')
    if len(docs)!=1:raise ReviewRequired('Multiple HHS annual notices require review')
    d=docs[0];number=d.get('document_number','');date=d.get('publication_date','')
    if not re.fullmatch(fr'{year}-\d{{5}}',number) or not re.fullmatch(fr'{year}-\d{{2}}-\d{{2}}',date):raise ReviewRequired('Federal Register document number or publication year mismatch')
    expected=f'https://www.govinfo.gov/content/pkg/FR-{date}/pdf/{number}.pdf'
    if d.get('pdf_url')!=expected:raise ReviewRequired('Unrecognized official Federal Register publication URL')
    url=expected.replace('/pdf/','/html/').replace('.pdf','.htm')
    u=parse_govinfo_fpl(get(url),year,number,url);u['source']['published']=date
    return u

def collect_fpl_resilient(year,get=fetch):
    try:return collect_fpl(year,get)
    except (URLError,TimeoutError,OSError):return collect_fpl_register(year,get)

class GovHTML(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.text=[];self.links=[];self.tables=[];self.table=None;self.cell=None;self.row=None;self.nested=0;self.heading=None;self.procedure=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('h1','h2','h3','h4'):self.heading=[]
        if tag=='a' and attrs.get('href'):self.links.append(attrs['href'])
        if tag=='table':
            if self.table is not None:self.nested+=1
            else:self.table={'before':' '.join(self.text)[-12000:],'procedure':self.procedure,'rows':[]}
        if self.table is not None and not self.nested:
            if tag=='tr':self.row=[]
            if tag in ('th','td'):self.cell=[]
        if tag in ('p','h1','h2','h3','br'):self.text.append('\n')
    def handle_data(self,data):
        self.text.append(data)
        if self.heading is not None:self.heading.append(data)
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('h1','h2','h3','h4') and self.heading is not None:
            proc=re.search(r'Rev\.\s*Proc\.\s*(\d{4}-\d+)', ' '.join(self.heading))
            if proc:self.procedure=proc[1]
            self.heading=None
        if self.table is not None and not self.nested:
            if tag in ('th','td') and self.cell is not None:
                if self.row is not None:self.row.append(' '.join(' '.join(self.cell).split()))
                self.cell=None
            if tag=='tr' and self.row is not None:self.table['rows'].append(self.row);self.row=None
        if tag=='table' and self.table is not None:
            if self.nested:self.nested-=1
            else:self.tables.append(self.table);self.table=None
        if tag in ('p','h1','h2','h3'):self.text.append('\n')

def parse_irs(raw,url):
    if not re.search(r'Initial[\s\S]{0,80}percentage',raw,re.I):return []
    parsed=GovHTML();parsed.feed(raw);out=[]
    for table in parsed.tables:
        rows=table['rows']
        if not rows or len(rows[0])!=3 or not all(t in ' '.join(rows[0]).lower() for t in ('household income','initial percentage','final percentage')):continue
        years=re.findall(r'Applicable\s+Percentage\s+Table\s+for\s+(20\d{2})',table['before'],re.I)
        if not years:raise ReviewRequired('IRS table has no unambiguous coverage-year heading')
        year=int(years[-1])
        if year<2026:continue
        body=rows[1:]
        if len(body)!=6:raise ReviewRequired(f'IRS {year}: changed subsidy bands need an app rule review')
        rates=[]
        for i,row in enumerate(body):
            if len(row)!=3:raise ReviewRequired('IRS table column count changed')
            nums=[int(n) for n in re.findall(r'(\d+)%',row[0])]
            expected=[133] if i==0 else list(BANDS[i])
            if nums!=expected or (i==0 and 'less than' not in row[0].lower()) or (i==5 and 'not more than' not in row[0].lower()):raise ReviewRequired('IRS income bands changed; do not reuse the old eligibility rule')
            values=[]
            for cell in row[1:]:
                match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*%',cell)
                if not match:raise ReviewRequired('IRS percentage cell is not a literal percentage')
                values.append(float(Decimal(match[1])/Decimal(100)))
            if not 0<=values[0]<=values[1]<=.25:raise ReviewRequired('IRS contribution percentages are out of range')
            rates.append([*BANDS[i],*values])
        procedures=re.findall(r'Rev\.\s*Proc\.\s*(\d{4}-\d+)',table['before'])
        heading=re.search(r'<h1\b[^>]*>.*?Internal Revenue Bulletin.*?</h1>([\s\S]{0,1600})',raw,re.I)
        date_match=re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(20\d{2})',re.sub('<[^>]+>',' ',heading[1] if heading else ''))
        source={'agency':'IRS','url':url,'reference':'Revenue Procedure '+table['procedure'] if table.get('procedure') else f'{year} applicable percentage table'}
        if date_match:source['published']=dt.datetime.strptime(' '.join(date_match.groups()),'%B %d %Y').date().isoformat()
        out.append({'id':f'irs-aca-contribution-{year}-'+digest(canonical(rates))[:12],'year':year,'section':'acaContribution','title':'ACA contribution percentages','summary':f'Official IRS {year} premium-tax-credit contribution percentages; supported six-band table verified.','source':source,'evidence':{'method':'Official IRS bulletin table; coverage year, percentage cells and band structure verified','sha256':digest(raw)},'values':{'acaContributionRates':rates,'acaMinimumFpl':100,'acaMaximumFpl':400}})
    return out

def discover_irs(get=fetch,pages=3):
    links=set()
    for page in range(pages):
        url=IRS_INDEX+('' if page==0 else f'?page={page}');p=GovHTML();p.feed(get(url))
        for href in p.links:
            absolute=urljoin(IRS_INDEX,href)
            if re.fullmatch(r'https://www\.irs\.gov/irb/20\d{2}-\d{1,2}_IRB',absolute,re.I):links.add(absolute)
            # The official index links PDF editions. Their bulletin identifiers also name the IRS HTML editions.
            pdf=re.fullmatch(r'https://www\.irs\.gov/pub/irs-irbs/irb(\d{2})-(\d{1,2})\.pdf',absolute,re.I)
            if pdf:links.add(f'https://www.irs.gov/irb/{2000+int(pdf[1])}-{pdf[2]}_IRB')
    if not links:raise ReviewRequired('IRS bulletin index returned no bulletin links')
    return sorted(links)

def validate_update(u):
    year=u.get('year');v=u.get('values',{});source=urlparse(u.get('source',{}).get('url',''))
    if not isinstance(year,int) or isinstance(year,bool) or not 2026<=year<=2100:raise ReviewRequired('Invalid ACA coverage year')
    if source.scheme!='https' or source.username or source.password:raise ReviewRequired('Invalid official source URL')
    if u.get('section')=='acaPoverty':
        if source.hostname not in ('aspe.hhs.gov','public-inspection.federalregister.gov','www.hhs.gov','www.federalregister.gov','www.govinfo.gov'):raise ReviewRequired('Unsupported HHS source')
        if set(v)!=set(('acaPovertyGuidelineYear','acaPovertyGuidelines')) or v['acaPovertyGuidelineYear']!=year-1:raise ReviewRequired('Coverage/guideline year mismatch')
        f=v['acaPovertyGuidelines']
        if set(f)!=set(REGIONS) or any(not isinstance(f[k],list) or len(f[k])!=2 or any(isinstance(x,bool) or not isinstance(x,int) or not 0<x<=200000 for x in f[k]) for k in REGIONS):raise ReviewRequired('Invalid regional FPL table')
    elif u.get('section')=='acaContribution':
        if source.hostname not in ('www.irs.gov','irs.gov'):raise ReviewRequired('Unsupported IRS source')
        if set(v)!=set(('acaContributionRates','acaMinimumFpl','acaMaximumFpl')) or v['acaMinimumFpl']!=100 or v['acaMaximumFpl']!=400:raise ReviewRequired('Unsupported subsidy eligibility bounds')
        rows=v['acaContributionRates']
        if not isinstance(rows,list) or len(rows)!=6 or any(not isinstance(r,list) or len(r)!=4 or r[:2]!=list(BANDS[i]) or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in r) or not 0<=r[2]<=r[3]<=.25 for i,r in enumerate(rows)):raise ReviewRequired('Invalid contribution table')
    else:raise ReviewRequired('Unsupported ACA section')
    if not isinstance(u.get('id'),str) or not u['id']:raise ReviewRequired('Missing update id')

def merge_updates(manifest,updates,checked_at,errors=None,pending=None):
    if manifest.get('schemaVersion')!=1 or not isinstance(manifest.get('updates'),list):raise ReviewRequired('Unsupported manifest format')
    result=copy.deepcopy(manifest);new={};conflicts=set()
    for u in updates:
        validate_update(u);key=(u['year'],u['section'])
        if key in new and new[key]['values']!=u['values']:conflicts.add(key)
        else:new[key]=u
    if conflicts:raise ReviewRequired('Conflicting official tables require review: '+str(sorted(conflicts)))
    # Preserve all existing non-ACA sections and older ACA years. Replace only the exact year/section found.
    for key,u in new.items():
        old=[x for x in result['updates'] if (x.get('year'),x.get('section'))==key]
        if len(old)==1 and old[0].get('values')==u['values']:continue
        result['updates']=[x for x in result['updates'] if (x.get('year'),x.get('section'))!=key]+[u]
    result['acaMonitor']={'checkedAt':checked_at,'status':'needs-review' if errors else 'ok','errors':errors or [],'pending':pending or [],'latestContributionYear':max([x['year'] for x in result['updates'] if x.get('section')=='acaContribution'],default=None),'latestGuidelineYear':max([x['values']['acaPovertyGuidelineYear'] for x in result['updates'] if x.get('section')=='acaPoverty'],default=None),'method':'Weekly official HHS API/Federal Register and IRS bulletin checks; unsupported rule changes require review.'}
    if result['updates']!=manifest['updates']:result['publishedAt']=checked_at[:10]
    return result

def run(manifest,get=fetch,today=None):
    today=today or dt.datetime.now(dt.timezone.utc).date();updates=[];errors=[];pending=[]
    for year in range(max(2025,today.year-1),today.year+2):
        try:updates.append(collect_fpl_resilient(year,get))
        except NotPublished as e:pending.append(str(e))
        except Exception as e:errors.append(f'HHS {year}: {e}')
    try:
        urls=discover_irs(get)
        def read(url):
            try:return parse_irs(get(url),url),None
            except Exception as e:return [],f'IRS {url}: {e}'
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for found,error in pool.map(read,urls):updates.extend(found);errors.extend([error] if error else [])
        if not any(u['section']=='acaContribution' for u in updates):errors.append('No supported ACA contribution table found in recent IRS bulletins; retain existing data and review discovery.')
    except Exception as e:errors.append(f'IRS discovery: {e}')
    checked=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    try:return merge_updates(manifest,updates,checked,errors,pending)
    except ReviewRequired as e:return merge_updates(manifest,[],checked,errors+[str(e)],pending)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,default=Path('tax-updates.json'));ap.add_argument('--output',type=Path);ap.add_argument('--strict',action='store_true');args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text());updated=run(manifest);out=args.output or args.manifest
    temporary=out.with_suffix(out.suffix+'.tmp');temporary.write_text(json.dumps(updated,indent=2,ensure_ascii=False)+'\n');temporary.replace(out)
    print(json.dumps(updated['acaMonitor'],indent=2))
    if args.strict and updated['acaMonitor']['errors']:raise SystemExit(2)
if __name__=='__main__':main()
