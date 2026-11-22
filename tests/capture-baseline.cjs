// Capture only from the backed-up, pre-Phase-0 application, before editing it.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {loadModel}=require('./model-harness.cjs');
const {scenarios,select}=require('./cases.cjs');
const file=process.argv[2];
if(!file)throw Error('Pass the original application file explicitly.');
const m=loadModel(file);
const cases=scenarios(m).map(([name,input])=>{
  const rows=m.run(input); const report=m.report();
  return {name,input,expected:rows.map(select),reportRows:report.rows.map(select)};
});
fs.writeFileSync(path.join(__dirname,'fixtures','retired-baseline.json'),JSON.stringify({sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),cases},null,2)+'\n');
console.log(`Captured ${cases.length} synthetic retired-household fixtures.`);
