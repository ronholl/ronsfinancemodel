const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {loadModel}=require('./model-harness.cjs');
const fixture=require('./fixtures/phase1-retired-baseline.json');
const m=loadModel(process.env.MODEL_FILE || path.join(__dirname,'..','index.html'));
const f=m.raw.family;
const plain=v=>JSON.parse(JSON.stringify(v));
function person(overrides={}){
  return Object.assign({id:'child-1',name:'Synthetic Child',relationship:'child',birthDate:'2010-06-15',notes:'',periods:{household:[],taxDependent:[],support:[],student:[]}},overrides);
}
function state(dependents=[],props={}){
  return m.base({},Object.assign({by1:1986,endYear:2045,familyTimeline:Object.assign(plain(f.defaults()),{enabled:true,dependents})},props));
}
const row=(s,y)=>plain(f.build(s)).years.find(r=>r.year===y);

for(const c of fixture.cases)test(`Phase 1 preserves all retirement outputs and interview steps: ${c.name}`,()=>{
  for(const setting of ['absent','off','on']){
    const input=plain(c.input);
    if(setting==='absent')delete input.familyTimeline;
    else input.familyTimeline={schemaVersion:1,enabled:setting==='on',dependents:[person({birthDate:'2020-12-31',periods:{taxDependent:[{start:'2026',end:'2044'}]}})]};
    assert.deepEqual(m.run(input),c.rows,setting);
    assert.deepEqual(m.report().rows,c.reportRows,setting);
    assert.deepEqual(plain(m.raw.setupVisibleSteps()),c.interviewSteps,setting);
  }
});

test('family timeline defaults to off with independent empty records',()=>{
  const a=f.defaults(),b=f.defaults();assert.equal(a.enabled,false);a.dependents.push(person());assert.equal(b.dependents.length,0);
  const input=m.base();assert.equal(input.familyTimeline.enabled,false);
  assert.deepEqual(plain(f.build(input)),{enabled:false,years:[],issues:[]});
});
test('legacy import retains the existing migration behavior and adds a disabled family namespace',()=>{
  const input=plain(fixture.cases[0].input);delete input.familyTimeline;
  const migrated=m.migrate(input);assert.equal(migrated.familyTimeline.enabled,false);
  const {familyTimeline,familyHealth,acaData,...financial}=migrated;
  assert.equal(acaData.autoApply,true);
  assert.equal(familyHealth.enabled,false);
  assert.deepEqual(financial,fixture.cases[0].migratedInput);
  assert.deepEqual(m.run(migrated),fixture.cases[0].migratedRows);
});
test('normalization preserves names, unknown metadata and stable record identifiers',()=>{
  const raw={enabled:true,dependents:[person({id:'duplicate',extensionNote:'keep'}),person({id:'duplicate',name:'Second'})],extra:{keep:true}};
  const first=plain(f.normalize(raw)),second=plain(f.normalize(first));
  assert.deepEqual(first,second);assert.notEqual(first.dependents[0].id,first.dependents[1].id);
  assert.equal(first.dependents[0].extensionNote,'keep');assert.deepEqual(first.extra,{keep:true});
  assert.equal(raw.dependents[1].id,'duplicate');
});
test('disable and re-enable retain all timeline records',()=>{
  const original=plain(f.normalize({enabled:true,dependents:[person()]}));
  const off=plain(f.reduce(original,{type:'enabled',value:false},2026));
  assert.equal(off.enabled,false);assert.deepEqual(off.dependents,original.dependents);
  const back=plain(f.reduce(off,{type:'enabled',value:true},2026));assert.deepEqual(back,original);
});
test('future schemas are retained without being reinterpreted or edited',()=>{
  const profile={schemaVersion:7,enabled:true,dependents:[{id:'future',newField:{keep:1}}],futureRules:['keep']};
  const s=state([],{familyTimeline:profile});
  const result=plain(f.build(s));assert.equal(result.years.length,0);assert.match(result.issues[0].message,/unsupported version/);
  const edited=plain(f.reduce(profile,{type:'addDependent'},2026));assert.deepEqual(edited.dependents,profile.dependents);
  const off=plain(f.reduce(profile,{type:'enabled',value:false},2026));assert.equal(off.schemaVersion,7);assert.deepEqual(off.futureRules,['keep']);
});
test('strict dates handle leap years without local-timezone shifts',()=>{
  assert(f.date('2000-02-29'));assert(f.date('2024-02-29'));
  for(const value of ['1900-02-29','2023-02-29','2026-04-31','2026-13-01','2026-01-00','2026-2-03','2026-01-01T00:00:00Z'])assert.equal(f.date(value),null,value);
  assert.equal(f.age('2010-12-31','2026-12-30'),15);assert.equal(f.age('2010-12-31','2026-12-31'),16);
  assert.equal(f.age('2028-02-29','2028-02-28'),null);assert.equal(f.age('2028-02-29','2029-12-31'),1);
});
test('dependent ages are measured at December 31 including newborn age zero',()=>{
  const s=state([person({birthDate:'2026-12-31'})]);
  assert.equal(row(s,2026).dependents[0].age,0);assert.equal(row(s,2027).dependents[0].age,1);
});
test('a planned future child is not counted before birth',()=>{
  const s=state([person({birthDate:'2028-12-31',periods:{taxDependent:[{start:'2028',end:''}]}})]);
  assert.equal(row(s,2026).dependents[0].notBorn,true);assert.equal(row(s,2026).plannedTaxDependentCount,0);
  assert.equal(row(s,2028).plannedTaxDependentCount,1);assert.equal(row(s,2028).dependents[0].age,0);
});
test('planned tax dependency includes both endpoint years and supports gaps',()=>{
  const s=state([person({periods:{taxDependent:[{start:'2026',end:'2028'},{start:'2031',end:'2032'}]}})]);
  for(const y of [2026,2028,2031,2032])assert.equal(row(s,y).plannedTaxDependentCount,1,String(y));
  for(const y of [2029,2030,2033])assert.equal(row(s,y).plannedTaxDependentCount,0,String(y));
});
test('ongoing periods continue through the plan end',()=>{
  const s=state([person({periods:{support:[{start:'2026-01-01',end:''}]}})]);
  assert.equal(row(s,2045).supportedCount,1);
});
test('date periods recognize partial years and inclusive final days',()=>{
  const s=state([person({periods:{support:[{start:'2026-12-31',end:'2027-01-01'}]}})]);
  assert.equal(row(s,2026).dependents[0].support,'partial');assert.equal(row(s,2027).dependents[0].support,'partial');
  assert.equal(row(s,2028).dependents[0].support,'none');
});
test('adjacent ranges can cover a full year; overlapping ranges count once',()=>{
  const s=state([person({periods:{support:[{start:'2026-01-01',end:'2026-06-30'},{start:'2026-07-01',end:'2026-12-31'},{start:'2026-05-01',end:'2026-09-01'}]}})]);
  assert.equal(row(s,2026).supportedCount,1);assert.equal(row(s,2026).dependents[0].support,'full');
  assert(plain(f.validate(s)).some(i=>/overlapping/.test(i.message)));
});
test('household, tax dependency, support and student plans remain independent',()=>{
  const s=state([person({periods:{household:[{start:'2010-06-15',end:'2027-08-01'}],taxDependent:[{start:'2026',end:'2030'}],support:[{start:'2026-01-01',end:'2029-12-31'}],student:[{start:'2028-09-01',end:'2030-05-31'}]}})]);
  const r=row(s,2028).dependents[0];assert.equal(r.household,'none');assert.equal(r.taxDependent,'full');assert.equal(r.support,'full');assert.equal(r.student,'partial');
});
test('missing dates or years are shown as unspecified, without inventing dependency',()=>{
  const s=state([person({birthDate:''})]);const r=row(s,2026);
  assert.equal(r.dependents[0].age,null);assert.equal(r.dependents[0].taxDependent,'unspecified');
  assert.equal(r.plannedTaxDependentCount,0);assert.equal(r.taxDependencyUnspecifiedCount,1);
});
test('invalid and reversed periods produce review errors rather than valid counts',()=>{
  for(const range of [{start:'2027',end:'2026'},{start:'',end:'2028'},{start:'2026.5',end:''}]){
    const s=state([person({periods:{taxDependent:[range]}})]);
    assert(plain(f.validate(s)).some(i=>i.severity==='error'));
    assert.equal(row(s,2026).dependents[0].taxDependent,'invalid');assert.equal(row(s,2026).plannedTaxDependentCount,0);
  }
  const s=state([person({periods:{support:[{start:'2027-06-01',end:'2026-06-01'}]}})]);
  assert.equal(row(s,2026).dependents[0].support,'invalid');
});
test('periods before birth are rejected while a birth-year tax assumption is allowed',()=>{
  const s=state([person({birthDate:'2026-12-31',periods:{support:[{start:'2026-01-01',end:''}],taxDependent:[{start:'2026',end:''}]}})]);
  const r=row(s,2026).dependents[0];assert.equal(r.support,'invalid');assert.equal(r.taxDependent,'full');
});
test('exact adult dates never overwrite legacy birth-year or retirement timing',()=>{
  const s=state([]);s.familyTimeline.birthDate1='1985-06-15';const previous=m.run(s);
  const result=plain(f.build(s));assert.equal(result.years[0].adults[0].age,41);
  assert(result.issues.some(i=>/differs/.test(i.message)));assert.equal(s.by1,1986);assert.deepEqual(m.run(s),previous);
});
test('adult timeline ages use a disclosed birth-year approximation when no exact date exists',()=>{
  const s=state([]);const adult=row(s,2026).adults[0];assert.equal(adult.age,40);assert.equal(adult.approximate,true);
});
test('timeline records independent wage endings and the existing survivor event',()=>{
  const s=state([],{name2:'Synthetic Partner',householdMode:'couple',by2:1988,wagesEnd1:2041,wagesEnd2:2043,widowMode:'p1Survives',widowDeathYear:2042});
  assert(row(s,2041).events.includes('Synthetic Retiree: last W-2 wage year'));
  assert(row(s,2042).events.includes('Synthetic Partner: modeled death year'));
  assert.equal(row(s,2043).adults[1].deceased,true);assert.equal(row(s,2043).adults[0].deceased,false);
});
test('timeline builder is pure and repeatable, and does not modify financial state',()=>{
  const s=state([person()]),before=JSON.stringify(s);const a=plain(f.build(s)),b=plain(f.build(s));
  assert.deepEqual(a,b);assert.equal(JSON.stringify(s),before);
});
test('reducer adds, edits and removes records without changing the original profile',()=>{
  let p=plain(f.defaults()),initial=JSON.stringify(p);
  p=plain(f.reduce(p,{type:'addDependent'},2026));const id=p.dependents[0].id;
  p=plain(f.reduce(p,{type:'memberField',member:0,key:'name',value:'Example Child'},2026));
  p=plain(f.reduce(p,{type:'addPeriod',member:0,kind:'support'},2026));
  p=plain(f.reduce(p,{type:'periodField',member:0,kind:'support',period:0,key:'end',value:'2030-12-31'},2026));
  assert.equal(p.dependents[0].periods.support[0].end,'2030-12-31');assert.equal(p.dependents[0].id,id);
  p=plain(f.reduce(p,{type:'removePeriod',member:0,kind:'support',period:0},2026));assert.equal(p.dependents[0].periods.support.length,0);
  p=plain(f.reduce(p,{type:'removeDependent',member:0},2026));p=plain(f.reduce(p,{type:'addDependent'},2026));assert.notEqual(p.dependents[0].id,id);
  assert.equal(initial,JSON.stringify(plain(f.defaults())));
});
test('new future-child periods start no earlier than the entered birth date',()=>{
  let p=plain(f.normalize({enabled:true,dependents:[person({birthDate:'2028-07-01'})]}));
  p=plain(f.reduce(p,{type:'addPeriod',member:0,kind:'household'},2026));
  p=plain(f.reduce(p,{type:'addPeriod',member:0,kind:'taxDependent'},2026));
  assert.equal(p.dependents[0].periods.household[0].start,'2028-07-01');assert.equal(p.dependents[0].periods.taxDependent[0].start,'2028');
});
test('JSON backup round-trip preserves enabled and disabled family records',()=>{
  for(const enabled of [false,true]){
    const s=state([person({notes:'School plans\nSecond line',periods:{taxDependent:[{start:'2026',end:'2030'}]}})]);s.familyTimeline.enabled=enabled;
    const a=m.migrate(s),b=m.migrate(JSON.parse(JSON.stringify(a)));assert.deepEqual(a,b);
  }
});
test('family editor escapes imported names and notes',()=>{
  m.run(state([person({name:'<img src=x onerror=alert(1)>',notes:'<script>alert(1)</script>'})]));
  const html=f.render();assert(html.includes('&lt;img'));assert(!html.includes('<img src=x'));assert(!html.includes('<script>alert'));
});
test('family tab is absent when disabled, visible when enabled, and no interview steps are added',()=>{
  m.run(m.base());const off=m.setup();assert(!off.includes('class="setup-tab active" onclick="setupSetView(\'family\')"'));assert(!off.includes('>Family Timeline</button>'));
  m.run(state([person()]));const on=m.setup('family');assert(on.includes('>Family Timeline</button>'));assert(on.includes('Year-by-year family timeline'));
  assert(on.includes('do not verify tax eligibility'));assert(on.includes('not ACA household-size'));
});
test('timeline rejects an invalid or oversized year range',()=>{
  for(const props of [{startYear:2030,endYear:2026},{startYear:2026,endYear:2126}]){
    const result=plain(f.build(state([],props)));assert.equal(result.years.length,0);assert.equal(result.issues.at(-1).field,'planYears');
  }
});
