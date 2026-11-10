import React from 'react';
import {AbsoluteFill,OffthreadVideo,Img,staticFile} from 'remotion';
import recipes from './human-recipes.json';
import {C,Fonts,ease,mix,tnow} from './Kit';
const LEFT=140,WIDTH=740;
type Row=[string,string];
const initial:Record<string,Row[]>={IntroHuman:[['同一个','窗口'],['别','聊到底']],ClarifyHuman:[['大模型',''],['偷偷','降智？']],MisconceptionHuman:[['它真的',''],['有','记忆吗？']],MemoryQuestionHuman:[['每天都聊，',''],['它还','记得？']],CapacityHuman:[['','容量上限']],ManageHuman:[['管理','上下文']],WatchHuman:[['同一个','窗口'],['也别','硬聊']],SummaryHuman:[['模型',''],['不主动','记忆']],ClosingHuman:[['交接，','更靠谱']]};
const support=(key:string,s:any)=>key==='MisconceptionHuman'?'聊过的话，\n是怎么接上的？':key==='SummaryHuman'?'前文，需要随请求\n一起带入':s.foot||'';
function titleRows(key:string,s:any,index:number):Row[]{
 if(s.kind==='cta')return [['','点赞 · 关注'],['来评论区','聊聊']];
 if(s.kind==='hero')return [['','下期见']];
 if(key==='A-Human')return s.rows;
 return index===0?initial[key]:s.lines.map((v:string)=>['',v]);
}
export const Human=({clip}:any)=>{
 const t=tnow(),key=clip.source_key,isA=key==='A-Human';
 const rec:any=(recipes.examples as any[]).find(x=>x.variant===key)||{};
 const states:any[]=isA?[
  {at:0,kind:'side',eyebrow:'要求跟丢了，工作就开始跑偏',rows:[['详细要求',''],['明明','说过了']]},
  {at:2.28,kind:'side',eyebrow:'提醒一次，补回一项',rows:[['刚提醒，',''],['又','忘了']]},
  {at:7.32,kind:'side',eyebrow:'修好这里，那里又遗漏',rows:[['补回这项，',''],['另一项','又丢了']]}
 ]:[{...rec,at:0},...(rec.beats||[]).map((b:any)=>({...rec,...b}))];
 return <AbsoluteFill style={{fontFamily:'Han',color:C.cream}}>
  <Fonts/>
  <div style={{position:'absolute',inset:0,background:'linear-gradient(90deg,#171526aa,transparent 60%)'}}/>
  {states.map((s,index)=>{
   const at=s.at,next=states[index+1]?.at??10000;
   if(t<at||t>next+.2)return null;
   const enter=ease(t,at,.25),leave=ease(t,next-.18,.18);
   const punch=s.kind==='punch'||s.kind==='hero';
   const travel=punch?ease(t,at+(s.kind==='hero'?.02:.22),s.kind==='hero'?.38:.88):1;
   const rows=titleRows(key,s,index),foot=support(key,s),eyebrow=s.kind==='cta'?'喜欢这期内容':s.eyebrow;
   return <div key={index} style={{position:'absolute',inset:0,opacity:enter*(1-leave),transform:`translateY(${-leave*12}px)`}}>
    {eyebrow&&<div style={{position:'absolute',left:LEFT,top:185,width:WIDTH,fontSize:36,lineHeight:1.5,letterSpacing:2,color:'#e9deee'}}>{eyebrow}</div>}
    <div style={{position:'absolute',left:punch?mix(690,LEFT,travel):LEFT,top:punch?mix(360,285,travel):285,textAlign:'left',transform:`translateY(${(1-enter)*18}px)`}}>
     {rows.map(([normal,focus],i)=>{
      const fit=Math.min(1,WIDTH/(normal.length*88+focus.length*136));
      const normalSize=punch?mix(165,88*fit,travel):88*fit;
      const focusSize=punch?mix(218,136*fit,travel):136*fit;
      return <div key={i} style={{whiteSpace:'nowrap',lineHeight:1.24,marginBottom:rows.length>1?12:0}}><span style={{fontFamily:'Song',fontSize:normalSize,fontWeight:650}}>{normal}</span><strong style={{fontFamily:'Han',fontSize:focusSize,fontWeight:900,color:C.gold,textShadow:'0 4px 20px #17152660'}}>{focus}</strong></div>;
     })}
    </div>
    {foot&&<div style={{position:'absolute',left:LEFT,top:rows.length>1?695:505,width:WIDTH,fontSize:43,lineHeight:1.65,letterSpacing:2,whiteSpace:'pre-line',color:'#f2eaf4',opacity:ease(t,at+(punch?1.2:.45),.4)}}>{foot}</div>}
    {s.kind==='cta'&&<div style={{position:'absolute',left:LEFT,top:690,fontSize:40,color:C.gold,letterSpacing:26}}>♡　＋　···</div>}
   </div>;
  })}
  {key==='MemoryQuestionHuman'&&<div style={{position:'absolute',left:LEFT,top:670,width:WIDTH}}>{['doubao','workbuddy','deepseek'].map((name,i)=><div key={name} style={{display:'flex',alignItems:'center',gap:24,marginBottom:26,opacity:ease(t,2.52+i*.35,.3),transform:`translateX(${(1-ease(t,2.52+i*.35,.5))*-28}px)`}}><Img src={staticFile('side-'+name+'.png')} style={{width:62,height:62,objectFit:'contain',borderRadius:14}}/><span style={{fontSize:44,lineHeight:1.35,letterSpacing:1}}>{['豆包','WorkBuddy','DeepSeek'][i]}</span></div>)}</div>}
  {key==='IntroHuman'&&<div style={{position:'absolute',left:LEFT,top:560,width:WIDTH}}>{['忘要求','理解跑偏','速度变慢'].map((s,i)=><div key={s} style={{display:'flex',alignItems:'center',gap:24,marginBottom:24,fontSize:43,lineHeight:1.4,opacity:ease(t,4.13+i*.28,.3),transform:`translateX(${(1-ease(t,4.13+i*.28,.4))*-24}px)`}}><span style={{width:28,height:3,background:C.gold}}/>{s}</div>)}</div>}
  {rec.meter&&<div style={{position:'absolute',left:LEFT,top:key==='WatchHuman'?720:650,width:WIDTH,opacity:ease(t,.55,.35)}}>
   <div style={{display:'flex',gap:8}}>{Array.from({length:21},(_,i)=><div key={i} style={{width:24,height:38,borderRadius:4,background:i/21<mix(rec.meter.from,rec.meter.to,ease(t,rec.meter.at,4))?C.gold:'#ffffff26'}}/>)}</div>
   <div style={{fontSize:39,lineHeight:1.5,marginTop:30,color:C.cream}}>{rec.meter.value&&t>=rec.meter.value_at?<div style={{display:'flex',gap:28,alignItems:'baseline'}}><strong style={{fontSize:92,color:C.gold}}>70%</strong><span style={{fontSize:34}}>原案例个人经验</span></div>:'内容增加，逐渐接近边界'}</div>
  </div>}
  {isA&&<div style={{position:'absolute',left:LEFT,top:675,width:670}}>{['关键信息','指定风格','之前要求'].map((s,i)=>{const drop=i===0?ease(t,2.28)*(1-ease(t,3.77)):i===2?ease(t,7.32):0;return <div key={s} style={{display:'flex',gap:25,alignItems:'center',fontSize:44,lineHeight:1.35,borderBottom:'1px solid #fff3',padding:'10px 0',marginBottom:8,opacity:1-drop,transform:`translate(${drop*60}px,${drop*60}px) rotate(${drop*4}deg)`}}><span style={{fontSize:32,color:C.gold}}>0{i+1}</span>{s}<span style={{marginLeft:'auto',color:C.gold}}>✓</span></div>})}</div>}
  {isA&&t>=8.3&&<div style={{position:'absolute',left:LEFT,top:870,fontSize:38,color:C.gold,opacity:ease(t,8.3)}}>◌ 等待处理中…</div>}
 </AbsoluteFill>;
};
