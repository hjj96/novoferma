'use strict';
// Portable source/behavior checks. Visual acceptance uses the actual browser separately.
const {spawnSync}=require('node:child_process');
const {readdirSync,existsSync}=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
function run(command,args){
 const result=spawnSync(command,args,{cwd:root,stdio:'inherit'});
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status||1);
}
run(process.env.PYTHON||'python3',['scripts/check_site.py']);
for(const file of readdirSync(path.join(root,'output/concept')).filter(x=>x.endsWith('.js'))){
 run(process.execPath,['--check',path.join('output/concept',file)]);
}
if(existsSync(path.join(__dirname,'check_interactions.cjs')))run(process.execPath,['scripts/check_interactions.cjs']);
console.log('Site source, JavaScript syntax and available interaction checks passed.');

