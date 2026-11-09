import React,{useContext} from 'react';
import {AbsoluteFill,Img,staticFile} from 'remotion';
import {SceneContext} from './RuntimeContext';
import {sec,lin} from './vox';
export const ScreenScene=()=>{const s=useContext(SceneContext)?.screen;if(!s)throw Error('Screen scenes require an original image and measured focus rectangle.');const t=sec(),u=.5-.5*Math.cos(Math.PI*lin(t,.85,1.4));const [x,y,w,h]=s.focus,base=1920/s.width;
 const target=Math.min(1250/(w*base),500/(h*base),7),scale=1+(target-1)*u,fx=(x+w/2)*base,fy=(y+h/2)*base,tx=u*(1160-fx)-(scale-1)*fx,ty=u*(535-fy)-(scale-1)*fy;
 return <AbsoluteFill style={{background:'#e5e9e6',fontFamily:'Han',overflow:'hidden'}}><div style={{position:'absolute',left:530*u,top:240*u,width:1920-620*u,height:1080-480*u,overflow:'hidden',borderRadius:18*u,boxShadow:'0 20px 60px #243b4a30'}}><Img src={staticFile(s.asset)} style={{position:'absolute',width:1920,height:s.height*base,left:tx-530*u,top:ty-240*u,transform:`scale(${scale})`,transformOrigin:'0 0'}}/></div>
 <div style={{position:'absolute',left:70,top:80,opacity:u,color:'#243747'}}><div style={{fontSize:30,color:'#8571b1'}}>完整界面 → 目标位置</div><div style={{fontSize:82,fontWeight:900,marginTop:20}}>{s.name}</div></div><div style={{position:'absolute',right:100,top:50,background:'#243747',color:'#fffaf0',padding:'16px 30px',fontSize:42,fontWeight:900,opacity:1-u}}>{s.name}</div>
 <div style={{position:'absolute',left:70,top:395,width:420,height:420*s.height/s.width,opacity:u,border:'3px solid #819ba6',borderRadius:10,overflow:'hidden'}}><Img src={staticFile(s.asset)} style={{width:'100%'}}/><div style={{position:'absolute',left:x*420/s.width,top:y*420/s.width,width:w*420/s.width,height:h*420/s.width,border:'3px solid #8571b1'}}/></div></AbsoluteFill>};
