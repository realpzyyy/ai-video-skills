// Shared deterministic scene source for the offline gallery and Remotion.
export const TEMPLATE_VERSION = '2.1.0';
export const STYLE_IDS = ['tactile', 'editorial', 'precision'];
export const PALETTE_IDS = ['apricot', 'sky', 'lilac'];
export const LAYOUT_IDS = ['collect', 'compare', 'steps', 'aroll'];
export const example = {
  style_id:'tactile',palette_id:'apricot',layout:'collect',
  title:['把知识','打包成 Skill'],kicker:'把课堂知识变成可用工具',
  labels:['方法论','知识点','解决思路'],concept:'AI Skill',
  description:'方法与练习的工具包',benefit:'课后可以安装、实践',
  caption_lines:['打包成一个 AI Skill'],highlights:['AI Skill'],
  compare:[{title:'只给资料',body:'内容停留在阅读',symbol:'≡'},{title:'交付工具',body:'方法进入实践',symbol:'↗'}],
  steps:[{title:'选择方法',body:'找到当前问题'},{title:'安装工具',body:'带入实际材料'},{title:'动手实践',body:'形成自己的结果'}],
  result:'从理解，走向行动',duration_seconds:6
};
export const escapeHTML = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const units = s => [...s].reduce((n,c)=>n+(/[^\x00-\x7f]/.test(c)?1:.55),0);
const requireText = (s,max,name) => {
  if(typeof s!=='string'||!s.trim()||units(s)>max) throw Error(name+': empty or too long; split meaningfully, never shrink type');
};
export function validateScene(c){
  if(!STYLE_IDS.includes(c.style_id)||!PALETTE_IDS.includes(c.palette_id)||!LAYOUT_IDS.includes(c.layout)) throw Error('Unknown standard style, palette or layout');
  if(!Array.isArray(c.title)||c.title.length!==2) throw Error('Two semantic title lines required');
  c.title.forEach(t=>requireText(t,c.style_id==='editorial'?9:7.2,'title'));
  requireText(c.kicker,22,'kicker'); requireText(c.description,14,'description');
  requireText(c.benefit,18,'benefit'); requireText(c.concept,c.style_id==='precision'?4.8:7.5,'concept');
  if(!Array.isArray(c.labels)||c.labels.length!==3)throw Error('Three labels required');
  c.labels.forEach(t=>requireText(t,4,'label'));
  if(!Array.isArray(c.caption_lines)||c.caption_lines.length<1||c.caption_lines.length>2)throw Error('One or two caption lines required');
  c.caption_lines.forEach(t=>requireText(t,14,'caption'));
  if(!Array.isArray(c.highlights)||c.highlights.some(s=>typeof s!=='string'||!s||!c.caption_lines.some(l=>l.includes(s))))throw Error('Highlights must be exact spoken caption substrings');
  if(!Number.isFinite(c.duration_seconds)||c.duration_seconds<3||c.duration_seconds>30)throw Error('Scene duration must be 3–30 seconds');
  if(c.layout==='compare'){
    if(!Array.isArray(c.compare)||c.compare.length!==2)throw Error('Two comparison objects required');
    c.compare.forEach(x=>{requireText(x.title,6,'compare title');requireText(x.body,9,'compare body');requireText(x.symbol,1,'compare symbol');});
    requireText(c.result,16,'result');
  }
  if(c.layout==='steps'){
    if(!Array.isArray(c.steps)||c.steps.length!==3)throw Error('Three actual steps required');
    c.steps.forEach(x=>{requireText(x.title,6,'step title');requireText(x.body,10,'step body');});
    requireText(c.result,16,'result');
  }
  return c;
}
export const clamp = x=>Math.max(0,Math.min(1,x));
export function phase(t,start,duration=.45){const p=clamp((t-start)/duration);return 1-Math.pow(1-p,3);}
const enter=(t,start)=>{const p=phase(t,start);return 'opacity:'+p+';translate:0 '+((1-p)*26)+'px';};
const connection=(t,start)=>'stroke-dasharray:1;stroke-dashoffset:'+(1-phase(t,start,.7));
export function portraitRect(style,layout='collect'){
  if(layout==='aroll')return {left:48,top:70,width:624,height:940,borderRadius:style==='editorial'?'180px 180px 12px 12px':style==='precision'?12:36};
  return style==='tactile'?{left:474,top:92,width:198,height:292,borderRadius:'80px 80px 40px 40px'}:
    style==='editorial'?{left:48,top:386,width:265,height:471,borderRadius:'140px 140px 8px 8px'}:
    {left:48,top:104,width:165,height:294,borderRadius:8};
}
export function demoPortrait(){
  return '<svg viewBox="0 0 220 330" role="img" aria-label="通用人物示意，非真人素材"><rect width="220" height="330" fill="#e7e2d9"/><path d="M22 330v-48q8-64 88-66 80 2 88 66v48" fill="#64736e"/><rect x="83" y="185" width="54" height="61" rx="23" fill="#c4a58c"/><ellipse cx="110" cy="126" rx="67" ry="84" fill="#d7bda5"/><path d="M43 125q-7-86 67-88 72 0 67 92l-20-56q-30 28-92 10z" fill="#3f4743"/><path d="M57 119h48v28H59zm58 0h48l-2 28h-46zm-10 9h10" fill="none" stroke="#4d514d" stroke-width="5"/><path d="M88 177q22 15 45 0" fill="none" stroke="#886954" stroke-width="3"/></svg>';
}
function captionMarkup(c){
  const keys=[...c.highlights].sort((a,b)=>b.length-a.length);
  const mark=line=>{let out='',i=0;while(i<line.length){const k=keys.find(x=>line.startsWith(x,i));if(k){out+='<em>'+escapeHTML(k)+'</em>';i+=k.length;}else{out+=escapeHTML(line[i++]);}}return out;};
  return '<div class="caption">'+c.caption_lines.map(l=>'<span class="caption-line check-text">'+mark(l)+'</span>').join('')+'</div>';
}
function artwork(c,t){
  const e=escapeHTML;
  if(c.layout==='aroll')return '';
  if(c.layout==='compare')return c.compare.map((x,i)=>'<div class="compare-panel '+(i?'second':'first')+'" style="'+enter(t,.2+i*.5)+'"><div class="compare-symbol">'+e(x.symbol)+'</div><h3 class="check-text">'+e(x.title)+'</h3><p class="check-text">'+e(x.body)+'</p><span class="diagram-lines"></span></div>').join('')+'<div class="compare-result check-text" style="'+enter(t,1.5)+'">'+e(c.result)+'</div>';
  if(c.layout==='steps')return c.steps.map((x,i)=>'<div class="step" style="top:'+(i*158)+'px;'+enter(t,.2+i*.6)+'"><span class="step-number">0'+(i+1)+'</span><b class="check-text">'+e(x.title)+'</b><small class="check-text">'+e(x.body)+'</small></div>'+(i<2?'<div class="step-connector" style="top:'+(128+i*158)+'px;opacity:'+phase(t,.7+i*.6)+'"></div>':'')).join('')+'<div class="steps-result check-text" style="'+enter(t,2)+'">'+e(c.result)+'</div>';
  if(c.style_id==='tactile')return '<svg class="arrow-lines" viewBox="0 0 620 560"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">'+['M95 245 Q95 304 193 324','M300 228V319','M501 255 Q510 304 427 325'].map((d,i)=>'<path pathLength="1" d="'+d+'" style="'+connection(t,.8+i*.2)+'"/>').join('')+'</g></svg>'+
    c.labels.map((l,i)=>'<div class="paper '+['one','two','three'][i]+'" style="'+enter(t,.15+i*.3)+'"><i></i><b class="check-text">'+e(l)+'</b><span class="lines"></span></div>').join('')+
    '<div class="kit-back" style="'+enter(t,1.5)+'"></div><div class="kit-tab" style="'+enter(t,1.5)+'"></div><div class="kit-front" style="'+enter(t,1.7)+'"><strong class="check-text">'+e(c.concept)+'</strong><small class="check-text">'+e(c.description)+'</small><i class="kit-dot"></i></div>';
  if(c.style_id==='editorial')return c.labels.map((l,i)=>'<div class="editor-item check-text" style="'+enter(t,.2+i*.45)+'"><span>0'+(i+1)+'</span>'+e(l)+'</div>').join('')+'<div class="editor-arrow" style="opacity:'+phase(t,1.45)+';scale:1 '+phase(t,1.45)+'"></div><div class="editor-kit check-text" style="'+enter(t,1.8)+'">'+e(c.concept)+'</div>';
  return '<svg class="connections" viewBox="0 0 624 492"><g fill="none" stroke="currentColor" stroke-width="3">'+['M236 46H290Q322 46 322 78V171Q322 201 355 201H396','M236 201H396','M236 356H290Q322 356 322 324V231Q322 201 355 201'].map((d,i)=>'<path pathLength="1" d="'+d+'" style="'+connection(t,.7+i*.35)+'"/>').join('')+'</g></svg>'+c.labels.map((l,i)=>'<div class="node check-text" style="top:'+(i*155)+'px;'+enter(t,.15+i*.35)+'">'+e(l)+'</div>').join('')+'<div class="node-hub check-text" style="'+enter(t,1.7)+'">'+e(c.concept)+'</div><div class="hub-note check-text" style="'+enter(t,1.9)+'">'+e(c.description)+'</div>';
}
export function sceneHTML(config,time=3,{portrait='',demo=false}={}){
  const c=validateScene(config),e=escapeHTML;
  const local=clamp(time/c.duration_seconds)*6;
  const fade=1-phase(time,c.duration_seconds-.25,.25);
  if(portrait&&!/^data:image\/(png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(portrait))throw Error('Only embedded local raster portrait allowed');
  const face=portrait?'<img src="'+portrait+'" alt="本次原片人物">':demo?demoPortrait():'';
  return '<div class="canvas '+c.style_id+' palette '+c.palette_id+' '+(c.layout==='aroll'?'aroll':'')+'" data-style="'+c.style_id+'" data-palette="'+c.palette_id+'" data-layout="'+c.layout+'" style="opacity:'+fade+'"><div class="kicker check-text">'+e(c.kicker)+'</div><h4>'+c.title.map(l=>'<span class="check-text">'+e(l)+'</span>').join('')+'</h4><div class="portrait">'+face+'</div>'+(c.style_id==='editorial'?'<div class="red-rule" style="scale:'+phase(local,0,.6)+' 1;transform-origin:left"></div>':'')+'<div class="artwork '+c.layout+'">'+artwork(c,local)+'</div><p class="benefit check-text" style="'+enter(local,2)+'">'+e(c.benefit)+'</p>'+captionMarkup(c)+'<div class="footnote">'+(demo?'公开模板示意 · 非真人/非软件界面':'概念示意 · 非软件操作界面')+'</div></div>';
}
