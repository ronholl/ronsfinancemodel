const fields = ['yr','age1','age2','spending','cashDraw','stkSales','ira1Addl','ira2Addl','rothDraw1','rothDraw2','hsaWith','hsaDep','grossSS','rmd1','rmd2','pre2020InhDraw','pre2020InhAddl','post2020InhDraw','mandatoryFunding','totalFunding','totalRequired','fundingTax','unfunded','excessFunds','cashSweep','agi','magi','fedOrd','ltcg','stTax','incomeTax','irmaaTx','irmaaMagi','irmaaLookbackYear','irmaaSurvivorRelief','medicareBase','taxFiling','rothConv','rothConvNet','rothConvTax','rothConvTaxOutsideCash','rothConvTaxOutsideSecurities','rothConvTaxIraWithdrawal','rothConvTaxWithheld','endCash','sec','ira1','ira2','roth1','roth2','hsa','pre2020Inh1','pre2020Inh2','post2020Inh','netWorth'];
const select = row => Object.fromEntries(fields.filter(k=>k in row).map(k=>[k,row[k]]));
function scenarios(m) {
  const cases = [
    ['single-retired-cash-and-SS',m.base({cash:30000,spending:42000,sec:250000,ira1:500000,roth1:150000},{cashFloor:10000,ssAge1:67,ssmo1:2400,endYear:2030,growthRate:.04,divRate:.015,intRate:.02,spendInfl:.02})],
    ['joint-IRA-first',m.base({cash:10000,spending:75000,ira1:900000,ira2:600000,roth1:200000},{name2:'Synthetic Spouse',householdMode:'couple',by2:1957,filing:'MFJ',state:'CA',cashFloor:10000,ssAge1:67,ssAge2:67,ssmo1:2500,ssmo2:1800,fundingOrder1:'IRA',fundingOrder2:'SEC',endYear:2030,growthRate:.04})],
    ['brokerage-tax-and-muni',m.base({cash:10000,spending:50000,secTaxableBal:400000,secTreasuryBal:100000,secCAMuniBal:100000,secOtherMuniBal:50000},{state:'CA',cashFloor:10000,qualDivsMode:'qualified',stkGainPct:.5,growthRate:.04,divRate:.025,divReinvestPct:.5,endYear:2028})],
    ['RMDs-and-inherited-lots',m.base({cash:10000,spending:50000,ira1:500000},{by1:1950,rmdStart1:2024,cashFloor:10000,growthRate:.03,endYear:2028,pre2020InhLots:[{id:'pre-fixture',beneficiary:'1',ownerBy:1940,deathYear:2018,startYear:2026,balance:100000}],post2020InhLots:[{id:'post-fixture',beneficiary:'1',ownerBy:1940,deathYear:2020,startYear:2026,balance:150000,strategy:'even'}]})],
    ['survivor-accounts-and-relief',m.base({cash:10000,spending:50000,ira1:500000,ira2:300000,roth1:80000,roth2:50000},{name2:'Synthetic Spouse',householdMode:'couple',by2:1953,filing:'MFJ',cashFloor:10000,widowMode:'p1Survives',widowDeathYear:2026,widowSSA44Relief:true,widowIraSpousePct:60,ssAge1:67,ssAge2:67,ssmo1:2500,ssmo2:1800,endYear:2029})],
    ['closeout-lookback-and-SOY',m.base({cash:10000,ira1:400000,spending:30000},{cashFloor:10000,endYear:2029,yearEndCloseouts:{2026:{status:'final',agi:180000,magi:200000,federalIncomeTax:24000,stateIncomeTax:6000}},soy:{2026:{cash:10000,ira1:400000,spending:30000},2028:{cash:15000,ira1:390000,spending:31000}}})]
  ];
  for(const method of ['NORMAL','OUTSIDE','IRA','WITHHOLD']) {
    cases.push([`conversion-${method}`,m.base({cash:70000,sec:100000,ira1:500000,roth1:50000,spending:40000},{cashFloor:10000,rothConvTaxFunding:method,ovIncomeLevel:[{magiTarget:100000,startYear:2026,endYear:2028}],endYear:2028})]);
  }
  return cases;
}
module.exports={scenarios,select};
