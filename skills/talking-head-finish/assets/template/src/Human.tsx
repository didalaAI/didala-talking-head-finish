import React from 'react';
import {AbsoluteFill,Img,staticFile} from 'remotion';
import {sec,p,lin} from './vox';
import {SceneSpec} from './RuntimeContext';
const white='#fcfaff',lav='#dfd4ff',gold='#e8c794',muted='#b2aabd';
const enter=(t:number,at=0):React.CSSProperties=>({opacity:p(t,at,.15),translate:`0 ${(1-p(t,at,.55))*45}px`});
const measure=(s:string,max=710)=>Math.min(126,max/Math.max(1,Array.from(s).reduce((n,c)=>n+(/[\x00-\x7f]/.test(c)?.55:1),0)));
const Rule=({t,w=600}:{t:number;w?:number})=><div style={{height:5,width:w*p(t,.45,.75),background:lav}}/>;
const Side=({t,lines,eyebrow,foot}:{t:number;lines:string[];eyebrow?:string;foot?:string})=><div style={{position:'absolute',left:105,top:180,width:740}}>
 <div style={{fontSize:38,fontWeight:700,color:lav,letterSpacing:2,lineHeight:1.45,...enter(t)}}>{eyebrow}</div>
 {lines.map((s,i)=><div key={i} style={{fontSize:Math.min(i?116:126,measure(s)),fontWeight:900,lineHeight:1.15,letterSpacing:'-.02em',marginTop:i?17:30,color:i?lav:white,...enter(t,.12+i*.16)}}>{s}</div>)}
 <div style={{marginTop:34}}><Rule t={t} w={Math.min(610,(lines[lines.length-1]||'').length*82)}/></div>
 {foot&&<div style={{fontSize:38,fontWeight:700,lineHeight:1.45,marginTop:30,color:white,...enter(t,.65)}}>{foot}</div>}
 </div>;
const Punch=({t,lines,eyebrow,foot}:{t:number;lines:string[];eyebrow?:string;foot?:string})=>{const e=p(t,1.05,.75),word=lines.join('');return <>
 <div style={{position:'absolute',left:75+30*e-(1-p(t,0,.45))*600,top:490-200*e,width:1790,fontSize:Math.min(230-110*e,1750/Math.max(1,word.length)),fontWeight:900,color:lav,whiteSpace:'nowrap',letterSpacing:'-.02em',lineHeight:1.15,textShadow:'0 5px 22px #16112055'}}>{word}</div>
 <div style={{position:'absolute',left:110,top:180,fontSize:38,fontWeight:700,color:lav,opacity:p(t,.1)}}>{eyebrow}</div>
 {foot&&<div style={{position:'absolute',left:110,top:505,width:685,opacity:p(t,1.65,.3)}}><Rule t={10}/><div style={{fontSize:40,fontWeight:700,lineHeight:1.45,marginTop:28}}>{foot}</div></div>}
 </>};
/** Nine approved presenter compositions share the original side/punch primitives,
 * but their stage changes, tags and meters are authored against this episode's speech. */
export const Human=({scene}:{scene:SceneSpec})=>{
 const t=sec(),duration=scene.frames/60,variant=scene.variant||scene.id;
 const basePunch=scene.kind==='punch'||['CapacityHuman','ManageHuman'].includes(variant);
 const beats=scene.beats||[];const beat=[...beats].reverse().find(b=>t>=b.at);
 const local=t-(beat?.at||0),lines=beat?.lines||scene.lines||['本期重点'],eyebrow=beat?.eyebrow??scene.eyebrow,foot=beat?.foot??scene.foot;
 const style=beat?.kind||(basePunch?'punch':'side');
 const tagAt=scene.tags_at??duration*.42,tagList=variant==='MemoryQuestionHuman'||scene.tag_layout==='list';
 const meter=scene.meter;const meterAt=meter?.at??duration*.18;
 const from=meter?.from??.35,to=meter?.to??1,progress=from+(to-from)*lin(t,meterAt,Math.max(.5,duration-meterAt-.4));
 return <AbsoluteFill style={{fontFamily:'Han',color:white}}>
 {style==='punch'?<Punch t={local} lines={lines} eyebrow={eyebrow} foot={foot}/>:style==='hero'?<div style={{position:'absolute',left:75,top:430,fontSize:Math.min(240,1750/Math.max(1,lines.join('').length)),fontWeight:900,color:lav,whiteSpace:'nowrap',translate:`${(1-p(local,0,.25))*-550}px 0`}}>{lines.join('')}</div>:style==='cta'?<div style={{position:'absolute',left:105,top:210,width:1550,display:'flex',gap:34}}>{lines.map((s,i)=><div key={i} style={{fontSize:Math.min(86,measure(s,430)),fontWeight:900,...enter(local,i*.12)}}>{s}</div>)}</div>:<Side t={local} lines={lines} eyebrow={eyebrow} foot={foot}/>}
 {Boolean(scene.tags?.length)&&<div style={{position:'absolute',left:113,top:tagList?505:532,width:660,display:tagList?'block':'flex',gap:28}}>{scene.tags!.map((tag,i)=>{const step=Math.min(tagList ? .55 : .35,duration*.45/Math.max(1,scene.tags!.length-1));const at=tag.at??tagAt+i*step;return <div key={i} style={{...enter(t,at),display:tagList?'flex':'block',alignItems:'center',gap:22,marginBottom:tagList?18:0}}>
 {tag.asset&&<Img src={staticFile(tag.asset)} style={{width:62,height:62,objectFit:'contain'}}/>}
 <div><div style={{fontSize:tagList?38:36,fontWeight:700,color:tag.color||(i===scene.tags!.length-1?gold:lav)}}>{tag.text}</div>{!tagList&&<div style={{marginTop:10,height:4,width:(1-.55*p(t,at+.32))*145,background:tag.color||lav}}/>}</div>
 </div>})}</div>}
 {meter&&<div style={{position:'absolute',left:115,top:meter.value!==undefined&&t>=(meter.value_at??duration*.65)?meter.value_y??meter.y??455:meter.y??665,width:610,opacity:p(t,meterAt,.3)}}>
 {meter.value!==undefined&&t>=(meter.value_at??duration*.65)?<><div style={{fontSize:meter.value_size??180,fontWeight:900,lineHeight:1.05,color:gold}}>{meter.value}<span style={{fontSize:72}}>{meter.unit||''}</span></div><div style={{fontSize:34,fontWeight:700,marginTop:15}}>{meter.label}</div></>:<><div style={{height:14,background:'#dfd4ff33',position:'relative'}}><div style={{height:14,width:610*Math.max(0,Math.min(1,progress)),background:lav}}/><div style={{position:'absolute',right:0,top:-12,width:3,height:40,background:gold}}/></div>{meter.label&&<div style={{fontSize:31,fontWeight:700,color:muted,marginTop:21}}>{meter.label}</div>}</>}
 </div>}
 </AbsoluteFill>;
};
