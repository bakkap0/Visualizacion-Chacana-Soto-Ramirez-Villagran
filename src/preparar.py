from pathlib import Path
import json,re,csv,io,hashlib
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'data/processed';P.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'docs/download_manifest.json').read_text(encoding='utf8'))
PARAMS={'PM25':('mp25_ug_m3','ug/m3'),'PM10':('mp10_ug_m3n','ug/m3N'),'0001':('so2_ppb','ppb'),'WSPD':('velocidad_viento_m_s','m/s'),'WDIR':('direccion_viento_grados','Deg'),'TEMP':('temperatura_c','deg.C'),'RHUM':('humedad_relativa_pct','%')}
idx=pd.date_range('2023-01-01','2025-12-31 23:00',freq='h')
frames=[];audits=[]
for m in manifest:
 b=(ROOT/m['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==m['sha256']
 t=b.decode('latin1');head,body=t.split('#DATA',1);body=body.split('EOF')[0]
 plots=re.findall(r'^# \d+\. (.+?) \(([^()]*)\)',head,re.M)
 var,unit=PARAMS[m['parameter']]
 actual_unit=plots[0][1];print(m['station'],var,'unit',actual_unit)
 assert actual_unit==unit or (m['parameter']=='WDIR' and actual_unit in ['Deg','Deg.M','deg','degrees','grados'])
 rows=list(csv.reader(io.StringIO(body.strip())))
 expected_cols=3 if m['group']=='Cal' else 1
 parsed=[]
 for row in rows:
  if not row or not ''.join(row[:2]).strip():continue
  row=[x.strip() for x in row]
  if not re.fullmatch(r'\d{6}',row[0]):raise ValueError(row)
  stamp=row[0]+row[1].zfill(4)
  vals=[float(v) if v else np.nan for v in row[2:2+expected_cols]]
  if len(vals)!=expected_cols:raise ValueError('Columnas incompletas')
  parsed.append([stamp,*vals])
 d=pd.DataFrame(parsed,columns=['fecha_hora',*['v'+str(i) for i in range(expected_cols)]])
 d['fecha_hora']=pd.to_datetime(d['fecha_hora'],format='%y%m%d%H%M',errors='raise')
 before=len(d);outside=((d.fecha_hora<idx.min())|(d.fecha_hora>idx.max())).sum()
 d=d[d.fecha_hora.between(idx.min(),idx.max())]
 duplicates=int(d.duplicated('fecha_hora').sum())
 if duplicates:raise ValueError('Tiempos duplicados: revisar antes de continuar')
 d=d.set_index('fecha_hora').reindex(idx);d.index.name='fecha_hora'
 selected=d['v0'].copy();status=pd.Series(np.where(selected.notna(),'validado' if m['group']=='Cal' else 'sin_clasificacion_en_exportacion','sin_dato'),index=idx)
 if m['group']=='Cal':
  for i,label in [(1,'preliminar'),(2,'no_validado')]:
   use=selected.isna() & d['v'+str(i)].notna();selected.loc[use]=d.loc[use,'v'+str(i)];status.loc[use]=label
 invalid=pd.Series(False,index=idx)
 if m['parameter'] in ['PM25','PM10','0001','WSPD']:invalid=selected.lt(0)
 elif m['parameter']=='RHUM':invalid=selected.lt(0)|selected.gt(100)
 elif m['parameter']=='WDIR':invalid=selected.lt(0)|selected.gt(360)
 invalid=invalid | (selected.notna() & ~np.isfinite(selected))
 clean=selected.mask(invalid)
 out=pd.DataFrame({'fecha_hora':idx,'estacion_id':m['station_id'],'codigo_serie':m['station_code'],'estacion':m['station'],'comuna':m['commune'],'variable':var,'unidad':actual_unit,'valor_original':selected.to_numpy(),'valor':clean.to_numpy(),'estado_validacion':status.to_numpy(),'fuera_rango':invalid.to_numpy(),'archivo_fuente':m['file']})
 for i in range(3):out[['valor_validado','valor_preliminar','valor_no_validado'][i]]=d['v'+str(i)].to_numpy() if m['group']=='Cal' else np.nan
 frames.append(out)
 audits.append(dict(estacion=m['station'],variable=var,registros_exportados=before,fuera_periodo=int(outside),duplicados=duplicates,horas_esperadas=len(idx),horas_con_dato=int(selected.notna().sum()),horas_utilizables=int(clean.notna().sum()),faltantes_analisis=int(clean.isna().sum()),cobertura_pct=round(clean.notna().mean()*100,2),fuera_rango=int(invalid.sum()),validados=int((status=='validado').sum()),preliminares=int((status=='preliminar').sum()),no_validados=int((status=='no_validado').sum()),primer_dato=str(clean.first_valid_index()),ultimo_dato=str(clean.last_valid_index())))
long=pd.concat(frames,ignore_index=True)
long.to_csv(P/'mediciones_largo_2023_2025.csv',index=False,encoding='utf-8-sig',date_format='%Y-%m-%d %H:%M:%S')
keys=['fecha_hora','estacion_id','codigo_serie','estacion','comuna']
wide=long.pivot(index=keys,columns='variable',values='valor');wide.columns.name=None
for field,suffix in [('estado_validacion','estado'),('fuera_rango','fuera_rango')]:
 extra=long.pivot(index=keys,columns='variable',values=field);extra.columns=[c+'_'+suffix for c in extra.columns];wide=wide.join(extra)
wide=wide.reset_index().sort_values(['estacion','fecha_hora'])
wide['fecha']=wide.fecha_hora.dt.strftime('%Y-%m-%d');wide['anio']=wide.fecha_hora.dt.year;wide['mes']=wide.fecha_hora.dt.month;wide['hora']=wide.fecha_hora.dt.hour;wide['dia_semana']=wide.fecha_hora.dt.dayofweek
wide['estacion_anio']=wide.mes.map({12:'verano',1:'verano',2:'verano',3:'otono',4:'otono',5:'otono',6:'invierno',7:'invierno',8:'invierno',9:'primavera',10:'primavera',11:'primavera'})
for var in ['temperatura_c','humedad_relativa_pct']:
 wide[var+'_estado']=wide[var+'_estado'].fillna('variable_no_descargada_para_estacion')
 wide[var+'_fuera_rango']=wide[var+'_fuera_rango'].astype('boolean')
assert len(wide)==len(idx)*4 and not wide.duplicated(['estacion_id','fecha_hora']).any()
assert wide.fecha_hora.min()==idx.min() and wide.fecha_hora.max()==idx.max()
wide.to_csv(P/'dataset_horario_cqp_2023_2025.csv',index=False,encoding='utf-8-sig',date_format='%Y-%m-%d %H:%M:%S')
quality=pd.DataFrame(audits);quality.to_csv(ROOT/'docs/calidad_por_serie.csv',index=False,encoding='utf-8-sig')
long['anio']=long.fecha_hora.dt.year;long['mes']=long.fecha_hora.dt.month
monthly=long.groupby(['estacion','comuna','variable','unidad','anio','mes'],observed=True).agg(horas_esperadas=('valor','size'),horas_con_dato=('valor','count'),media=('valor','mean'),mediana=('valor','median'),minimo=('valor','min'),maximo=('valor','max')).reset_index()
monthly['cobertura_pct']=100*monthly.horas_con_dato/monthly.horas_esperadas
monthly.loc[monthly.variable.eq('direccion_viento_grados'),['media','mediana']]=np.nan
monthly.to_csv(ROOT/'docs/cobertura_mensual.csv',index=False,encoding='utf-8-sig')
long['fecha']=long.fecha_hora.dt.floor('D')
daily=long.groupby(['estacion_id','estacion','comuna','variable','unidad','fecha'],observed=True).agg(horas_con_dato=('valor','count'),media_observada=('valor','mean'),maximo_horario=('valor','max')).reset_index()
daily.loc[daily.variable.eq('direccion_viento_grados'),['media_observada','maximo_horario']]=np.nan
daily['suficiente_para_eda']=(daily.horas_con_dato>=18)&~daily.variable.eq('direccion_viento_grados')
daily['media_diaria_eda']=daily.media_observada.where(daily.suficiente_para_eda)
daily.to_csv(P/'resumen_diario_eda.csv',index=False,encoding='utf-8-sig',date_format='%Y-%m-%d')
summary={'filas_horario':len(wide),'filas_largo':len(long),'filas_diario':len(daily),'columnas_horario':len(wide.columns),'horas_por_estacion':len(idx),'inicio':str(idx.min()),'fin':str(idx.max()),'series_descargadas':len(manifest),'duplicados_clave_horaria':0,'valores_fuera_rango':int(long.fuera_rango.sum()),'estados_contaminantes':long[long.variable.isin(['mp25_ug_m3','mp10_ug_m3n','so2_ppb'])].estado_validacion.value_counts().to_dict()}
(ROOT/'docs/resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2));print(quality[['estacion','variable','cobertura_pct','fuera_rango','validados','preliminares','no_validados']].to_string(index=False))


