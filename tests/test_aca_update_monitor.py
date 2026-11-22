import copy,importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('aca_update_monitor',ROOT/'scripts/aca_update_monitor.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
TABLE=(ROOT/'tests/monitor-fixtures/irs-2027-table.html').read_text()
def response(year=2026,region='US',size=1,amount=15960):return {'status':200,'data':{'year':str(year),'state':region,'household_size':str(size),'income':str(amount)}}
def fpl_get(url):
    year,region,size=url.rsplit('/',3)[1:];size=int(size);base,increment={'us':(15960,5680),'ak':(19950,7100),'hi':(18360,6530)}[region]
    return json.dumps(response(int(year),region.upper(),size,base+(size-1)*increment))
class CollectorTests(unittest.TestCase):
    def test_live_hhs_income_format(self):self.assertEqual(a.parse_hhs(response(),2026,'US',1),15960)
    def test_documented_hhs_format(self):
        p=response();p['data']['poverty_threshold']=p['data'].pop('income');self.assertEqual(a.parse_hhs(p,2026,'US',1),15960)
    def test_future_year_default_is_not_new_data(self):
        with self.assertRaises(a.NotPublished):a.parse_hhs(response(),2027,'US',1)
    def test_wrong_year_forward_is_rejected(self):
        with self.assertRaises(a.ReviewRequired):a.parse_hhs(response(2027),2026,'US',1)
    def test_region_and_size_verified(self):
        for region,size in [('AK',1),('US',2)]:
            with self.subTest(region=region,size=size),self.assertRaises(a.ReviewRequired):a.parse_hhs(response(),2026,region,size)
    def test_invalid_response_and_conflicting_fields(self):
        for p in [{'status':500,'data':{}},response(amount=-1),response(amount=True),{'status':200,'data':dict(response()['data'],poverty_threshold='123')}]:
            with self.subTest(p=p),self.assertRaises((a.ReviewRequired,ValueError)):a.parse_hhs(p,2026,'US',1)
    def test_all_regions_and_sizes_checked_before_publish(self):
        seen=[]
        def get(url):seen.append(url);return fpl_get(url)
        u=a.collect_fpl(2026,get);self.assertEqual(len(seen),24);self.assertEqual(u['year'],2027);self.assertEqual(u['values']['acaPovertyGuidelineYear'],2026);self.assertEqual(u['values']['acaPovertyGuidelines']['HI'],[18360,6530]);a.validate_update(u)
    def test_nonuniform_fpl_table_requires_review(self):
        def get(url):
            p=json.loads(fpl_get(url))
            if url.endswith('/hi/8'):p['data']['income']='99999'
            return json.dumps(p)
        with self.assertRaises(a.ReviewRequired):a.collect_fpl(2026,get)
    def test_irs_rates_and_current_procedure(self):
        u=a.parse_irs(TABLE,'https://www.irs.gov/irb/2026-31_irb')[0];self.assertEqual(u['year'],2027);self.assertEqual(u['values']['acaContributionRates'][-1],[300,400,.1022,.1022]);self.assertEqual(u['source']['reference'],'Revenue Procedure 2026-26');self.assertEqual(u['source']['published'],'2026-07-27');a.validate_update(u)
    def test_irs_nested_spans_and_whitespace(self):
        raw=TABLE.replace('6.78%','<span>6.78%</span>').replace('Applicable Percentage','Applicable\n Percentage');self.assertEqual(a.parse_irs(raw,'https://www.irs.gov/irb/2026-31_irb')[0]['year'],2027)
    def test_changed_bands_or_eligibility_never_auto_publish(self):
        for raw in [TABLE.replace('not more than 400%','not more than 500%'),TABLE.replace('Less than 133%','Less than 138%'),TABLE.replace('10.22%','unknown')]:
            with self.subTest(raw=raw[-300:]),self.assertRaises(a.ReviewRequired):a.parse_irs(raw,'https://www.irs.gov/irb/2026-31_irb')
    def test_unrelated_table_not_mistaken_for_contribution_schedule(self):self.assertEqual(a.parse_irs('<table><tr><th>Income tax</th></tr><tr><td>10%</td></tr></table>','https://www.irs.gov/irb/2026-31_irb'),[])
    def test_missing_year_heading_rejected(self):
        with self.assertRaises(a.ReviewRequired):a.parse_irs(TABLE.replace('Applicable Percentage Table for 2027','Other table'),'https://www.irs.gov/irb/2026-31_irb')
    def test_discover_official_pdf_and_html_bulletin_links(self):
        raw='<a href="/pub/irs-irbs/irb26-31.pdf">IRS</a><a href="/irb/2025-32_IRB">IRS</a><a href="https://evil.example/irb/2026-99_IRB">No</a>'
        self.assertEqual(a.discover_irs(lambda url:raw,pages=1),['https://www.irs.gov/irb/2025-32_IRB','https://www.irs.gov/irb/2026-31_IRB'])
    def test_no_links_is_a_visible_failure(self):
        with self.assertRaises(a.ReviewRequired):a.discover_irs(lambda url:'<p>Unavailable</p>',pages=1)
    def test_merge_preserves_federal_and_prior_years(self):
        manifest={'schemaVersion':1,'updates':[{'id':'federal','year':2027,'section':'federal','values':{'fedStdBase':33200}}]};before=copy.deepcopy(manifest);u=a.collect_fpl(2026,fpl_get);out=a.merge_updates(manifest,[u],'2026-11-22T00:00:00Z');self.assertEqual(out['updates'][0],manifest['updates'][0]);self.assertEqual(manifest,before);self.assertEqual(out['acaMonitor']['latestGuidelineYear'],2026)
    def test_duplicate_same_values_idempotent(self):
        u=a.collect_fpl(2026,fpl_get);m={'schemaVersion':1,'updates':[u]};out=a.merge_updates(m,[u],'2026-11-22T00:00:00Z');self.assertEqual(out['updates'],m['updates'])
    def test_conflicting_tables_refuse_overwrite(self):
        u=a.collect_fpl(2026,fpl_get);v=copy.deepcopy(u);v['values']['acaPovertyGuidelines']['US'][0]+=100
        with self.assertRaises(a.ReviewRequired):a.merge_updates({'schemaVersion':1,'updates':[]},[u,v],'2026-11-22T00:00:00Z')
    def test_region_missing_or_guideline_year_wrong_rejected(self):
        for field,value in [('acaPovertyGuidelineYear',2027),('acaPovertyGuidelines',{'US':[15960,5680]})]:
            u=a.collect_fpl(2026,fpl_get);u['values'][field]=value
            with self.assertRaises(a.ReviewRequired):a.validate_update(u)
    def test_status_shows_fetch_failures_and_pending_years(self):
        out=a.merge_updates({'schemaVersion':1,'updates':[]},[],'2026-11-22T00:00:00Z',['HHS unavailable'],['2027 not released']);self.assertEqual(out['acaMonitor']['status'],'needs-review');self.assertEqual(out['acaMonitor']['pending'],['2027 not released'])
    def test_source_protocol_and_credentials_rejected(self):
        for url in ['http://aspe.hhs.gov/x','https://user:secret@aspe.hhs.gov/x','https://aspe.hhs.gov.evil.example/x']:
            u=a.collect_fpl(2026,fpl_get);u['source']['url']=url
            with self.subTest(url=url),self.assertRaises(a.ReviewRequired):a.validate_update(u)
if __name__=='__main__':unittest.main()
