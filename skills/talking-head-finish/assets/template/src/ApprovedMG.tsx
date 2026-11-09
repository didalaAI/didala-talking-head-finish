import React from 'react';
import {AbsoluteFill,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {D,T,Grain,p,lin,TickMarks,Screw,PaperRoll,MailFold} from './CompareKit';
import {SceneContext} from './RuntimeContext';

const ink='#2c292c',red='#a5483b';
const defaultRows=['保留原声原速','字幕清楚易读','动画讲明文意','突出文案重点','不同形式交替'];
const defaultParts=[
 {sub:'本轮问题',title:'优化文字设计',at:3,color:red},
 {sub:'第一轮提问',title:'剪好口播',at:7.8,color:'#6d6374'},
 {sub:'第一轮回复',title:'字幕已对齐',at:10,color:'#6c706b'},
 {sub:'第二轮提问',title:'加解释动画',at:11.67,color:'#6d6374'},
 {sub:'第二轮回复',title:'分镜已完成',at:13.2,color:'#6c706b'},
];
const Copy=React.createContext({rows:defaultRows,parts:defaultParts});
const useCopy=()=>React.useContext(Copy);
type Palette={bg:string;fg:string;muted:string;accent:string;metal:string;edge:string;surface:string;dark:boolean};
const palettes:Record<string,Palette>={
 pearl:{bg:'#efede7',fg:'#302c30',muted:'#7c7376',accent:'#9c5b46',metal:'linear-gradient(130deg,#fffef7,#b8b5b4 46%,#f4f1e9 75%,#c5beb8)',edge:'#c7beb4',surface:'#e3ded4',dark:false},
 plum:{bg:'#29232e',fg:'#f3ece7',muted:'#bdb0c0',accent:'#d0afc2',metal:'linear-gradient(135deg,#f7ece8,#918294 45%,#dfcbd6 77%,#6c6278)',edge:'#c4aebe',surface:'#3c3345',dark:true},
};
const LogoLine=({label,color,fg}:{label:string;color:string;fg:string})=>{const scene=React.useContext(SceneContext);return <><D x={110} y={68}><T size={27} color={color} weight={700} style={{letterSpacing:4}}>{scene?.eyebrow||("上下文窗口 / "+label)}</T></D><D x={110} y={119} w={1700} h={2} style={{background:fg,opacity:.13}}/><D x={1630} y={62}><T size={28} color={color} weight={700}>读懂 AI</T></D></>};
const Note=({t,at=6.3,children,color=red}:{t:number;at?:number;children:React.ReactNode;color?:string})=>{const scene=React.useContext(SceneContext);return <D x={110} y={863} style={{opacity:p(t,at),translate:`0 ${16*(1-p(t,at))}px`}}><T size={42} color={color} weight={700}>{scene?.foot||children}</T></D>};
const EpisodeTitle=({children,size,color}:{children:React.ReactNode;size:number;color?:string})=>{const scene=React.useContext(SceneContext);return <T size={size} color={color}>{scene?.title||children}</T>};
const Binder=({w=105,color=ink}:{w?:number;color?:string})=><svg width={w} height={w*1.02} viewBox="0 0 110 112" style={{filter:'drop-shadow(0 6px 5px #201b2130)'}}><path d="M17 65h76l12 43H5Z" fill={color}/><path d="M29 68V18c0-15 52-15 52 0v50M36 68V22c0-7 38-7 38 0v46" fill="none" stroke="#c9c8c2" strokeWidth="5"/><path d="M7 106h96" stroke="#706e70" strokeWidth="3"/></svg>;
const Gear=({t,size=145}:{t:number;size?:number})=><div style={{width:size,height:size,rotate:`${t*48}deg`,filter:'drop-shadow(0 9px 6px #211c2333)'}}><svg width={size} height={size} viewBox="0 0 120 120"><path d="M48 0h24l4 15 13 8 15-4 12 21-11 11v17l11 11-12 21-15-4-13 8-4 15H48l-4-15-13-8-15 4L4 79l11-11V51L4 40l12-21 15 4 13-8Z" fill="#75675c" stroke="#e1d1b9" strokeWidth="3"/><circle cx="60" cy="60" r="29" fill="#c4b293" stroke="#51463e" strokeWidth="4"/><path d="M40 60h40M60 40v40" stroke="#51463e" strokeWidth="4"/></svg></div>;
const PaperCard=({i,scale=1}:{i:number;scale?:number})=>{const {parts}=useCopy();const s=parts[i];return <div style={{width:400,height:195,padding:'24px 28px',background:i===0?'#f2d6c4':'#fff5df',boxSizing:'border-box',borderTop:`7px solid ${s.color}`,borderRadius:3,boxShadow:'0 16px 26px #36281e26',transform:`scale(${scale})`,transformOrigin:'left top'}}><T size={29} color={s.color} weight={700}>{s.sub}</T><T size={44} color={ink} style={{marginTop:22,whiteSpace:'nowrap'}}>{s.title}</T><div style={{height:2,background:'#d6c7af',width:300,marginTop:19}}/></div>};

export const PaperCapacity=({t}:{t:number})=>{const {rows}=useCopy();const feed=lin(t,2.5,7.6);return <AbsoluteFill style={{background:'#e9dfcd'}}><Grain/>
 <D x={-70} y={755} w={2100} h={450} style={{background:'#cabb9f',rotate:'-4deg',boxShadow:'0 -7px 24px #6b5c4c22'}}/>
 <LogoLine label="纸艺 · 单次读取的边界" color={red} fg={ink}/>
 <D x={110} y={160}><EpisodeTitle size={102} color={ink}>一整卷内容，<span style={{color:red}}>只读入一段。</span></EpisodeTitle></D>
 <D x={1570} y={262} w={200} h={58} style={{background:'#d7c8ad',rotate:'8deg'}}/>
 <D x={160} y={367}><PaperRoll t={t}/></D><D x={1598} y={367}><PaperRoll t={-t}/></D>
 <D x={242} y={398} w={1420} h={300} style={{background:'#faf2df',overflow:'hidden',boxShadow:'0 22px 28px #42352e22'}}>
  <D x={42-feed*590} y={52} w={2200}>{[...rows,...rows.slice(0,2)].map((s,i)=><D key={i} x={i*345} y={i%2?111:0} w={355} style={{rotate:`${i%2?1.2:-1.2}deg`}}><T size={43} color={i%2?red:ink} style={{whiteSpace:'nowrap'}}>{s}</T><div style={{height:4,width:260,background:i%2?red:ink,opacity:.15,marginTop:23}}/></D>)}</D>
  <D x={0} y={0} w={400} h={300} style={{background:'#b8ad9855'}}/><D x={1055} y={0} w={370} h={300} style={{background:'#b8ad9855'}}/>
 </D>
 <D x={610} y={330} w={710} h={435} style={{border:'41px solid #373333',borderRadius:9,boxSizing:'border-box',boxShadow:'12px 18px 21px #32282d30',pointerEvents:'none'}}>
  <D x={8} y={-35}><T size={29} color='#fff2dd' weight={700}>本轮能读取的部分</T></D>
  <D x={17+480*lin(t,3.5,6.6)} y={10} w={5} h={325} style={{background:'#ad5c46',opacity:.65,boxShadow:'0 0 20px #a9554255'}}/>
 </D>
 <D x={1250} y={712}><Binder w={89}/></D><D x={1492} y={693}><Gear t={t}/></D>
 <D x={1742} y={387} style={{rotate:'90deg',transformOrigin:'left top'}}><TickMarks w={310}/></D>
 <Note t={t} at={6.5}>读取范围有限，这就是「上下文窗口」。</Note>
 </AbsoluteFill>};

const IntroRounds=({t,color,fg}:{t:number;color:string;fg:string})=><D x={240} y={340} w={1480} h={390} style={{opacity:1-p(t,2.72,.28),translate:`0 ${-20*p(t,2.7)}px`}}>{[1,2,3].map((n,i)=><D key={i} x={i*500} y={35*(1-p(t,.05+i*.8))} style={{opacity:p(t,.05+i*.8)}}><T size={168} color={i===2?color:fg} style={{opacity:i===2?1:.28}}>0{n}</T><T size={39} color={i===2?color:fg} weight={700} style={{marginTop:18}}>第{n}轮对话</T>{i<2&&<D x={330} y={90}><T size={80} color={fg} style={{opacity:.25}}>→</T></D>}</D>)}</D>;
export const PaperPacket=({t}:{t:number})=>{const {parts}=useCopy();const pack=p(t,15.1,1.3),send=p(t,17.05,1.4),flap=p(t,16.2,.75);return <AbsoluteFill style={{background:'#ece3d0'}}><Grain/>
 <D x={-35} y={810} w={2050} h={400} style={{background:'#c7b493',rotate:'-3deg',boxShadow:'0 -10px 25px #5b483b22'}}/>
 <LogoLine label="纸艺 · 前两轮也被带上" color={red} fg={ink}/><D x={110} y={164}><EpisodeTitle size={100} color={ink}>每一轮，<span style={{color:red}}>都带上前情。</span></EpisodeTitle></D>
 {t<3.1&&<IntroRounds t={t} color={red} fg={ink}/>}
 <D x={0} y={0} style={{translate:`${230*send}px ${-18*send}px`}}>
 {parts.map((s,i)=>{const x=i===0?755:i<3?245:1275,y=i===0?330:415+(i%2?0:225),a=p(t,s.at);return <D key={i} x={x+(745-x)*pack} y={y+(418+i*14-y)*pack+145*p(t,16.15,.8)} style={{opacity:a,translate:`${(1-a)*(i<3?-85:85)}px ${(1-a)*35}px`,rotate:`${(i-2)*2.5*(1-pack)}deg`,scale:String(1-.1*pack),zIndex:5-i}}><PaperCard i={i}/></D>})}
 <D x={716} y={450} w={500} h={340} style={{opacity:p(t,15.5),perspective:1500,zIndex:8}}>
  <D x={0} y={100} style={{filter:'drop-shadow(0 20px 18px #42312325)'}}><svg width="520" height="255" viewBox="0 0 520 255"><rect width="520" height="255" fill="#dac2a0"/><path d="M0 0 260 160 520 0v255H0Z" fill="#e3cfad"/><path d="M0 255 260 95 520 255" fill="#f0dfc1" stroke="#c7ac86" strokeWidth="2"/></svg></D>
  <D x={0} y={100} style={{transformOrigin:'center top',transform:`rotateX(${(1-flap)*180}deg)`,backfaceVisibility:'visible'}}><svg width="520" height="160" viewBox="0 0 520 160"><path d="M0 0 260 160 520 0Z" fill="#e8d3b3" stroke="#c3a681" strokeWidth="2"/></svg></D>
  <D x={99} y={301}><T size={33} color={red}>本轮问题 ＋ 历史</T></D>
  <D x={225} y={232} style={{opacity:p(t,17.1),scale:String(1.3-.3*p(t,17.1))}}><div style={{width:70,height:56,borderRadius:'50%',background:red,display:'grid',placeItems:'center',boxShadow:'0 6px 9px #5b342b22'}}><T size={25} color='#fff3df'>再读</T></div></D>
 </D>
 <D x={918} y={318-145*(1-p(t,15.15))+150*p(t,16.15,.8)} style={{opacity:p(t,15.15)*(1-p(t,16.75,.4)),zIndex:9,rotate:'-4deg'}}><Binder w={110}/></D>
 </D>
 <D x={130} y={770}><TickMarks w={480}/></D><D x={1570} y={755}><Gear t={t*.5} size={100}/></D>
 <Note t={t} at={16.65}>前文重新打包，随这次问题一起送入。</Note>
 </AbsoluteFill>};

const Reader=({t,c,w=690,h=460,reading=false,feed=0}:{t:number;c:Palette;w?:number;h?:number;reading?:boolean;feed?:number})=>{const {rows,parts}=useCopy();return <div style={{position:'relative',width:w,height:h,background:c.metal,borderRadius:38,border:`3px solid ${c.edge}`,boxShadow:`18px 35px 55px ${c.dark?'#09070e66':'#4d43472b'},inset 1px 1px 2px #fff8`,boxSizing:'border-box'}}>
 <D x={30} y={30} w={w-60} h={h-130} style={{borderRadius:20,background:'#28252c',padding:18,boxSizing:'border-box',boxShadow:'inset 0 5px 18px #0009'}}>
  <D x={18} y={18} w={w-96} h={h-166} style={{borderRadius:9,overflow:'hidden',background:'#f4ebdc'}}>
   {reading?<><D x={32} y={27}><T size={27} color={c.accent} weight={700}>{t<16.8?'本轮输入 · 准备中':'本轮输入已齐'}</T><T size={t<16.8?42:45} color={ink} style={{marginTop:18}}>{t<16.8?'等待问题与历史':'当前问题'}</T><T size={34} color={ink} weight={700} style={{marginTop:13}}>{t<16.8?`${parts.filter(s=>t>s.at).length} / 5 份内容`:'＋ 前两轮问答'}</T></D><D x={28} y={h-215} w={(w-155)*lin(t,17.25,1.3)} h={5} style={{background:c.accent}}/></>:
   <><D x={32-feed*560} y={52} w={1850} style={{display:'flex',gap:68,alignItems:'center'}}>{rows.map((s,i)=><div key={s} style={{width:230,flexShrink:0}}><T size={42} color={ink} style={{lineHeight:1.45}}>{s.slice(0,2)}<br/>{s.slice(2)}</T><div style={{width:185,height:4,background:c.accent,opacity:.6,marginTop:20}}/></div>)}</D><D x={25+(w-165)*lin(t,3.4,7.2)} y={0} w={5} h={h-166} style={{background:c.accent,opacity:.6,boxShadow:`0 0 30px 12px ${c.accent}33`}}/></>}
   <D x={0} y={0} w={w-96} h={h-166} style={{background:'linear-gradient(130deg,#ffffff20,transparent 48%,#ffffff10)',pointerEvents:'none'}}/>
  </D>
  {!reading&&<D x={0} y={0} w={(w-60)*(1-p(t,1.7,1.4))} h={h-130} style={{background:c.metal,borderRight:`5px solid ${c.edge}`,boxShadow:'8px 0 12px #0004'}}/>}
 </D>
 <D x={48} y={h-76}><T size={31} color={c.dark?'#29252e':'#5c514d'} weight={700}>{reading?'AI · 本轮重新读取':'一次读取范围'}</T></D>
 <D x={w-96} y={h-72} w={25} h={25} style={{borderRadius:'50%',background:c.accent,boxShadow:`0 0 15px ${c.accent}66`}}/>
 {[[14,14],[w-42,14],[14,h-42],[w-42,h-42]].map(([x,y],i)=><D key={i} x={x} y={y}><Screw size={23}/></D>)}
 </div>};
const Conveyor=({t,c,w=1250}:{t:number;c:Palette;w?:number})=><D x={0} y={0} w={w} h={110} style={{background:c.surface,border:`3px solid ${c.edge}`,borderRadius:54,boxShadow:'0 25px 25px #0e0b172b',overflow:'hidden'}}><D x={30} y={28} w={w-60} h={52} style={{borderTop:`2px solid ${c.edge}`,borderBottom:`2px solid ${c.edge}`,opacity:.6}}/>{[0,w-108].map((x,i)=><D x={x+11} y={10} key={i}><div style={{width:86,height:86,borderRadius:'50%',background:c.metal,display:'grid',placeItems:'center',rotate:`${t*56}deg`,border:`2px solid ${c.edge}`}}><div style={{width:64,height:4,background:c.accent}}/></div></D>)}{Array.from({length:14},(_,i)=><D key={i} x={130+(i*77+t*65)%(w-250)} y={83} w={18} h={3} style={{background:c.edge,opacity:.7}}/>)}</D>;

export const MachineCapacity=({t,kind}:{t:number;kind:string})=>{const {rows,parts}=useCopy();const c=palettes[kind],central=kind==='plum',feed=lin(t,2.7,7.7),focus=p(t,6.5,2);return <AbsoluteFill style={{background:c.bg}}><Grain dark={c.dark}/>
 <D x={central?490:850} y={245} w={1050} h={660} style={{background:`radial-gradient(ellipse,${c.accent}1c,transparent 68%)`}}/>
 <LogoLine label={central?'单次输入 · 有限范围':'一次能读多少'} color={c.accent} fg={c.fg}/>
 <D x={110} y={157}><EpisodeTitle size={central?95:91} color={c.fg}>{central?'可读入的内容，有一道边界。':'一次，能读进多少？'}</EpisodeTitle></D>
 {central?<>
  <D x={200} y={360} w={1500} h={370} style={{opacity:p(t,.35),scale:String(.96+.04*p(t,1.3)),transformOrigin:'center'}}>
   <D x={30} y={240}><Conveyor t={t} c={c} w={1420}/></D>
   <D x={45-feed*230} y={82} w={1410} h={168} style={{background:'#c8b9c5',overflow:'hidden',transform:'rotateX(6deg)',boxShadow:'0 16px 20px #100b1c55'}}><D x={35-feed*390} y={50} w={2200} style={{display:'flex',gap:60}}>{[...rows,...rows].map((s,i)=><T key={i} size={36} color='#534653' style={{whiteSpace:'nowrap'}}>{s}</T>)}</D></D>
   <D x={392} y={-40} style={{scale:'1.03',transformOrigin:'top center'}}><Reader t={t} c={c} w={660} h={410} feed={feed}/></D>
  </D>
  <D x={110} y={741}><T size={31} color={c.muted} weight={700}>窗口之外</T><T size={49} color={c.muted} style={{marginTop:14}}>这次不会同时读入</T></D>
  <D x={1270} y={739} style={{opacity:p(t,3)}}><T size={31} color={c.accent} weight={700}>窗口之内</T><T size={49} color={c.fg} style={{marginTop:14}}>才参与本轮处理</T></D>
 </>:<>
  <D x={110} y={348} w={570}><T size={129} color={c.accent}>有限<span style={{fontSize:72,color:c.fg}}>的</span></T><T size={110} color={c.fg}>读取范围</T><D y={290} w={410} h={2} style={{background:'#b3a69b'}}/><T size={36} color={c.muted} weight={700} style={{marginTop:55}}>这次输入的内容<br/>需要放进同一个窗口。</T></D>
  <D x={770} y={684}><Conveyor t={t} c={c} w={1030}/></D>
  <D x={760} y={475} w={1050} h={195} style={{background:'#d5c7b7',rotate:'-4deg',overflow:'hidden',boxShadow:'0 15px 15px #4c404228'}}><D x={-50-feed*540} y={53} w={2200} style={{display:'flex',gap:70}}>{[...rows,...rows].map((s,i)=><T key={i} size={37} color='#837466' style={{whiteSpace:'nowrap'}}>{s}</T>)}</D></D>
  <D x={987} y={320} style={{scale:String(1+.04*p(t,6.5,2)),transformOrigin:'center'}}><Reader t={t} c={c} w={680} h={440} feed={feed}/></D>
 </>}
 <Note t={t} color={c.accent}>看得进多少，才处理多少。</Note>
 </AbsoluteFill>};

const Doc=({i,c,compact=false,narrow=false}:{i:number;c:Palette;compact?:boolean;narrow?:boolean})=>{const {parts}=useCopy();const s=parts[i];return <div style={{width:compact?(narrow?285:340):405,height:compact?145:181,padding:compact?'19px 24px':'24px 28px',boxSizing:'border-box',borderRadius:compact?10:7,background:i===0?(c.dark?'#e5c8af':'#e5c4b0'):'#f2eee4',borderLeft:`7px solid ${i===0?c.accent:'#9d939b'}`,boxShadow:'0 14px 24px #0a081b22'}}><T size={compact?25:28} color={i===0?'#8c4d37':'#7b6c7b'} weight={700}>{s.sub}</T><T size={compact?37:44} color={ink} style={{marginTop:compact?13:20,whiteSpace:'nowrap'}}>{s.title}</T></div>};

export const MachinePacket=({t,kind}:{t:number;kind:string})=>{const {rows,parts}=useCopy();const c=palettes[kind],central=kind==='plum',g=p(t,15.1,1.35),send=p(t,17.05,1.2),fade=p(t,2.8,.4);return <AbsoluteFill style={{background:c.bg}}><Grain dark={c.dark}/>
 <LogoLine label="第三轮 · 先前问答也随请求带入" color={c.accent} fg={c.fg}/>
 <D x={110} y={158}><EpisodeTitle size={90} color={c.fg}>{central?'前情汇合，重新读一遍。':'看似记得，是前文又被带上。'}</EpisodeTitle></D>
 {t<3.1&&<IntroRounds t={t} color={c.accent} fg={c.fg}/>}
 {central?<>
  <D x={590} y={362} w={740} h={450} style={{border:`2px solid ${c.accent}44`,borderRadius:'50%',opacity:fade,transform:'rotateX(24deg)'}}/>
  <D x={710} y={333} style={{opacity:fade,scale:String(.94+.06*p(t,3)),transformOrigin:'center'}}><Reader t={t} c={c} w={500} h={352} reading/></D>
  {parts.map((s,i)=>{const pos=[[790,705],[160,355],[160,585],[1420,355],[1420,585]][i];const x=pos[0]+(790-pos[0])*g,y=pos[1]+(426+i*13-pos[1])*g-120*send;return <D key={i} x={x} y={y} style={{opacity:p(t,s.at)*(1-p(t,16.55,.5)),scale:String(1-.25*g),translate:`0 ${30*(1-p(t,s.at))}px`,transformOrigin:'center',zIndex:7-i}}><Doc i={i} c={c} compact/></D>})}
  <D x={709} y={734} style={{opacity:p(t,16.6),translate:`0 ${-20*send}px`}}><T size={37} color={c.accent}>5 份内容，汇入同一次请求</T></D>
 </>:<>
  <D x={110} y={716} style={{opacity:fade}}><Conveyor t={t} c={c} w={1700}/></D>
  <D x={1170} y={365} style={{opacity:fade}}><Reader t={t} c={c} w={595} h={413} reading/></D>
  <D x={110} y={309} style={{opacity:fade}}><T size={29} color={c.muted} weight={700}>前两轮问答</T></D>
  {parts.map((s,i)=>{const pos=[[650,315],[110,510],[110,686],[555,510],[555,686]];const [x,y]=pos[i];
   const compact=i>0,tx=770,ty=465+i*13;return <D key={i} x={x+(tx-x)*g+(440)*send} y={y+(ty-y)*g} style={{opacity:p(t,s.at)*(1-p(t,17.2,.55)),scale:String((i===0?.94:1)-.24*g),translate:`${45*(1-p(t,s.at))}px 0`,transformOrigin:'left top',zIndex:8-i}}><Doc i={i} c={c} compact={compact}/></D>})}
  <D x={110} y={403} style={{opacity:g,background:c.bg,padding:'20px 0',width:525}}><T size={68} color={c.fg}>前两轮问答</T><T size={40} color={c.accent} weight={700} style={{marginTop:20}}>＋ 当前问题</T><T size={32} color={c.muted} weight={700} style={{marginTop:44}}>一起送入，重新读取。</T></D>
  <D x={730+430*send} y={655} style={{opacity:g*(1-p(t,17.3,.5)),translate:`0 ${20*(1-g)}px`}}><div style={{width:355,height:68,background:c.accent,borderRadius:7,display:'grid',placeItems:'center',boxShadow:'0 8px 18px #100b1c33'}}><T size={32} color={c.dark?'#28242c':'#fff4e6'}>本轮完整输入 · 5份</T></div></D>
 </>}
 <Note t={t} at={7.7} color={c.accent}>当前问题 ＋ 历史问答 → AI 本轮重新读取</Note>
 </AbsoluteFill>};


export const ApprovedMG=({id}:{id:string})=>{
 const scene=React.useContext(SceneContext);const {fps}=useVideoConfig();const f=useCurrentFrame();
 if(!['P2-Capacity','P2-Packet','W1-Capacity','W1-Packet','V1-Capacity','V1-Packet'].includes(id))throw new Error('Effect is not in the confirmed collection: '+id);
 const cap=id.endsWith('Capacity'),base=cap?655/60:1135/60,t=f/fps*base/((scene?.frames||Math.round(base*fps))/fps);
 const rows=scene?.lines?.length?scene.lines:defaultRows;
 const parts=defaultParts.map((s,i)=>({...s,sub:scene?.items?.[i]?.label||s.sub,title:scene?.items?.[i]?.text||s.title}));
 const kind=id.startsWith('W1')?'pearl':'plum';
 return <Copy.Provider value={{rows,parts}}>{id.startsWith('P2')?(cap?<PaperCapacity t={t}/>:<PaperPacket t={t}/>):cap?<MachineCapacity t={t} kind={kind}/>:<MachinePacket t={t} kind={kind}/>}</Copy.Provider>;
};
