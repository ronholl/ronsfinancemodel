const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function loadModel(file = path.join(__dirname, '..', 'index.html')) {
  const html = fs.readFileSync(file, 'utf8');
  const start = html.indexOf('const RMD_TABLE =');
  const end = html.indexOf('</script>', start);
  if (start < 0 || end < 0) throw new Error('Application calculation script not found');
  const storage = new Map();
  const nodes=new Map(); let renderMode=false, reportHtml='';
  const document = {addEventListener(){}, getElementById(id){
    if(!renderMode)return null;
    if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',value:'',style:{},dataset:{},focus(){},querySelectorAll(){return [];},classList:{add(){},remove(){},toggle(){}}});
    return nodes.get(id);
  }, querySelectorAll(){return [];},querySelector(){return null;}};
  const context = vm.createContext({
    console, document, window:{open(){return {document:{open(){},write(html){reportHtml+=html;},close(){}},focus(){}};}}, history:{}, navigator:{userAgent:'Phase 0 regression harness'},
    location:{search:'',protocol:'file:',href:'file:///regression/index.html'},
    localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)},
    URL, URLSearchParams, Blob, setTimeout(){return 0;}, clearTimeout(){}, setInterval(){return 0;}, clearInterval(){},
    fetch(){throw new Error('Network access is disabled in regression tests');}
  });
  vm.runInContext(html.slice(start,end) + `\n globalThis.testApi = {
    defaultState, applyMigrations, runProjection, buildReportPayload, buildPortfolioBucketPlan,
    calcFedTax, getScaledTables, calcSuggestedWithholdPct, riskPathMetrics,
    projectionAccountingWarningsHtml:typeof projectionAccountingWarningsHtml==='function'?projectionAccountingWarningsHtml:undefined,
    renderCF, renderYD, generateReport, apCard,
    renderSetupGuide, setupVisibleSteps, renderSetupHouseholdStep,
    setSetupView(view){setupView=view;}, getState(){return S;},
    family:typeof buildFamilyTimeline==='function'?{
      defaults:familyTimelineDefaults, normalize:normalizeFamilyTimeline, date:familyDate, age:familyAgeAtDate,
      validate:validateFamilyTimeline, build:buildFamilyTimeline, reduce:reduceFamilyTimeline,
      render:renderSetupFamilyView, commit:familyCommit
    }:null,
    health:typeof healthDefaults==='function'?{
      defaults:healthDefaults,normalize:normalizeHealth,month:healthMonth,coverage:healthCoverageForYear,
      config:healthYearConfig,magi:calcAcaMagi,rate:acaContributionRate,estimate:estimateHealthCost,
      medicareMonth:healthMedicareMonth,render:renderSetupHealthView,commit:healthCommit,summary:healthSummaryHtml
    }:null,
    aca:typeof acaDataDefaults==='function'?{defaults:acaDataDefaults,normalize:normalizeAcaData,validate:acaValidateUpdate,policy:acaPolicyForYear,apply:acaApplyUpdates,current:acaUpdateCurrent,monitor:acaMonitorMessage,accept:acaAcceptManifest,startLoad:acaLoadInitialPlan,panel:acaRenderPanel,taxCurrent:taxUpdateIsCurrent,taxAllowed:taxUpdateAllowedKeys}:null,
    rothLabApplyScenario, riskScenarioState,
    setState(state){ S=state; proj=runProjection(state); return proj; },
    report(){return buildReportPayload();}
  };`, context, {filename:file,timeout:10000});
  const api = context.testApi;
  const plain = value => JSON.parse(JSON.stringify(value));
  return {
    base(soy = {}, props = {}) {
      return Object.assign(plain(api.defaultState()), {
        name1:'Synthetic Retiree', householdMode:'single', by1:1955, filing:'SINGLE', state:'',
        startYear:2026,endYear:2026, rmdStart1:2031,rmdStart2:9999,
        growthRate:0,divRate:0,intRate:0,spendInfl:0,wageGrowth:0,ssCola:0,
        bracketInfl:0,irmaaInfl:0,medicareCostInfl:0,soy:{2026:soy}
      },props);
    },
    run(state){return plain(api.setState(plain(state)));},
    migrate(state){return plain(api.applyMigrations(plain(state)));},
    report(){return plain(api.report());},
    render(){renderMode=true;api.renderCF();return nodes;},
    print(){renderMode=true;reportHtml='';api.generateReport();return reportHtml;},
    setup(view='interview'){renderMode=true;api.setSetupView(view);api.renderSetupGuide();return nodes.get('setup-guide-root').innerHTML;},
    raw:api, context, html
  };
}
module.exports={loadModel};
