const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {loadModel}=require('./model-harness.cjs'),m=loadModel(process.env.MODEL_FILE||path.join(__dirname,'..','index.html')),a=m.raw.aca;
const plain=v=>JSON.parse(JSON.stringify(v)),near=(x,y)=>assert(Math.abs(x-y)<1e-8,`${x} != ${y}`);
const rates=()=>({id:'synthetic-rates-2028',section:'acaContribution',year:2028,source:{agency:'IRS',url:'https://www.irs.gov/irb/2027-31_IRB'},values:{acaContributionRates:[[100,133,.022,.022],[133,150,.033,.044],[150,200,.044,.068],[200,250,.068,.087],[250,300,.087,.103],[300,400,.103,.103]],acaMinimumFpl:100,acaMaximumFpl:400}});
const fpl=()=>({id:'synthetic-fpl-2028',section:'acaPoverty',year:2028,source:{agency:'HHS',url:'https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines/api/2027/us/1'},values:{acaPovertyGuidelineYear:2027,acaPovertyGuidelines:{US:[17000,6000],AK:[21000,7500],HI:[19000,6900]}}});
function health(){return m.base({cash:100000,ptWages:50000,spending:30000},{by1:1986,startYear:2026,endYear:2030,familyHealth:{schemaVersion:1,enabled:true,householdConfirmed:true,householdSize:2,foreignIncome:0,dependentMagi:0,fplGrowth:2.5,periods:[{id:'h',kind:'marketplace',label:'Synthetic quote',start:'2026-01',end:'2030-12',premium:1000,benchmark:900,outOfPocket:100,inflation:0,members:['p1'],creditEligible:true}]}});}
test('ACA data defaults auto-on with independent storage and health option off',()=>{const x=a.defaults(),y=a.defaults();assert.equal(x.autoApply,true);x.years[2028]={};assert.deepEqual(plain(y.years),{});assert.equal(m.base().familyHealth.enabled,false);});
test('legacy migration adds automatic ACA data without changing financial inputs',()=>{const s=health(),original=m.run(s);delete s.acaData;const migrated=m.migrate(s);assert.equal(migrated.acaData.autoApply,true);assert.deepEqual(m.run(migrated),original);});
test('official built-in 2026/2027 sections match published baseline values',()=>{for(const year of [2026,2027]){const p=plain(a.policy(m.base(),year));assert.equal(p.contribution.status,'official');assert.equal(p.poverty.status,'official');assert.equal(p.poverty.values.acaPovertyGuidelineYear,year-1);}});
test('client validates contribution and poverty sections independently',()=>{assert.deepEqual(plain(a.validate(rates())),[]);assert.deepEqual(plain(a.validate(fpl())),[]);});
test('future FPL API default to old year cannot pass client validation',()=>{const u=fpl();u.values.acaPovertyGuidelineYear=2026;assert(a.validate(u).some(x=>/Guideline year/.test(x)));});
test('missing regions, invalid numbers, missing fields and unknown keys are rejected',()=>{
 for(const mutate of [u=>delete u.values.acaPovertyGuidelines.HI,u=>u.values.acaPovertyGuidelines.US[0]=-1,u=>u.values.acaPovertyGuidelines.US[0]='17000',u=>u.values.bad=123,u=>u.values.acaPovertyGuidelines.XY=[1,2]]){const u=fpl();mutate(u);assert(a.validate(u).length);}
});
test('unexpected subsidy cliff or band structure requires an app rule review',()=>{
 for(const mutate of [u=>u.values.acaMaximumFpl=500,u=>u.values.acaContributionRates[0][0]=0,u=>u.values.acaContributionRates.pop(),u=>u.values.acaContributionRates[5][3]=Infinity,u=>u.values.acaContributionRates[3][2]=true]){const u=rates();mutate(u);assert(a.validate(u).length);}
});
test('untrusted source protocols and lookalike domains are rejected',()=>{
 for(const url of ['javascript:alert(1)','http://www.irs.gov/x','https://www.irs.gov.evil.test/x','https://user:password@www.irs.gov/x']){const u=rates();u.source.url=url;assert(a.validate(u).length);}
});
test('auto apply changes only the exact ACA sections and preserves Medicare tables',()=>{
 const s=health(),before=JSON.stringify(s.taxTables),family=JSON.stringify(s.familyHealth),prior=JSON.stringify(s.acaData);
 const result=plain(a.apply(s,[rates(),fpl()],true));assert.equal(result.applied.length,2);assert.equal(JSON.stringify(s.taxTables),before);assert.equal(JSON.stringify(s.familyHealth),family);assert.notEqual(JSON.stringify(s.acaData),prior);
 const p=plain(a.policy(s,2028));assert.equal(p.contribution.year,2028);assert.equal(p.poverty.year,2028);assert.equal(p.contribution.status,'official');assert.equal(p.poverty.status,'official');
});
test('auto-update opt-out preserves figures until a manual apply',()=>{const s=health();s.acaData.autoApply=false;assert.equal(a.apply(s,[rates()],true).applied.length,0);assert.equal(a.policy(s,2028).contribution.year,2027);assert.equal(a.apply(s,[rates()],false).applied.length,1);});
test('manually entered and pinned data are protected from automatic replacement',()=>{
 for(const mode of ['entered','pinned']){const s=health();a.apply(s,[rates()],false);const saved=s.acaData.years[2028].acaContribution;if(mode==='entered')saved.status='entered';else saved.pinned=true;saved.values.acaContributionRates[0][2]=.01;
 const before=JSON.stringify(saved);const r=a.apply(s,[rates()],true);assert.equal(r.skipped.length,1);assert.equal(JSON.stringify(s.acaData.years[2028].acaContribution),before);a.apply(s,[rates()],false);near(s.acaData.years[2028].acaContribution.values.acaContributionRates[0][2],.022);}
});
test('conflicting records for one section/year retain the previous figures',()=>{const s=health(),x=rates(),y=rates();y.id='conflict';y.values.acaContributionRates[0][2]=.01;const r=a.apply(s,[x,y],true);assert(r.errors.length);assert.equal(a.policy(s,2028).contribution.year,2027);});
test('applying an official update twice is idempotent',()=>{const s=health();assert.equal(a.apply(s,[rates()],true).applied.length,1);assert.equal(a.apply(s,[rates()],true).applied.length,0);assert.equal(a.current(rates(),s),true);});
test('FPL and contribution schedules can arrive separately without false Official status',()=>{
 const s=health();a.apply(s,[fpl()],true);let cfg=plain(m.raw.health.config(s,2028,'SINGLE'));near(cfg.fpl,23000);assert.equal(cfg.ruleYear,2027);assert.equal(cfg.contributionStatus,'projected');assert.equal(cfg.povertyStatus,'official');assert.equal(cfg.projected,true);
 a.apply(s,[rates()],true);cfg=plain(m.raw.health.config(s,2028,'SINGLE'));assert.equal(cfg.ruleYear,2028);assert.equal(cfg.projected,false);
});
test('a new rate table can arrive before its FPL figures',()=>{const s=health();a.apply(s,[rates()],true);const cfg=m.raw.health.config(s,2028,'SINGLE');assert.equal(cfg.contributionStatus,'official');assert.equal(cfg.povertyStatus,'projected');assert.equal(cfg.projected,true);near(cfg.fpl,21640*1.025);});
test('later years inflate the latest received poverty table and retain the latest rate year',()=>{const s=health();a.apply(s,[rates(),fpl()],true);const cfg=m.raw.health.config(s,2030,'SINGLE');near(cfg.fpl,23000*1.025**2);assert.equal(cfg.ruleYear,2028);assert.equal(cfg.projected,true);});
test('future ACA records never change earlier coverage years',()=>{const s=health(),prior=m.run(s).filter(x=>x.yr<2028);a.apply(s,[rates(),fpl()],true);assert.deepEqual(m.run(s).filter(x=>x.yr<2028),prior);});
test('new published figures are actually used to recalculate assistance',()=>{const s=health(),old=m.run(s).find(x=>x.yr===2028);a.apply(s,[rates(),fpl()],true);const r=m.run(s).find(x=>x.yr===2028);assert.equal(r.health.ruleYear,2028);assert.equal(r.health.guidelineYear,2027);assert.notEqual(r.health.credit,old.health.credit);assert.equal(r.health.projected,false);assert(r.taxSolverConverged);});
test('retired financial projection remains exact with automatic ACA updates installed but health off',()=>{const s=health();s.familyHealth.enabled=false;const before=m.run(s);a.apply(s,[rates(),fpl()],true);assert.deepEqual(m.run(s),before);});
test('ACA data survives JSON export/import with per-year source metadata intact',()=>{const s=health();a.apply(s,[rates(),fpl()],true);const t=m.migrate(plain(s));assert.deepEqual(t.acaData,plain(s.acaData));assert.deepEqual(m.run(t),m.run(s));});
test('unsupported saved schema retained without editing or pretending it was applied',()=>{const s=health();s.acaData={schemaVersion:7,autoApply:true,newField:{keep:1},years:{}};assert(a.apply(s,[rates()],true).errors.length);assert.deepEqual(s.acaData.newField,{keep:1});assert.equal(a.policy(s,2028).contribution.year,2027);});
test('missing, stale and failed source monitor statuses are visible while data is retained',()=>{const s=health();assert(a.monitor(s).warning);s.acaData.monitor={checkedAt:new Date().toISOString(),errors:[]};assert.equal(a.monitor(s).warning,false);s.acaData.monitor.errors=['IRS unavailable'];assert(a.monitor(s).warning);s.acaData.monitor={checkedAt:'2020-01-01',errors:[]};assert(a.monitor(s).text.includes('overdue'));});
test('tax updater recognizes both ACA sections without adding their fields to tax tables',()=>{assert.deepEqual(plain(a.taxAllowed('acaContribution')),['acaContributionRates','acaMinimumFpl','acaMaximumFpl']);assert.deepEqual(plain(a.taxAllowed('acaPoverty')),['acaPovertyGuidelineYear','acaPovertyGuidelines']);});
test('every ACA record in the published manifest passes the app validator',()=>{const manifest=require('../tax-updates.json');assert.equal(manifest.schemaVersion,1);const records=manifest.updates.filter(u=>['acaContribution','acaPoverty'].includes(u.section));assert(records.length>=4);for(const u of records)assert.deepEqual(plain(a.validate(u)),[],u.id);});
test('routine source checks do not dirty or upload an unchanged retirement plan',()=>{
 const fresh=loadModel(process.env.MODEL_FILE||path.join(__dirname,'..','index.html'));fresh.run(fresh.base());let saves=0;fresh.context.saveState=()=>{saves++;};fresh.context.acaRenderPanel=()=>{};
 fresh.raw.aca.accept({schemaVersion:1,updates:[],acaMonitor:{checkedAt:new Date().toISOString(),errors:[]}});assert.equal(saves,0);assert(fresh.raw.getState().acaData.monitor.checkedAt);
});
test('automatic application saves changed ACA figures once while preserving tax tables',()=>{
 const fresh=loadModel(process.env.MODEL_FILE||path.join(__dirname,'..','index.html'));fresh.run(fresh.base());const tables=JSON.stringify(fresh.raw.getState().taxTables);let saves=0;fresh.context.saveState=()=>{saves++;};fresh.context.renderAll=()=>{};fresh.context.showSaved=()=>{};fresh.context.acaRenderPanel=()=>{};
 fresh.raw.aca.accept({schemaVersion:1,updates:[rates(),fpl()],acaMonitor:{checkedAt:new Date().toISOString(),errors:[]}});assert.equal(saves,1);assert.equal(JSON.stringify(fresh.raw.getState().taxTables),tables);
});
test('a slow initial private-plan load retains the loaded automatic-update preference',async()=>{
 const fresh=loadModel(process.env.MODEL_FILE||path.join(__dirname,'..','index.html'));fresh.run(fresh.base());let finish;const gate=new Promise(resolve=>{finish=resolve;});const remote=fresh.base();remote.acaData.autoApply=false;
 fresh.context.ghIsConfigured=()=>true;fresh.context.initGitHubLoad=async()=>{await gate;fresh.raw.setState(remote);};fresh.context.acaRenderPanel=()=>{};
 const loading=fresh.raw.aca.startLoad();fresh.raw.aca.accept({schemaVersion:1,updates:[rates(),fpl()],acaMonitor:{checkedAt:new Date().toISOString(),errors:[]}});assert(!fresh.raw.getState().acaData.years[2028]);finish();await loading;
 assert.equal(fresh.raw.getState().acaData.autoApply,false);assert(!fresh.raw.getState().acaData.years[2028]);assert(fresh.raw.getState().acaData.monitor.checkedAt);
});
