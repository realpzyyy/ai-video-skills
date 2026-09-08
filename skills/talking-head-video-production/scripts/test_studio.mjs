import test from 'node:test';
import assert from 'node:assert/strict';
import {sceneHTML,example,STYLE_IDS,PALETTE_IDS,LAYOUT_IDS,validateScene,portraitRect} from '../assets/studio.mjs';
test('36 standard combinations render actual scene objects',()=>{
  for(const style_id of STYLE_IDS)for(const palette_id of PALETTE_IDS)for(const layout of LAYOUT_IDS){
    const c={...example,style_id,palette_id,layout};const html=sceneHTML(c,3,{demo:true});
    assert.ok(html.includes('data-style="'+style_id+'"'));assert.ok(html.includes('caption-line'));
    assert.ok(html.includes('data-layout="'+layout+'"'));assert.ok(!html.includes('真人原片'));
    if(layout==='compare')assert.ok(html.includes('compare-panel'));
    if(layout==='steps')assert.ok(html.includes('step-number'));
  }
});
test('objects change over time, no whole-poster-only motion',()=>{
  for(const style_id of STYLE_IDS){const c={...example,style_id};assert.notEqual(sceneHTML(c,.3),sceneHTML(c,3));assert.ok(sceneHTML(c,.3).includes('opacity:0;translate:0 26px'));}
});
test('long captions are rejected, never shrunk',()=>assert.throws(()=>validateScene({...example,caption_lines:['字'.repeat(15)]})));
test('wrong style or palette is rejected',()=>assert.throws(()=>validateScene({...example,palette_id:'paper-red'})));
test('HTML payload is escaped and outside images are refused',()=>{
  const html=sceneHTML({...example,title:['<x>','测试']},3);assert.ok(html.includes('&lt;x&gt;'));assert.ok(!html.includes('<x>'));
  assert.throws(()=>sceneHTML(example,3,{portrait:'https://example.com/x.png'}));
});
test('two-line captions retain spoken words and semantic highlight',()=>{
  const html=sceneHTML({...example,caption_lines:['把知识打包','变成 AI Skill']},3);assert.equal((html.match(/caption-line check-text/g)||[]).length,2);assert.ok(html.includes('<em>AI Skill</em>'));
});
test('video portrait positions match the three distinct masters',()=>{
  assert.equal(portraitRect('tactile').width,198);assert.equal(portraitRect('editorial').width,265);assert.equal(portraitRect('precision').width,165);
});
