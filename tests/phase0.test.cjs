const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {loadModel}=require('./model-harness.cjs');
const {select}=require('./cases.cjs');
const fixture=require('./fixtures/retired-baseline.json');
const m=loadModel(process.env.MODEL_FILE || path.join(__dirname,'..','index.html'));
const near=(a,b,msg='',eps=.51)=>assert(Math.abs(a-b)<=eps,`${msg}: expected ${b}, got ${a}`);
const first=s=>m.run(s)[0];

for(const c of fixture.cases)test(`retired baseline: ${c.name}`,()=>{
  // Conversion withholding can differ within the existing $0.50 solver
  // tolerance after correcting signed settlement; every other fixture is exact
  // apart from floating point representation.
  const tolerance=c.name==='conversion-WITHHOLD'?.51:1e-8;
  const rows=m.run(c.input).map(select), reports=m.report().rows.map(select);
  for(const [actual,expected] of [[rows,c.expected],[reports,c.reportRows]]){
    assert.equal(actual.length,expected.length);
    expected.forEach((row,i)=>Object.entries(row).forEach(([k,v])=>{
      if(typeof v==='number')near(actual[i][k],v,`${c.name} row ${i} ${k}`,tolerance);
      else assert.deepEqual(actual[i][k],v);
    }));
  }
});

test('surplus is deposited once with zero, positive, or changing cash floors',()=>{
  for(const cashFloor of [0,5000,15000]){
    const r=first(m.base({ptWages:10000},{cashFloor}));
    near(r.netWorth,10000); near(r.endCash,Math.min(cashFloor,10000));
    near(r.sec,Math.max(0,10000-cashFloor));
    near(r.unfunded,Math.max(0,cashFloor-10000));
  }
  const rows=m.run(m.base({cash:10000,ptWages:10000},{cashFloor:5000,endYear:2028,ovCashFloor:[{floor:0,startYear:2027,endYear:2027}]}));
  near(rows[2].netWorth,40000);
});
test('retired Social Security and RMD surplus is saved once',()=>{
  const r=first(m.base({ira1:300000},{by1:1950,rmdStart1:2024,ssAge1:67,ssmo1:2000}));
  near(r.netWorth,300000+r.grossSS-r.fundingTax); near(r.endCash,0);
});
test('cash-funded HSA deposit transfers assets and increases required funding',()=>{
  const r=first(m.base({cash:10000,hsaDep:5000}));
  near(r.netWorth,10000); near(r.hsa,5000); near(r.endCash,5000);
  near(r.totalRequired,5000); near(r.cashDraw,5000);
});
test('HSA strategy deposit is funded through the selected account order',()=>{
  const r=first(m.base({sec:20000},{ovHSADeposit:[{amount:3000,startYear:2026,endYear:2026}],stkGainPct:0}));
  near(r.stkSales,3000); near(r.hsa,3000); near(r.netWorth,20000);
});
test('unfunded HSA deposit cannot create assets',()=>{
  const r=first(m.base({hsaDep:5000}));
  near(r.hsa,0); near(r.netWorth,0); near(r.unfunded,5000);
  near(r.hsaDepositFunded,0); near(r.hsaDepositShortfall,5000);
});
test('partially funded HSA deposit cannot create assets or hide shortfall',()=>{
  const r=first(m.base({cash:3000,hsaDep:5000}));
  near(r.hsa,3000); near(r.netWorth,3000); near(r.unfunded,2000);
  near(r.hsaDepositFunded,3000);
});
test('HSA deposit and reimbursement conserve assets together',()=>{
  const r=first(m.base({cash:10000,hsa:20000,hsaDep:3000,hsaWith:7000,spending:5000}));
  near(r.netWorth,25000); near(r.hsa,16000); near(r.unfunded,0);
});
test('HSA withdrawal using same-year deposit cannot manufacture money in a deficit',()=>{
  const r=first(m.base({hsa:1000,hsaDep:5000,hsaWith:6000,spending:10000}));
  near(r.netWorth,0); near(r.unfunded,9000); near(r.hsaDepositFunded,5000);
});
test('pre-tax payroll deductions reduce take-home and AGI once',()=>{
  const r=first(m.base({grossWages:100000,preTaxDed1:10000},{cashFloor:10000}));
  near(r.w2AGI,90000);
  const payroll=90000*.0765;
  near(r.netWorth,100000-10000-payroll-r.incomeTax);
  near(r.atWages,100000-10000-payroll-r.incomeTax);
});
test('payroll deductions carry forward and explicit zero stops them',()=>{
  const rows=m.run(m.base({}, {cashFloor:10000,endYear:2028,soy:{2026:{grossWages:100000,preTaxDed1:10000},2028:{preTaxDed1:0}}}));
  near(rows[1].w2AGI,90000); near(rows[2].w2AGI,100000);
});
test('explicit withholding and 401k contributions conserve earnings',()=>{
  const r=first(m.base({grossWages:100000,preTaxDed1:10000,withholdPct:25},{cashFloor:10000,k401Trad1:.1,k401Roth1:.05,k401Emp1:.03}));
  near(r.w2AGI,80000); near(r.atWages,50000);
  near(r.netWorth,100000-10000-90000*.0765-r.incomeTax+3000);
});
test('survivor stops deceased wages, other income and employer contributions in either direction',()=>{
  for(const widowMode of ['p1Survives','p2Survives']){
    const rows=m.run(m.base({}, {name2:'Synthetic Spouse',householdMode:'couple',filing:'MFJ',by2:1957,widowMode,widowDeathYear:2026,endYear:2027,k401Trad1:.1,k401Trad2:.1,k401Emp1:.03,k401Emp2:.03,soy:{2026:{grossWages:10000,grossWages2:12000,ptWages:1000,ptWages2:2000},2027:{grossWages:10000,grossWages2:12000,ptWages:1000,ptWages2:2000}}}));
    const r=rows[1],dead=widowMode==='p1Survives'?2:1;
    near(r[`grossWages${dead}`],0); near(r[`ptWages${dead}`],0);
    near(r[`k401Contrib${dead}Trad`],0); near(r[`k401Emp${dead}Amt`],0);
    assert(rows[0].grossWages1>0 && rows[0].grossWages2>0);
  }
});
for(const method of ['NORMAL','OUTSIDE','IRA','WITHHOLD']){
  test(`overwithholding refund is returned once: ${method}`,()=>{
    const r=first(m.base({grossWages:20000,withholdPct:50},{cashFloor:5000,rothConvTaxFunding:method}));
    near(r.netWorth,20000-20000*.0765-r.incomeTax);
    assert(r.fundingTax<0); near(r.taxRefund,-r.fundingTax);
  });
  test(`Roth conversion and tax funding conserve assets: ${method}`,()=>{
    const r=first(m.base({cash:50000,sec:100000,ira1:500000,spending:30000},{cashFloor:10000,rothConvTaxFunding:method,ovIncomeLevel:[{magiTarget:100000,startYear:2026,endYear:2026}]}));
    near(r.netWorth,650000-30000-r.fundingTax-r.rothConvTaxWithheld);
    near(r.roth1,r.rothConvNet); assert(r.rothConv>0); assert(r.taxSolverConverged);
  });
  test(`manual tax funding pays dedicated conversion tax once: ${method}`,()=>{
    const r=first(m.base({cash:50000,sec:100000,ira1:500000,spending:30000},{cashFloor:10000,rothConvTaxFunding:method,ovSpending:[{taxOvr:2000,startYear:2026,endYear:2026}],ovIncomeLevel:[{magiTarget:100000,startYear:2026,endYear:2026}]}));
    const dedicated=(method==='OUTSIDE'||method==='IRA')?r.rothConvTaxFundingNeed:0;
    near(r.fundingTax,2000+dedicated);
    near(r.netWorth,650000-30000-r.fundingTax-r.rothConvTaxWithheld);
  });
}
test('loss-year account withdrawals cannot exceed assets after modeled growth',()=>{
  for(const account of ['sec','ira1','roth1']){
    const r=first(m.base({[account]:100000,spending:80000},{growthRate:-.5,stkGainPct:0}));
    assert(r.unfunded>0,account+' must show a shortfall');
    near(r.netWorth,0); assert(r.endCash>=0);
  }
});
test('loss-year conversions and dedicated tax draws use the same available balance',()=>{
  for(const method of ['NORMAL','OUTSIDE','IRA','WITHHOLD']){
    const r=first(m.base({ira1:100000},{growthRate:-.8,rothConvTaxFunding:method,ovIncomeLevel:[{magiTarget:100000,startYear:2026,endYear:2026}]}));
    assert(r.rothConv+r.ira1Addl+r.rmd1<=20000.51);
    near(r.netWorth,20000-r.fundingTax-r.rothConvTaxWithheld);
  }
});
test('projection does not leak solver variables into global scope',()=>{
  m.run(m.base({ira1:300000,spending:30000}));
  for(const name of ['unfunded_f','fundingChoice_f','irmaaMagi_f','qualDivs_f','taxableRMDs_f','taxableStkGain_f','w2AGI_f'])assert(!Object.hasOwn(m.context,name),name);
});
test('report payload carries HSA funding and solver diagnostics',()=>{
  const r=first(m.base({cash:3000,hsaDep:5000})); const out=m.report().rows[0];
  near(out.hsaDep,r.hsaDep); near(out.hsaDepositFunded,r.hsaDepositFunded);
  near(out.hsaDepositShortfall,r.hsaDepositShortfall);
  assert.equal(out.taxSolverConverged,r.taxSolverConverged);
});
test('legacy migration and JSON round-trip retain plan inputs',()=>{
  const s=m.base({cash:10000,spending:30000,ira1:400000});
  const migrated=m.migrate(s), round=m.migrate(JSON.parse(JSON.stringify(migrated)));
  assert.deepEqual(round,migrated); assert.deepEqual(m.run(round),m.run(migrated));
});
test('deterministic mixed retirement scenarios conserve every fully funded year',(t)=>{
  let seed=20261122,checked=0;
  const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<160;i++){
    const floor=[0,10000,25000][i%3];
    const s=m.base({cash:30000,sec:150000,ira1:700000,roth1:150000,hsa:30000,
      spending:30000+rnd()*60000,ptWages:rnd()*20000,hsaDep:i%5===0?3000:0,hsaWith:i%4===0?4000:0},
      {cashFloor:floor,endYear:2029,growthRate:-.2+rnd()*.35,divRate:.02,intRate:.02,
       divReinvestPct:rnd(),stkGainPct:rnd(),ssAge1:67,ssmo1:2000,
       rothConvTaxFunding:['NORMAL','OUTSIDE','IRA','WITHHOLD'][i%4],
       ...(i%2?{ovIncomeLevel:[{magiTarget:90000,startYear:2026,endYear:2029}]}:{})});
    const rows=m.run(s);
    for(const r of rows){
      assert(Number.isFinite(r.netWorth));
      for(const k of ['endCash','sec','ira1','ira2','roth1','roth2','hsa'])assert(r[k]>=0,k);
      if(r.unfunded>.5)continue;
      const opening=r.startCashBal+r.startSec+r.startIRA1+r.startIRA2+r.startRoth1+r.startRoth2+r.startHSA+r.startPre2020Inh1+r.startPre2020Inh2+r.startPost2020Inh;
      const growth=r.secGrowth+r.ira1Growth+r.ira2Growth+r.roth1Growth+r.roth2Growth+r.startHSA*r.gRate+
        [...r.pre2020LotDetails,...r.post2020LotDetails].reduce((sum,l)=>sum+l.endBal-l.startBal+l.draw,0);
      const contributions=r.k401Contrib1Trad+r.k401Contrib2Trad+r.k401Contrib1Roth+r.k401Contrib2Roth+r.k401Emp1Amt+r.k401Emp2Amt;
      const expected=opening+growth+r.atWages+r.ptWages+r.grossSS+r.divs+contributions-r.spending-r.fundingTax-r.rothConvTaxWithheld;
      near(r.netWorth,expected,`case ${i}, year ${r.yr}`,1.01); checked++;
    }
  }
  assert(checked>=500,`only ${checked} funded years checked`);
  t.diagnostic(`${checked} fully funded years reconciled across 160 synthetic four-year scenarios.`);
});
test('Roth Lab and Risk Lab project clones through the corrected engine',()=>{
  const s=m.base({cash:10000,ira1:400000,spending:40000},{endYear:2028,cashFloor:10000});
  m.run(s);
  const clone=JSON.parse(JSON.stringify(s));
  m.raw.rothLabApplyScenario(clone,{kind:'magi',customMagi:80000},2026,2028);
  const rows=m.run(clone); assert(rows.some(r=>r.rothConv>0));
  const out=m.raw.riskPathMetrics(rows,[1,1,1],{label:'Synthetic',stock:[0,0,0],bond:[0,0,0],infl:[0,0,0]});
  assert.equal(out.annual.length,3); assert.equal(out.depleted,false);
  assert.deepEqual(s.soy,{2026:{cash:10000,ira1:400000,spending:40000}});
});
test('cash-flow and printable report show HSA requirement and funding warning',()=>{
  m.run(m.base({cash:3000,hsaDep:5000}));
  const nodes=m.render();
  assert(nodes.get('cf-thead').innerHTML.includes('HSA Deposit'));
  assert(nodes.get('cf-accounting-warnings').innerHTML.includes('2,000'));
  const report=m.print();
  assert(report.includes('HSA Deposit\nRequired')); assert(report.includes('Only the funded amount'));
  assert(!report.includes('NaN')); assert(!report.includes('undefined'));
});
test('calculation warning appears only for a failed solver',()=>{
  assert.equal(m.raw.projectionAccountingWarningsHtml([{yr:2026,taxSolverConverged:true}]),'');
  assert(m.raw.projectionAccountingWarningsHtml([{yr:2026,taxSolverConverged:false}]).includes('did not settle'));
});
test('restricted HSA holdings are not used before maturity',()=>{
  const r=first(m.base({hsa:10000,hsaWith:8000,spending:8000},{restrictedInvestments:[{id:'hsa-restricted',accountKey:'hsa',value:7000,availableDate:'2028-01-01'}]}));
  near(r.hsaWith,3000); near(r.hsa,7000); near(r.unfunded,5000);
});
test('severe-loss RMD is capped and reported as an unmet distribution',()=>{
  const r=first(m.base({ira1:100000},{by1:1950,rmdStart1:2024,growthRate:-.999}));
  near(r.rmd1,100); assert(r.rmdUnfunded1>3000); assert(r.ira1>=0);
  assert(m.raw.projectionAccountingWarningsHtml([r]).includes('calculated RMD'));
});
test('zero withholding override still pays payroll taxes',()=>{
  const r=first(m.base({grossWages:20000,withholdPct:0}));
  near(r.atWages,20000-20000*.0765); near(r.netWorth,r.atWages);
});
test('retired depletion remains an explicit failure in Risk Lab',()=>{
  const rows=m.run(m.base({cash:10000,spending:15000},{endYear:2027}));
  near(rows[0].unfunded,5000);near(rows[0].netWorth,0);
  const metrics=m.raw.riskPathMetrics(rows,[1,1],{label:'Synthetic',stock:[0,0],bond:[0,0],infl:[0,0]});
  assert.equal(metrics.depleted,true);assert.equal(metrics.depletionYear,2026);
});
test('dashboard action plan agrees with cash-funded and unfunded years',()=>{
  m.run(m.base({cash:13000,spending:10000,hsaDep:5000}));
  const card=m.raw.apCard(2026);
  assert(card.includes('⚠ Funding Shortfall'));assert(card.includes('HSA Deposit Funded'));
  assert(card.includes('Cash Draw'));assert(!card.includes('✓ Step 1 Funded'));
  assert(!card.includes('No draws or conversions needed'));
  m.run(m.base({cash:20000,spending:10000}));
  const funded=m.raw.apCard(2026);
  assert(funded.includes('Account Draws Needed'));assert(!funded.includes('Funding Shortfall'));
});
test('a conversion alone is an account transfer, never printable spending funding',()=>{
  const r=first(m.base({ira1:200000},{rothConvTaxFunding:'WITHHOLD',ovIncomeLevel:[{magiTarget:100000,startYear:2026,endYear:2026}]}));
  assert(r.rothConv>0);near(r.totalFunding,0);
  const html=m.print();
  const table=html.match(/<table class="cf-table cf-screen-only"[\s\S]*?<\/table>/)[0];
  const header=table.match(/<tr class="cf-sub">([\s\S]*?)<\/tr>/)[1];
  const labels=[...header.matchAll(/<th[^>]*>([\s\S]*?)<\/th>/g)].map(x=>x[1].replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim());
  const cells=[...table.match(/<tbody>([\s\S]*?)<\/tbody>/)[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(x=>x[1].replace(/<[^>]*>/g,'').trim());
  assert.equal(cells[labels.indexOf('Total Funded')],'$0');
});
