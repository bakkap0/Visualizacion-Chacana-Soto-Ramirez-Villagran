import urllib.request,urllib.parse,json,hashlib,time,argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Descarga series oficiales SINCA 2023-2025')
parser.add_argument('--refresh',action='store_true',help='Volver a descargar las series existentes')
args=parser.parse_args()
(ROOT/'data/raw').mkdir(parents=True,exist_ok=True)
(ROOT/'docs').mkdir(parents=True,exist_ok=True)
previous_path=ROOT/'docs/download_manifest.json'
previous={x['file']:x for x in json.loads(previous_path.read_text(encoding='utf8'))} if previous_path.exists() else {}
STATIONS=[('188','548','Ventanas','Puchuncaví'),('278','503','La Greda','Puchuncaví'),('204','539','Centro Quintero','Quintero'),('185','509','Concón','Concón')]
jobs=[]
for sid,code,name,commune in STATIONS:
 for var,group,macro in [('PM25','Cal','PM25.horario.horario'),('PM10','Cal','PM10.horario.horario'),('0001','Cal','0001.horario.horario'),('WSPD','Met','horario_010'),('WDIR','Met','horario_000_spec' if code=='509' else 'horario_010_spec')]+([('TEMP','Met','horario_002'),('RHUM','Met','horario_000')] if code=='509' else []):
  jobs.append(dict(station_id=sid,station_code=code,station=name,commune=commune,parameter=var,group=group,macro=macro))
def fetch(j):
 p=dict(outtype='txt',macro=f'./RV/{j["station_code"]}/{j["group"]}/{j["parameter"]}//{j["macro"]}.ic',path='/usr/airviro/data/CONAMA/',lang='esp',rsrc='',macropath='',**{'from':'22123100','to':'26010123'})
 u='https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.tsindico2.cgi?'+urllib.parse.urlencode(p)
 filename=f'{j["station_code"]}_{j["parameter"]}_2023_2025.txt';f=ROOT/'data/raw'/filename
 for attempt in range(3):
  try:
   cached=f.exists() and not args.refresh
   if cached: b=f.read_bytes()
   else:
    with urllib.request.urlopen(u,timeout=90) as r: b=r.read()
   if b'#DATA' not in b or b'EOF' not in b: raise ValueError('Respuesta sin bloque de datos completo')
   if not cached: f.write_bytes(b)
   result={**j,'url':u,'file':'data/raw/'+filename,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'download_utc':previous.get('data/raw/'+filename,{}).get('download_utc',datetime.fromtimestamp(f.stat().st_mtime,timezone.utc).isoformat()) if cached else datetime.now(timezone.utc).isoformat()}
   t=b.decode('latin1');head=t.split('#DATA')[0]
   result['plot_variables']=[line.strip() for line in head.splitlines() if __import__('re').match(r'# \d+\.',line)]
   print(j['station'],j['parameter'],len(b),flush=True)
   return result
  except Exception:
   if attempt==2: raise
   time.sleep(2)
results=[]
with ThreadPoolExecutor(max_workers=3) as ex:
 for fut in as_completed([ex.submit(fetch,j) for j in jobs]): results.append(fut.result())
(ROOT/'docs/download_manifest.json').write_text(json.dumps(sorted(results,key=lambda x:(x['station_code'],x['parameter'])),ensure_ascii=False,indent=2),encoding='utf8')
print('DOWNLOADED',len(results))


