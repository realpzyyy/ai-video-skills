#!/usr/bin/env node
// Uses an existing Remotion runtime. No dependency installation or media upload.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {example,validateScene,STYLE_IDS,PALETTE_IDS,LAYOUT_IDS} from '../assets/studio.mjs';
const base=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2),flags={};
for(let i=0;i<args.length;i++){const k=args[i];if(k==='--demo'||k==='--still')flags[k]=true;else if(k.startsWith('--')&&args[i+1])flags[k]=args[++i];else throw Error('Invalid argument '+k)}
const known=['--demo','--still','--runtime','--browser','--output','--project','--scene','--python','--style','--palette','--layout','--frame'];
if(Object.keys(flags).some(k=>!known.includes(k)))throw Error('Unknown flag');
if(!flags['--runtime']||!flags['--output'])throw Error('Need --runtime existing-project-dir --output new-file.mp4|png');
if(!flags['--browser']||!fs.existsSync(flags['--browser']))throw Error('Need --browser path-to-existing-Chrome-executable; automatic browser downloads are disabled');
let config,props;
if(flags['--demo']){
  if(flags['--scene']||flags['--project'])throw Error('Public demo never accepts a private project or scene');
  config={...example,style_id:flags['--style']||'tactile',palette_id:flags['--palette']||'apricot',layout:flags['--layout']||'collect'};
  props={config,demo:true};
}else{
  if(!flags['--project']||!flags['--scene'])throw Error('Pause: confirmed --project and --scene required before render');
  if(flags['--style']||flags['--palette']||flags['--layout'])throw Error('Use the approved scene file, not CLI overrides');
  config=JSON.parse(fs.readFileSync(flags['--scene'],'utf8'));
  const gate=spawnSync(flags['--python']||'python3',[path.join(base,'check_gate.py'),'--project',flags['--project'],'--scene',flags['--scene']],{encoding:'utf8'});
  if(gate.error||gate.status!==0)throw Error(gate.stderr||gate.error?.message||'Gate failed');
  props={config,demo:false,portrait:config.portrait_data_url||''};
  if(!props.portrait)throw Error('Scene export needs portrait_data_url from the approved local source. For moving video integrate StandardScene in the host timeline.');
}
validateScene(config);
const output=path.resolve(flags['--output']);
if(fs.existsSync(output))throw Error('Refusing to overwrite output');
if(!fs.existsSync(path.dirname(output)))throw Error('Output parent must exist');
if(flags['--still']&&!output.endsWith('.png'))throw Error('Still output must be PNG');
if(!flags['--still']&&!output.endsWith('.mp4'))throw Error('Video output must be MP4');
const runtime=path.resolve(flags['--runtime']),req=createRequire(path.join(runtime,'package.json'));
const {bundle}=req('@remotion/bundler'),{selectComposition,renderStill,renderMedia}=req('@remotion/renderer');
// Bundler resolves copies against the chosen existing runtime, never this author's machine.
const job=fs.mkdtempSync(path.join(os.tmpdir(),'talking-head-render-'));
for(const name of ['studio.mjs','studio.css','studio-remotion.tsx'])fs.copyFileSync(path.join(base,'../assets',name),path.join(job,name));
fs.symlinkSync(path.join(runtime,'node_modules'),path.join(job,'node_modules'),process.platform==='win32'?'junction':'dir');
process.chdir(job); // Keep Remotion build caches out of the installed Skill directory.
fs.writeFileSync(path.join(job,'entry.tsx'),"import {registerRoot} from 'remotion'; import {StudioRoot} from './studio-remotion'; registerRoot(StudioRoot);\n",{flag:'wx'});
const serveUrl=await bundle({entryPoint:path.join(job,'entry.tsx')});
const browserOptions={browserExecutable:path.resolve(flags['--browser']),onBrowserDownload:()=>{throw Error('Browser download not authorized')}};
const composition=await selectComposition({serveUrl,id:'StandardScene',inputProps:props,...browserOptions});
const frame=flags['--frame']===undefined?90:Number(flags['--frame']);
if(flags['--still']){
  if(!Number.isInteger(frame)||frame<0||frame>=composition.durationInFrames)throw Error('Invalid still frame');
  await renderStill({serveUrl,composition,inputProps:props,output,imageFormat:'png',frame,...browserOptions});
}else await renderMedia({serveUrl,composition,inputProps:props,outputLocation:output,codec:'h264',pixelFormat:'yuv420p',concurrency:2,...browserOptions});
console.log(JSON.stringify({output,type:flags['--demo']?'public_template_demo_not_final':'scene_asset_not_final',template_version:'2.1.0',temporary_job:job}));
