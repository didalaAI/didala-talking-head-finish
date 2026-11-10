"""Compile a confirmed source design using this episode's text, assets and SRT timing.

The approved source is the implementation, not a screenshot or prose imitation.
Templates never read private media. Every authored scene has a reviewable JSON spec.
"""
from pathlib import Path
import argparse,hashlib,json,re
SKILL=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def effects():return {x['id']:x for x in read(SKILL/'references/approved-effects.json')['effects']}
def inside(root,value):
 p=(root/value).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('Design paths must remain inside the project')
 return p
def example(effect):
 if effect not in effects():raise ValueError('Effect is not in the current confirmed collection')
 return read(SKILL/('references/design-examples/'+effect+'.json'))
def validate_spec(project,scene,spec,demo=False):
 entry=effects().get(scene.get('variant'))
 if not entry or spec.get('effect')!=entry['id']:raise ValueError('Scene and confirmed design do not match')
 allowed={'human':['side','punch'],'mg':['mg'],'screen':['screen'],'h3':['h3']}[entry['mode']]
 if scene.get('kind') not in allowed:raise ValueError('Scene kind does not match the confirmed effect')
 if not demo and (not spec.get('semantic_alignment') or not spec.get('reviewed_for_current_script')):raise ValueError('Describe this episode object/action/result and review its text/cues before rendering')
 ref=example(entry['id'])
 if set(ref['text'])-set(spec.get('text',{})):raise ValueError('Design is missing authored text slots')
 if any(not isinstance(v,str) for v in spec['text'].values()):raise ValueError('Text slots must be strings')
 timing=spec['timing'];previous=(-1,-1)
 if len(timing)<2 or timing[0]!=[0,0]:raise ValueError('Timing must start at [source=0, actual=0]')
 for a,b in timing:
  if a<=previous[0] or b<=previous[1]:raise ValueError('Source and actual cue times must increase strictly')
  previous=a,b
 if abs(timing[-1][1]-scene['frames']/60)>1/60:raise ValueError('Timing must cover this whole scene; do not freeze its tail')
 if abs(timing[-1][0]-ref['duration'])>.02:raise ValueError('Timing must retain the complete approved action')
 for value in spec.get('assets',{}).values():
  if not inside(project/'public',value).is_file():raise ValueError('Missing current-project design asset: '+value)
 if entry['mode']=='h3':
  if not scene.get('asset') or not inside(project/'public',scene['asset']).is_file():raise ValueError('Generated design needs this episode actual generated video')
 if entry['mode']=='screen':
  if not spec.get('screens'):raise ValueError('Provide original screenshot and measured region')
  for q in spec['screens']:
   x,y,w,h=q['focus']
   if min(w,h,q['width'],q['height'])<=0 or x<0 or y<0 or x+w>q['width'] or y+h>q['height']:raise ValueError('Screenshot focus is outside the full image')
   for value in [q['asset']]+([q['icon']] if q.get('icon') else []):
    if not inside(project/'public',value).is_file():raise ValueError('Missing screenshot or product icon')
 if entry['source_key']=='MemoryQuestionHuman':
  if entry['family']=='v31' and not all('side-'+x+'.png' in spec.get('assets',{}) for x in ['doubao','workbuddy','deepseek']):raise ValueError('This approved application list requires all three current product icons')
  if entry['family']=='v2' and not all(x.get('asset') for x in spec.get('recipe',{}).get('tags',[])):raise ValueError('Application names need their corresponding icons')
 for tag in spec.get('recipe',{}).get('tags',[]):
  if tag.get('asset') and not inside(project/'public',tag['asset']).is_file():raise ValueError('Missing corresponding application icon')
 if entry['mode']=='human':
  box=spec.get('text_region',{});left=box.get('left',140);width=box.get('width',740)
  if left<70 or width<400 or left+width>1850:raise ValueError('Measure a readable subject-safe text region')
 return entry
def compile_project(project,plan):
 """Build only selected scene implementations. No executable code is accepted in the spec."""
 project=Path(project);imports=[];mapping=[];records=[]
 folder=project/'src/selected';folder.mkdir(parents=True,exist_ok=True)
 for i,scene in enumerate(plan['scenes']):
  if not scene.get('design'):continue
  spec=read(inside(project,scene['design']));entry=validate_spec(project,scene,spec,plan.get('technical_demo',False))
  source=SKILL/'assets/designs'/entry['family'];tokens=read(source/'tokens.json')
  # Deterministic isolated directory: changes never overwrite hand-authored source outside selected/.
  target=folder/('scene'+str(i));target.mkdir(exist_ok=True)
  for filename,meta in tokens.items():
   text=(source/filename).read_text('utf-8')
   for token in sorted(meta['tokens'],key=lambda x:x['start'],reverse=True):
    value=json.dumps(spec['text'][token['id']],ensure_ascii=False)
    text=text[:token['start']]+('{'+value+'}' if token['jsx'] else value)+text[token['end']:]
   # Asset lookup supports supplied icons and arbitrary new topic media, without copying author assets.
   text=text.replace('staticFile(', 'assetFile(')
   if 'assetFile(' in text:text="import {assetFile} from './timing';\n"+text
   region=spec.get('text_region',{})
   text=text.replace('const LEFT=140,WIDTH=740;',f"const LEFT={float(region.get('left',140))},WIDTH={float(region.get('width',740))};")
   (target/filename).write_text(text,encoding='utf-8')
  save(target/'human-recipes.json',{'examples':[spec.get('recipe',{})]})
  save(target/'screens.json',spec.get('screens') or [dict(asset='',icon='',name='',value='',detail='',location='',width=1,height=1,focus=[0,0,1,1])])
  timing="import {staticFile} from 'remotion';\nconst points:number[][]="+json.dumps(spec['timing'])+";\n"
  timing+="export const mappedTime=(t:number)=>{let i=1;while(i<points.length-1&&t>points[i][1])i++;const [a,x]=points[i-1],[b,y]=points[i];return a+(b-a)*Math.max(0,Math.min(1,(t-x)/(y-x)));};\n"
  timing+="const assets:Record<string,string>="+json.dumps(spec.get('assets',{}))+";\nexport const assetFile=(name:string)=>staticFile(assets[name]||name);\n"
  (target/'timing.ts').write_text(timing,encoding='utf-8')
  clip=dict(source_key=entry['source_key'],duration=spec['duration'],asset=scene.get('asset',''))
  wrapper="import React from 'react';\nimport {"+entry['component']+" as Component} from './"+entry['module'].removesuffix('.tsx')+"';\nconst clip="+json.dumps(clip)+";\nexport const Scene=()=> <Component {...({clip} as any)}/>;\n"
  (target/'Scene.tsx').write_text(wrapper,encoding='utf-8')
  imports.append(f"import {{Scene as S{i}}} from './scene{i}/Scene';")
  mapping.append(json.dumps(scene['id'])+f':S{i}')
  records.append(dict(scene=scene['id'],effect=entry['id'],spec_sha256=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()))
 registry="import React from 'react';\n"+'\n'.join(imports)+"\nconst scenes:Record<string,React.ComponentType>={"+','.join(mapping)+"};\nexport const Selected=({id}:{id:string})=>{const C=scenes[id];if(!C)throw new Error('Compile this selected design first');return <C/>;};\n"
 (folder/'Registry.tsx').write_text(registry,encoding='utf-8');save(project/'design-build.json',dict(version='0.3.0',selection_revision=159,scenes=records))
 return records
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
 q=s.add_parser('example');q.add_argument('--effect',required=True);q.add_argument('--out',type=Path,required=True)
 q=s.add_parser('compile');q.add_argument('--project',type=Path,required=True)
 a=p.parse_args()
 if a.cmd=='example':
  if a.out.exists():raise ValueError('Choose a new spec path; existing work is not overwritten')
  save(a.out,example(a.effect));print('Example saved. Adapt text, assets, timing and object/action/result before production.')
 else:print(json.dumps(compile_project(a.project,read(a.project/'plan.json')),ensure_ascii=False))
if __name__=='__main__':main()
