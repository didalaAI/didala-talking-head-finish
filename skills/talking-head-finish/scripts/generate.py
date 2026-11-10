"""ComfyUI local / Comfy Cloud adapter. No credentials or model weights bundled."""
from pathlib import Path
import argparse,copy,hashlib,json,os,time,urllib.error,urllib.parse,urllib.request,uuid
import sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        old,new=urllib.parse.urlsplit(req.full_url),urllib.parse.urlsplit(newurl)
        if old.scheme=='https' and new.scheme!='https':raise ValueError('Refusing HTTPS downgrade')
        out=super().redirect_request(req,fp,code,msg,headers,newurl)
        if out and (old.hostname,old.port)!=(new.hostname,new.port):
            for k in list(out.headers)+list(out.unredirected_hdrs):
                if k.lower() in ['x-api-key','authorization','cookie']:out.remove_header(k)
        return out

class Client:
    def __init__(self,base_url,provider='local',key_env=None):
        self.base=base_url.rstrip('/');self.provider=provider;self.headers={}
        parsed=urllib.parse.urlsplit(self.base)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:raise ValueError('Use a plain endpoint URL; credentials belong in the configured environment variable')
        if provider=='cloud':
            if parsed.scheme!='https' and parsed.hostname not in ['localhost','127.0.0.1']:raise ValueError('Cloud endpoint must use HTTPS')
            key=os.environ.get(key_env or 'COMFY_CLOUD_API_KEY')
            if not key:raise ValueError('Set your own cloud API key environment variable; its value is never printed or saved.')
            self.headers['X-API-Key']=key
        self.op=urllib.request.build_opener(SafeRedirect(),urllib.request.ProxyHandler({}) if parsed.hostname in ['localhost','127.0.0.1'] else urllib.request.ProxyHandler())
    def request(self,path,data=None,content_type='application/json',raw=False):
        if isinstance(data,dict):data=json.dumps(data).encode()
        req=urllib.request.Request(self.base+path,data=data,headers={**self.headers,**({'Content-Type':content_type} if data is not None else {})})
        try:
            with self.op.open(req,timeout=90) as response:result=response.read()
        except urllib.error.HTTPError as e:
            # Do not print signed URLs, response bodies, API keys or provider headers.
            code=e.code;e.close()
            raise RuntimeError('Generation API returned HTTP '+str(code)+'; check account credits, workflow nodes and configuration.') from None
        return result if raw else (json.loads(result) if result.strip() else {})
    def upload(self,image):
        image=Path(image);boundary='didala-'+uuid.uuid4().hex
        filename='input-'+uuid.uuid4().hex+image.suffix.lower()
        fields=b''
        for name,value in [('type','input'),('overwrite','false')]:fields+=(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n').encode()
        fields+=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+image.read_bytes()+f'\r\n--{boundary}--\r\n'.encode()
        data=self.request('/upload/image',fields,'multipart/form-data; boundary='+boundary)
        return (data.get('subfolder','').strip('/')+'/' if self.provider=='local' and data.get('subfolder') else '')+data['name']
    def job(self,workflow,receipt,timeout=1800):
        receipt=Path(receipt)
        digest=hashlib.sha256(json.dumps(workflow,sort_keys=True).encode()).hexdigest()
        if receipt.exists():
            saved=json.loads(receipt.read_text(encoding='utf-8'));
            if saved['workflow_sha256']!=digest:raise ValueError('Receipt belongs to a different workflow; use a new output folder.')
            pid=saved['prompt_id']
        else:
            data=self.request('/prompt',{'prompt':workflow,'client_id':'didala-'+uuid.uuid4().hex})
            if data.get('node_errors'):raise ValueError('Provider rejected workflow nodes; inspect your exported workflow.')
            pid=data['prompt_id'];receipt.write_text(json.dumps(dict(prompt_id=pid,workflow_sha256=digest)),encoding='utf-8')
        start=time.monotonic();last=-60
        while time.monotonic()-start<timeout:
            path=('/history_v2/' if self.provider=='cloud' else '/history/')+urllib.parse.quote(pid,safe='')
            result=self.request(path);record=result.get(pid)
            if record:
                status=record.get('status',{})
                if status.get('status_str')=='error':raise RuntimeError('Generation failed. Receipt retained for provider diagnostics; no new job submitted.')
                if status.get('completed'):
                    return record
            if time.monotonic()-start-last>=45:print('RUNNING',round(time.monotonic()-start),'seconds',flush=True);last=time.monotonic()-start
            time.sleep(2)
        raise TimeoutError('Generation still pending. Receipt retained; rerun to resume the same job without re-submitting.')

def outputs(record):
    found=[]
    for node in record.get('outputs',{}).values():
        for values in node.values():
            if isinstance(values,list):
                found.extend(x for x in values if isinstance(x,dict) and str(x.get('filename','')).lower().endswith(('.mp4','.webm','.mov')))
    return list({(x['filename'],x.get('subfolder',''),x.get('type','output')):x for x in found}.values())

def generate(config,image,prompt,out,seed=79011,timeout=1800):
    config_path=Path(config);cfg=json.loads(config_path.read_text(encoding='utf-8'));out=Path(out)
    if out.exists() and any(out.iterdir()) and not (out/'input-record.json').is_file():raise ValueError('Use an empty/new shot folder; existing files are not overwritten')
    out.mkdir(parents=True,exist_ok=True)
    client=Client(cfg['base_url'],cfg.get('provider','local'),cfg.get('key_env'))
    wf_path=(config_path.parent/cfg['workflow']).resolve();wf=json.loads(wf_path.read_text(encoding='utf-8'))
    if 'nodes' in wf:raise ValueError('Export an API-format workflow, not the UI graph.')
    bind=cfg.get('bindings',{'image':['1','image'],'prompt':['5','prompt'],'seed':['6','noise_seed']})
    source_hash=hashlib.sha256(Path(image).read_bytes()).hexdigest()
    inputs=dict(image_sha256=source_hash,prompt=prompt,seed=seed,workflow_sha256=hashlib.sha256(wf_path.read_bytes()).hexdigest(),provider=cfg.get('provider','local'),endpoint=client.base)
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    provenance=out/'input-record.json'
    if provenance.exists():
        if json.loads(provenance.read_text(encoding='utf-8'))['fingerprint']!=fingerprint:raise ValueError('Output folder belongs to different inputs. Choose a new folder.')
        upload=json.loads(provenance.read_text(encoding='utf-8'))['uploaded_image']
    else:
        upload=client.upload(image);provenance.write_text(json.dumps(dict(**inputs,fingerprint=fingerprint,uploaded_image=upload),ensure_ascii=False,indent=2),encoding='utf-8')
    for key,value in [('image',upload),('prompt',prompt),('seed',seed)]:
        node,field=bind[key];wf[node]['inputs'][field]=value
    if cfg.get('split_conditioning'):
        if client.provider!='local':raise ValueError('Split-conditioning mode is local-only; cloud must use its own supported API workflow.')
        encode={k:v for k,v in wf.items() if k in ['1','2','3','5']};cache='didala-'+fingerprint[:24]
        encode['20']={'class_type':'H3SaveConditioning','inputs':{'conditioning':['5',0],'name':cache}}
        client.job(encode,out/'encode-receipt.json',timeout)
        queue=client.request('/queue')
        if not queue.get('queue_running') and not queue.get('queue_pending'):client.request('/free',{'unload_models':True,'free_memory':True})
        wf={k:v for k,v in wf.items() if k not in ['1','2','5']}
        wf['20']={'class_type':'H3LoadConditioning','inputs':{'name':cache}}
        wf['21']={'class_type':'EmptyMiniMaxH3LatentAV','inputs':{'width':1344,'height':768,'length':124}}
        wf['7']['inputs']['conditioning']=['20',0];wf['10']['inputs']['latent_image']=['21',0]
    (out/'workflow.json').write_text(json.dumps(wf,indent=2),encoding='utf-8')
    record=client.job(wf,out/'sample-receipt.json',timeout);(out/'history.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    files=outputs(record)
    if len(files)!=1:raise ValueError('Expected exactly one generated video; choose an output-only workflow.')
    media=files[0];query=urllib.parse.urlencode({k:media.get(k,'') for k in ['filename','subfolder','type']})
    result=client.request('/view?'+query,raw=True);target=out/'native.mp4'
    target.write_bytes(result)
    (out/'generation.json').write_text(json.dumps(dict(**inputs,native_sha256=hashlib.sha256(result).hexdigest(),action_review='pending',native_spec='Inspect with ffprobe; never label upscaled/interpolated dimensions as native.'),ensure_ascii=False,indent=2),encoding='utf-8')
    print('GENERATED',target,'ACTION REVIEW REQUIRED',flush=True)
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True);p.add_argument('--image',required=True);p.add_argument('--prompt-file',required=True);p.add_argument('--out',required=True);p.add_argument('--seed',type=int,default=79011);p.add_argument('--timeout',type=int,default=1800);a=p.parse_args()
    try:generate(a.config,a.image,Path(a.prompt_file).read_text(encoding='utf-8'),a.out,a.seed,a.timeout)
    except (ValueError,RuntimeError,TimeoutError,urllib.error.URLError) as e:print('ERROR:',str(e).split('https://')[0],file=sys.stderr);raise SystemExit(1)
