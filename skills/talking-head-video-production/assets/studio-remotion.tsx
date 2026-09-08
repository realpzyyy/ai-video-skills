import React from 'react';
import {AbsoluteFill, Composition, useCurrentFrame, useVideoConfig} from 'remotion';
import {Video} from '@remotion/media';
import {sceneHTML, example, portraitRect} from './studio.mjs';
import './studio.css';

// source is an already authorized local/staticFile video, never a generated face.
// Put a single scene into a Sequence in the host's confirmed edit timeline.
export const StandardScene = ({config=example, demo=false, portrait='', source='', trimBefore=0, showCaption=true}) => {
  const frame=useCurrentFrame(); const {fps,width,height}=useVideoConfig();
  if(width*16!==height*9) throw Error('Standard master is 9:16; adapt and approve another aspect ratio first');
  const rect=portraitRect(config.style_id,config.layout);
  const time=frame/fps;
  return <AbsoluteFill style={{background:'#eee'}}>
    <div style={{position:'absolute',width:720,height:1280,transform:`scale(${width/720})`,transformOrigin:'0 0'}}>
      <div className={showCaption?'':'caption-hidden'} dangerouslySetInnerHTML={{__html:sceneHTML(config,time,{portrait,demo})}} />
      {source ? <div style={{position:'absolute',...rect,overflow:'hidden',opacity:time>config.duration_seconds-.25?Math.max(0,(config.duration_seconds-time)/.25):1}}>
        <Video src={source} trimBefore={trimBefore} muted style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:'center 20%'}} />
      </div> : null}
    </div>
  </AbsoluteFill>;
};
// Importing the reusable component never registers a second Remotion root.
export const StudioRoot=()=> <Composition id="StandardScene" component={StandardScene} width={720} height={1280} fps={30} durationInFrames={180} defaultProps={{config:example,demo:true}} calculateMetadata={({props})=>({durationInFrames:Math.ceil(props.config.duration_seconds*30)})}/>;
