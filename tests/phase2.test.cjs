const {test}=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {loadModel}=require('./model-harness.cjs');
const fixture=require('./fixtures/phase2-retired-baseline.json');
const m=loadModel(process.env.MODEL_FILE||path.join(__dirname,'..','index.html')),h=m.raw.health;
const plain=v=>JSON.parse(JSON.stringify(v)),near=(a,b,eps=.51)=>assert(Math.abs(a-b)<=eps,`${a} != ${b}`);
const period=(v={})=>Object.assign({id:'health-1',label:'Synthetic coverage',kind:'marketplace',start:'2026-01',end:'2026-12',premium:1000,benchmark:900,outOfPocket:100,inflation:0,members:['p1'],creditEligible:true},v);
function state(soy={},p={},v={}){return m.base(Object.assign({cash:100000,ptWages:31300,spending:20000},soy),Object.assign({by1:1986,familyHealth:Object.assign(plain(h.defaults()),{enabled:true,householdConfirmed:true,periods:[period()]},p)},v));}
const first=s=>m.run(s)[0];
for(const c of fixture.cases)test('Phase 2 exact retired regression: '+c.name,()=>{
  for(const mode of ['absent','off']){
    const s=plain(c.input);if(mode==='absent')delete s.familyHealth;else s.familyHealth={enabled:false,periods:[period()],foreignIncome:99999,dependentMagi:77777};
    assert.deepEqual(m.run(s),c.rows);assert.deepEqual(m.report().rows,c.reportRows);assert.deepEqual(plain(m.raw.setupVisibleSteps()),c.steps);
    const migrated=m.migrate(s);delete migrated.familyHealth;delete migrated.acaData;const old=plain(c.migrated);delete old.familyHealth;assert.deepEqual(migrated,old);
  }
});
test('default off, independent arrays, legacy JSON round trip and off UI',()=>{
  const a=h.defaults(),b=h.defaults();a.periods.push(period());assert.equal(b.periods.length,0);assert.equal(b.enabled,false);
  const s=m.migrate(fixture.cases[0].input);assert.equal(s.familyHealth.enabled,false);assert.deepEqual(m.migrate(plain(s)),s);
  m.run(s);const html=m.setup();assert(!html.includes('>Health &amp; ACA</button>'));assert(!html.includes('>Health & ACA</button>'));assert(html.includes('Optional pre-Medicare'));
});
test('coverage months are strict, inclusive, and never silently ongoing',()=>{
  for(const bad of ['2026-00','2026-13','2026-2','2026-01-01',''])assert.equal(h.month(bad),null);
  const s=state({}, {periods:[period({start:'2026-03',end:'2026-08'})]});const r=first(s);near(r.health.grossPremium,6000);near(r.health.outOfPocket,600);assert.equal(r.health.months[1].premium,0);assert.equal(r.health.months[7].premium,1000);assert.equal(r.health.months[8].premium,0);
});
test('published 2026/2027 contribution tables and interpolation boundaries',()=>{
  const f=15650;
  for(const [pct,rate] of [[100,.021],[132.999,.021],[133,.0314],[150,.0419],[175,.05395],[200,.066],[225,.0752],[250,.0844],[300,.0996],[400,.0996]])near(h.rate(f*pct/100,f,2026),rate,1e-9);
  assert.equal(h.rate(f-1,f,2026),null);assert.equal(h.rate(4*f+.01,f,2026),null);
  near(h.rate(15960*2,15960,2027),.0678,1e-9);near(h.rate(15960*4,15960,2027),.1022,1e-9);
});
test('ACA uses prior-year FPL with separate Alaska and Hawaii values',()=>{
  for(const [yr,region,size,expected] of [[2026,'US',4,32150],[2026,'AK',2,26430],[2026,'HI',2,24310],[2027,'US',4,33000],[2027,'AK',2,27050],[2027,'HI',2,24890]]){
    const s=state({}, {region,householdSize:size});near(h.config(s,yr,'SINGLE').fpl,expected,1e-8);
  }
});
test('future rules are disclosed projections and projected FPL growth is explicit',()=>{
  const cfg=plain(h.config(state({}, {householdSize:1,fplGrowth:3}),2029,'SINGLE'));near(cfg.fpl,15960*1.03**2,1e-8);assert.equal(cfg.projected,true);assert.equal(cfg.ruleYear,2027);
  const r=first(state({}, {periods:[period({start:'2029-01',end:'2029-12'})]},{startYear:2029,endYear:2029,soy:{2029:{cash:100000,ptWages:40000}}}));assert(r.health.issues.some(x=>/Projection assumption/.test(x)));
});
test('MAGI adds exempt interest, nontaxable SS, foreign and required-filer dependent income once',()=>{
  near(h.magi(20000,3000,24000,6000,{foreign:4000,dependent:2000}),47000,1e-8);
  near(h.magi(-1000,200,0,0,{foreign:1000,dependent:0}),200,1e-8);
  near(h.magi(20000,3000,24000,6000,{foreign:4000,dependent:2000,override:0}),0,1e-8);
});
test('ACA and Medicare MAGI differ while the original Medicare lookback remains exact',()=>{
  const s=state({ptWages:0,ira1:200000},{foreignIncome:4000,dependentMagi:2000,periods:[]},{by1:1962,ssAge1:62,ssmo1:2000,endYear:2029,medicareMagi2:123456,medicareMagi1:234567});
  const rows=m.run(s);for(const r of rows){near(r.acaMagi,r.projectedMagi+r.grossSS-r.taxableSS+6000,1e-8);assert.equal(r.irmaaLookbackYear,r.yr-2);}
  near(rows[0].irmaaMagi,123456);near(rows[1].irmaaMagi,234567);near(rows[2].irmaaMagi,rows[0].magi);
});
test('basis returned from brokerage creates no ACA income; realized gains do',()=>{
  for(const pct of [0,.5]){const r=first(state({cash:0,ptWages:0,sec:100000},{periods:[period({creditEligible:false})]},{stkGainPct:pct}));near(r.acaMagi,r.stkSales*pct,1e-8);}
});
test('muni interest and reinvested taxable dividends enter ACA income',()=>{
  const r=first(state({cash:10000,ptWages:0,secTaxableBal:50000,secCAMuniBal:50000},{periods:[]},{divRate:.04,divReinvestPct:1}));
  near(r.acaMagi,r.agi+r.taxExemptInterest,1e-8);assert(r.taxExemptInterest>0);assert(r.fedTaxableDivInt>0);
});
test('existing qualified Roth and HSA withdrawal assumptions do not create ACA income',()=>{
  const r=first(state({cash:0,ptWages:0,roth1:100000,hsa:10000,hsaWith:5000},{periods:[period({creditEligible:false})]},{fundingOrder1:'ROTH'}));near(r.acaMagi,0);assert(r.rothDraw1>0);near(r.hsaWith,5000);
});
test('payroll deductions reduce ACA MAGI through modeled AGI without a second deduction',()=>{
  const r=first(state({grossWages:60000,ptWages:0,preTaxDed1:6000},{periods:[]},{k401Trad1:.1}));near(r.acaMagi,48000);
});
test('annual credit is sum of monthly lesser-of amounts and is not income tax reduction',()=>{
  const r=first(state());near(r.health.credit,10800-31300*.066,1e-8);near(r.health.netCost,12000-r.health.credit+1200,1e-8);
  near(r.spending,20000+r.health.netCost,.5);near(r.totalRequired,r.spending+r.fundingTax+r.hsaDep+r.cashGapNeeded,1e-8);
  const noHealth=state();noHealth.familyHealth.enabled=false;near(r.incomeTax,first(noHealth).incomeTax,1e-8);
});
test('premium credit cannot exceed eligible premiums and medical spending receives no credit',()=>{
  const r=first(state({}, {periods:[period({premium:100,benchmark:2000,outOfPocket:400})]}));near(r.health.credit,1200);near(r.health.netCost,4800);near(r.health.netPremium,0);
});
test('multiple Marketplace policies share one contribution per month',()=>{
  const s=state({}, {householdSize:2,periods:[period({premium:700,benchmark:600}),period({id:'health-2',premium:700,benchmark:600,members:['p2']})]},{householdMode:'couple',name2:'Synthetic Spouse',by2:1988,filing:'MFJ'});
  const r=first(s),rate=h.rate(31300,21150,2026);near(r.health.credit,14400-31300*rate,1e-8);
});
test('COBRA, employer, public, and private coverage do not receive Marketplace credits',()=>{
  for(const kind of ['cobra','employer','public','private']){const r=first(state({}, {periods:[period({kind})]}));near(r.health.credit,0);near(r.healthSpending,13200);}
});
test('missing confirmations, unknown members, and missing benchmark withhold assistance',()=>{
  for(const p of [{householdConfirmed:false},{periods:[period({creditEligible:false})]},{periods:[period({members:[]})]},{periods:[period({benchmark:''})]},{householdSource:'manual',householdSize:''}]){
    const r=first(state({},p));near(r.health.credit,0);near(r.healthSpending,13200);assert(r.health.issues.length>0);
  }
});
test('overlapping coverage of the same person warns and withholds assistance for that month',()=>{
  const r=first(state({}, {periods:[period(),period({id:'health-2',start:'2026-06',end:'2026-06'})]}));near(r.health.months[5].credit,0);assert(r.health.issues.some(x=>/overlapping/.test(x)));
});
test('family timeline provides tax dependents independent of support and coverage',()=>{
  const dependent={id:'child',name:'Synthetic Child',birthDate:'2010-06-15',periods:{taxDependent:[{start:'2026',end:'2026'}],support:[{start:'2026-01-01',end:'2035-12-31'}]}};
  const s=state({}, {},{familyTimeline:{enabled:true,dependents:[dependent]}});assert.equal(h.config(s,2026,'SINGLE').size,2);assert.equal(h.config(s,2027,'SINGLE').size,1);
  s.familyTimeline.dependents[0].periods.taxDependent=[];assert.equal(h.config(s,2026,'SINGLE').valid,false);
  s.familyHealth.years={2026:{householdSize:2}};assert.equal(h.config(s,2026,'SINGLE').valid,true);
});
test('year overrides do not leak to other years, and ACA override does not replace Medicare MAGI',()=>{
  const s=state({}, {years:{2026:{householdSize:3,foreignIncome:0,dependentMagi:1000,magiOverride:40000}}},{endYear:2027});
  const rows=m.run(s);near(rows[0].acaMagi,40000);assert.notEqual(rows[0].magi,40000);assert.equal(rows[0].health.householdSize,3);assert.equal(rows[1].health.householdSize,1);assert.equal(rows[1].health.override,null);
});
test('mixed Medicare and Marketplace couple counts both tax-family members, only eligible spouse in quote',()=>{
  const r=first(state({}, {periods:[period({members:['p2']})]},{householdMode:'couple',name2:'Synthetic Spouse',by1:1950,by2:1970,filing:'MFJ'}));
  assert.equal(r.health.householdSize,2);assert(r.medicareBase>0);assert(r.health.credit>0);assert(!r.health.issues.some(x=>/Medicare timing/.test(x)));
});
test('exact birthday and first-of-month rule block credits at Medicare timing without changing Medicare engine',()=>{
  for(const [date,lastCreditMonth] of [['1961-06-15',5],['1961-06-01',4]]){
    const s=state({}, {},{by1:1961,familyTimeline:{enabled:false,birthDate1:date}}),r=first(s);
    assert(r.health.months[lastCreditMonth-1].credit>0);near(r.health.months[lastCreditMonth].credit,0);near(r.health.grossPremium,12000);
    near(r.medicareBase,0);assert(r.health.issues.some(x=>/Medicare timing/.test(x)));
  }
});
test('coverage timing, repricing and quote growth do not change ordinary spending inflation anchors',()=>{
  const s=state({}, {periods:[period({end:'2027-12',kind:'cobra',inflation:10})]},{endYear:2028,spendInfl:.03});const rows=m.run(s);
  near(rows[0].householdSpending,20000);near(rows[1].householdSpending,20600);near(rows[2].householdSpending,21218);
  near(rows[1].healthSpending,14520);near(rows[2].healthSpending,0);
});
test('IRA-funded premiums settle jointly with income tax and reduced ACA assistance',()=>{
  const s=state({cash:0,ptWages:0,ira1:500000,spending:30000},{},{fundingOrder1:'IRA'}),r=first(s);
  assert(r.taxSolverConverged);near(r.acaMagi,r.ira1Addl);assert(r.health.credit>0);near(r.spending,30000+r.health.netCost);near(r.netWorth,500000-r.spending-r.fundingTax);
  const cash=first(state({ptWages:30000,spending:30000}));assert(r.acaMagi>cash.acaMagi);assert(r.health.credit<cash.health.credit);
});
for(const method of ['NORMAL','OUTSIDE','IRA','WITHHOLD'])test('health funding conserves cash with conversion tax method '+method,()=>{
  const s=state({cash:30000,sec:100000,ira1:500000,ptWages:0},{},{rothConvTaxFunding:method,cashFloor:10000,ovIncomeLevel:[{magiTarget:50000,startYear:2026,endYear:2026}]}),r=first(s);
  assert(r.taxSolverConverged);assert(r.rothConv>0);near(r.netWorth,630000-r.spending-r.fundingTax-r.rothConvTaxWithheld);near(r.healthSpending,r.health.netCost);
});
test('ACA Income Level conversion target uses ACA household addbacks only when enabled',()=>{
  const s=state({ptWages:20000,ira1:500000},{foreignIncome:5000,dependentMagi:2000,periods:[]},{ovIncomeLevel:[{magiTarget:50000,startYear:2026,endYear:2026}]}),r=first(s);
  near(r.acaMagi,50000,10);near(r.projectedMagi,43000,10);
  s.familyHealth.enabled=false;near(first(s).magi,50000,10);
});
test('manual tax override still iterates the insurance funding feedback',()=>{
  const r=first(state({cash:0,ptWages:0,ira1:500000,spending:30000},{},{ovSpending:[{taxOvr:2000,startYear:2026,endYear:2026}]}));assert(r.taxSolverConverged);near(r.fundingTax,2000);near(r.healthSpending,r.health.netCost);near(r.netWorth,500000-r.spending-2000);
});
test('insufficient assets produce an explicit unfunded health/spending gap',()=>{
  const r=first(state({cash:1000,ptWages:0,spending:0},{periods:[period({kind:'cobra',outOfPocket:0})]}));near(r.unfunded,11000);near(r.netWorth,0);near(r.healthSpending,12000);
});
test('future schemas are retained, safely disabled, and do not crash projections',()=>{
  const s=state({}, {schemaVersion:7,periods:[],years:undefined,newField:{keep:1}}),r=first(s);near(r.healthSpending,0);assert(r.health.issues.some(x=>/Unsupported/.test(x)));
  const migrated=m.migrate(s);assert.equal(migrated.familyHealth.schemaVersion,7);assert.deepEqual(migrated.familyHealth.newField,{keep:1});
});
test('enabled health report payload, cash-flow and printable report include one clear breakdown',()=>{
  const r=first(state());const report=m.report().rows[0];assert.deepEqual(report.health,r.health);near(report.healthSpending,r.healthSpending);
  const html=m.print();assert(html.includes('Optional pre-Medicare health insurance'));assert(html.includes('not deducted again'));
  const nodes=m.render();assert(nodes.get('cf-accounting-warnings').innerHTML.includes('ACA MAGI'));
});
test('health UI escapes imported names, identifiers, and labels',()=>{
  m.run(state({}, {periods:[period({id:'x\" onclick=\"alert(1)',label:'<img src=x onerror=alert(1)>'})]}));
  const html=m.setup('health');assert(html.includes('&lt;img'));assert(!html.includes('<img src=x'));assert(!html.includes('id="health-x" onclick='));assert(html.includes('Health &amp; ACA')||html.includes('Health & ACA'));
});
test('a covered child outside the derived tax dependency period receives no credit',()=>{
  const s=state({}, {periods:[period({members:['child']})]},{familyTimeline:{enabled:true,dependents:[{id:'child',name:'Synthetic Child',birthDate:'2010-01-01',periods:{taxDependent:[{start:'2020',end:'2025'}]}}]}});
  const r=first(s);near(r.health.credit,0);assert(r.health.issues.some(x=>/outside the derived tax family/.test(x)));
});
test('an unmarried partner is not automatically a second tax-family member',()=>{
  const s=state({}, {periods:[period({members:['p2']})]},{householdMode:'couple',name2:'Synthetic Partner',by2:1988,filing:'SINGLE'});
  const r=first(s);assert.equal(r.health.householdSize,1);near(r.health.credit,0);assert(r.health.issues.some(x=>/outside the derived tax family/.test(x)));
});
test('coverage-family count cannot exceed a manual tax-family count',()=>{
  const r=first(state({}, {householdSize:1,periods:[period({members:['p1','p2']})]},{householdMode:'couple',name2:'Synthetic Spouse',by2:1988,filing:'MFJ'}));near(r.health.credit,0);assert(r.health.issues.some(x=>/exceed the tax household/.test(x)));
});
test('invalid quoted costs flag incomplete calculations instead of claiming a funded plan',()=>{
  for(const p of [period({premium:-100}),period({end:''}),period({start:'2026-13'}),period({inflation:100})]){
    const r=first(state({}, {periods:[p]}));assert(r.health.inputErrors.length);assert(m.raw.projectionAccountingWarningsHtml([r]).includes('costs were omitted'));
    assert(m.raw.apCard(2026).includes('Review Calculation'));
    assert.throws(()=>m.raw.riskPathMetrics(m.run(state({}, {periods:[p]})),[1],{stock:[0],bond:[0],infl:[0]}),/incomplete inputs/);
  }
});
test('Risk Lab reprojects health once from the ordinary household spending base',()=>{
  const s=state({}, {periods:[period({end:'2027-12'})]},{endYear:2027});const original=m.run(s);
  const path={stock:[0,0],bond:[0,0],infl:[0,0]},settings={endYear:2027,stockPct:60,spendAdj:0};
  const scenario=m.raw.riskScenarioState(settings,path,true,original);const rows=m.run(plain(scenario.state));
  for(let i=0;i<rows.length;i++){near(rows[i].spending,original[i].spending,1e-8);near(rows[i].healthSpending,original[i].healthSpending,1e-8);near(rows[i].netWorth,original[i].netWorth,1e-8);}
});
test('fixed ACA income override never causes conversion targets to fill the entire IRA',()=>{
  const r=first(state({ptWages:20000,ira1:500000},{foreignIncome:5000,years:{2026:{magiOverride:40000}}},{ovIncomeLevel:[{magiTarget:50000,startYear:2026,endYear:2026}]}));
  near(r.rothConv,25000,10);near(r.acaMagi,40000);assert(r.taxSolverConverged);assert(r.health.issues.some(x=>/override is fixed/.test(x)));
});
test('disabling health restores projection outputs exactly and retains saved entries',()=>{
  const s=state(),base=plain(s);base.familyHealth.enabled=false;const before=m.run(base);
  const migrated=m.migrate(s);migrated.familyHealth.enabled=false;assert.deepEqual(m.run(migrated),before);
  assert.equal(migrated.familyHealth.periods[0].premium,1000);
});
test('synthetic mixed health and conversion cases conserve assets over multiple years',t=>{
  let seed=20261122,checked=0;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<60;i++){
    const s=state({cash:10000,sec:100000,ira1:500000,roth1:50000,ptWages:10000+rnd()*80000,spending:30000+rnd()*30000},
      {periods:[period({end:'2029-12',premium:600+rnd()*1000,benchmark:600+rnd()*1000,inflation:3})]},
      {endYear:2029,cashFloor:i%2?10000:0,stkGainPct:rnd(),growthRate:-.2+rnd()*.3,rothConvTaxFunding:['NORMAL','OUTSIDE','IRA','WITHHOLD'][i%4],...(i%3?{ovIncomeLevel:[{magiTarget:40000+rnd()*40000,startYear:2026,endYear:2029}]}:{})});
    const rows=m.run(s);
    for(const r of rows){assert(r.taxSolverConverged,`case ${i} ${r.yr}, residual ${r.taxSolverResidual}`);assert(Number.isFinite(r.health.netCost));assert(r.health.credit>=0&&r.health.credit<=r.health.grossPremium);near(r.healthSpending,r.health.netCost);
      if(r.unfunded>.5)continue;
      const opening=r.startCashBal+r.startSec+r.startIRA1+r.startRoth1;
      near(r.netWorth,opening+r.secGrowth+r.ira1Growth+r.roth1Growth+r.atWages+r.ptWages+r.divs-r.spending-r.fundingTax-r.rothConvTaxWithheld,1.01);checked++;
    }
  }
  t.diagnostic(`${checked} funded health-insurance years reconciled across 60 four-year scenarios.`);
});
test('a subsidy-boundary cycle falls back to full premiums, zero used credit, and review status',()=>{
  const s=require('./fixtures/aca-boundary-case.json'),rows=m.run(s),r=rows.find(x=>x.yr===2028);
  assert(r.taxSolverConverged);assert.equal(r.health.assistanceSuppressed,true);near(r.health.credit,0);near(r.healthSpending,r.health.grossPremium+r.health.outOfPocket);assert(r.health.potentialCredit>0);
  assert(r.health.issues.some(x=>/conservative fallback/.test(x)));assert(m.raw.apCard(2028).includes('Review Calculation'));
});
test('conversion withholding keeps Normal Funding gross conversion with optional insurance',()=>{
  const s=state({ptWages:0,ira1:500000},{},{ovIncomeLevel:[{magiTarget:50000,startYear:2026,endYear:2026}]});
  const normal=first(s);s.rothConvTaxFunding='WITHHOLD';const withheld=first(s);
  near(withheld.rothConv,normal.rothConv,1e-8);near(withheld.rothConvNet+withheld.rothConvTaxWithheld,withheld.rothConv,1e-8);
});
test('subsidy cutoffs are tested on annual income despite six-month coverage',()=>{
  for(const [income,hasCredit] of [[15649,false],[15650,true],[62600,true],[62600.01,false]]){
    const r=first(state({ptWages:income},{periods:[period({start:'2026-07',end:'2026-12'})]}));
    assert.equal(r.health.credit>0,hasCredit,String(income));near(r.health.grossPremium,6000);
  }
});
test('finalized Medicare MAGI remains a lookback value, not an ACA income input',()=>{
  const r=first(state({}, {},{yearEndCloseouts:{2026:{status:'final',agi:99999,magi:88888}}}));
  near(r.acaMagi,31300);near(r.magi,88888);near(r.health.agi,r.projectedAgi);
});
