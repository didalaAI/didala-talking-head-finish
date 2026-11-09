import React from 'react';
import {AbsoluteFill} from 'remotion';
import {sec,p} from './vox';
import {SceneSpec} from './RuntimeContext';
// V4's side/punch typography, with episode words passed by the authored plan.
export const Human=({scene}:{scene:SceneSpec})=>{const t=sec(),e=p(t,1.05,.75),lines=scene.lines||['把重点','讲清楚'];return <AbsoluteFill style={{fontFamily:'Han',color:'#fcfaff'}}>
 <div style={{position:'absolute',left:110,top:180,fontSize:38,fontWeight:700,color:'#dfd4ff',opacity:p(t,0,.2)}}>{scene.eyebrow}</div>
 {scene.kind==='punch'?<div style={{position:'absolute',left:75+30*e-(1-p(t,0,.45))*600,top:490-200*e,fontSize:230-110*e,fontWeight:900,color:'#dfd4ff',whiteSpace:'nowrap',letterSpacing:'-.02em',lineHeight:1.15}}>{lines.join('')}</div>:<div style={{position:'absolute',left:105,top:245,width:740}}>{lines.map((s,i)=><div key={i} style={{fontSize:Math.min(i?116:126,710/Array.from(s).reduce((n,c)=>n+(/[\x00-\x7F]/.test(c)?.55:1),0)),fontWeight:900,lineHeight:1.15,letterSpacing:'-.02em',marginTop:i?17:0,color:i?'#dfd4ff':'#fcfaff',opacity:p(t,.12+i*.16,.2),translate:`0 ${(1-p(t,.12+i*.16,.55))*45}px`}}>{s}</div>)}</div>}
 {scene.foot&&<div style={{position:'absolute',left:110,top:scene.kind==='punch'?505:600,width:685,fontSize:38,fontWeight:700,opacity:p(t,scene.kind==='punch'?1.65:.65,.3)}}><div style={{height:5,width:600*p(t,.45,.75),background:'#dfd4ff',marginBottom:28}}/>{scene.foot}</div>}
 </AbsoluteFill>};
