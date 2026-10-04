"""Exporta resultados y hallazgos reproducibles desde el dataset preparado."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import eda

def markdown_table(df):
    cols = list(df.columns)
    lines = ['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join(['---'] * len(cols)) + ' |']
    for row in df.itertuples(index=False, name=None):
        lines.append('| ' + ' | '.join(f'{x:.3f}' if isinstance(x, float) else str(x) for x in row) + ' |')
    return '\n'.join(lines)

def run(df=None):
    df = eda.load_data() if df is None else df
    reports = eda.ROOT / 'reports'
    figures = eda.ROOT / 'figures'
    reports.mkdir(exist_ok=True); figures.mkdir(exist_ok=True)
    all_stats, all_common, all_wind, annual, extremes = [], [], [], [], []
    sections = []
    for variable, (label, unit) in eda.VARIABLES.items():
        common = eda.common_hours(df, variable)
        stats = eda.station_summary(df, variable).assign(variable=variable)
        matched = eda.station_summary(common, variable).assign(variable=variable)
        wind = eda.relationships(df, variable).assign(variable=variable)
        yearly = common.groupby(['estacion', 'anio'], observed=True)[variable].agg(n='count', mediana='median', media='mean').reset_index().assign(variable=variable)
        all_stats.append(stats); all_common.append(matched); all_wind.append(wind); annual.append(yearly)
        extremes.append(df.nlargest(10,variable)[['fecha_hora','estacion',variable,variable+'_estado']].rename(columns={variable:'valor',variable+'_estado':'estado'}).assign(variable=variable))
        table = matched[['estacion','n','media','mediana','p95','maximo']]
        sections.extend([f'## {label} ({unit})',
                         f'Comparación sobre **{common.fecha_hora.nunique():,} horas comunes** entre las cuatro estaciones. No se imputan valores.',
                         markdown_table(table),
                         'La mediana describe el centro de la distribución; el percentil 95 describe su cola superior. Los máximos son registros puntuales que requieren revisión, no episodios oficialmente constatados.'])
    for name, parts in [('estadisticas_por_estacion',all_stats),('comparacion_horas_comunes',all_common),('relacion_viento',all_wind),('comparacion_anual_horas_comunes',annual),('extremos_para_revision',extremes)]:
        pd.concat(parts,ignore_index=True).to_csv(reports/f'{name}.csv',index=False,encoding='utf-8-sig')
    cov = eda.monthly_coverage(df,'mp25_ug_m3')
    worst = cov.sort_values('cobertura_pct').iloc[0]
    mp25 = eda.common_hours(df,'mp25_ug_m3')
    med = mp25.groupby('estacion',observed=True).mp25_ug_m3.median()
    profile = eda.hourly_profile(mp25,'mp25_ug_m3')
    v = profile[profile.estacion.eq('Ventanas')]
    peak = v.loc[v.mediana.idxmax()]
    low = v.loc[v.mediana.idxmin()]
    wind = eda.relationships(df,'mp25_ug_m3').set_index('estacion')
    direction = df.dropna(subset=['mp25_ug_m3','direccion_viento_grados']).copy()
    sectors = np.array(['N','NE','E','SE','S','SO','O','NO'])
    direction['sector_viento'] = sectors[((direction.direccion_viento_grados + 22.5) % 360 // 45).astype(int)]
    sector_stats = direction.groupby(['estacion','sector_viento'],observed=True).mp25_ug_m3.agg(n='count',mediana='median').reset_index()
    sector_stats.to_csv(reports/'mp25_por_sector_viento.csv',index=False,encoding='utf-8-sig')
    met = pd.concat([eda.relationships(df,'mp25_ug_m3',v).assign(predictor=v) for v in ['temperatura_c','humedad_relativa_pct']],ignore_index=True)
    met.to_csv(reports/'mp25_meteorologia_concon.csv',index=False,encoding='utf-8-sig')
    report = '\n\n'.join([
        '# Hallazgos preliminares del EDA · Aire CQP',
        'Fuente: descarga SINCA del 4 de octubre de 2026. Periodo 2023–2025. Cuatro estaciones históricas. Todas las mediciones disponibles de contaminantes en esta versión están clasificadas como no validadas. Los hallazgos son descriptivos y provisionales.',
        '## Pregunta ajustada', eda.QUESTION,
        'La frecuencia de episodios críticos queda pendiente de una definición analítica y normativa verificada. Concón sustituye explícitamente el foco Concón Oeste y no se presume identidad entre ambas. El análisis no evalúa un efecto de la nueva red pública.',
        '## Calidad y cobertura',
        f'105.216 posiciones hora/estación y 309.217 mediciones de contaminantes disponibles. No se imputan faltantes, no se eliminan extremos dentro de rango y no hay claves duplicadas. La menor cobertura mensual de MP2.5 corresponde a {worst.estacion}, {worst.periodo}: **{worst.cobertura_pct:.2f}%** ({int(worst.n)}/{int(worst.esperadas)} horas). Esta pérdida de información puede afectar la comparación y la evolución anual.',
        '## Hallazgos que responden a la pregunta',
        f'1. En horas comunes, Ventanas tiene la mayor mediana de MP2.5: **{med["Ventanas"]:.0f} µg/m³**. Centro Quintero y La Greda tienen {med["Centro Quintero"]:.0f} y {med["La Greda"]:.0f} µg/m³, y Concón {med["Concón"]:.0f} µg/m³. Esto describe las estaciones seleccionadas, no una exposición total por comuna.',
        '2. El orden entre estaciones cambia según contaminante. Ventanas presenta la mayor mediana de MP10 y Concón la mayor mediana de SO₂. Por tanto, la pregunta debe tratar cada contaminante por separado.',
        f'3. En Ventanas, el perfil mediano de MP2.5 alcanza **{peak.mediana:.0f} µg/m³ a las {int(peak.hora):02d}:00**, frente a {low.mediana:.0f} µg/m³ a las {int(low.hora):02d}:00. Los perfiles usan las mismas horas entre estaciones. La diferencia horaria merece explorarse por año y época antes de considerarla estable.',
        f'4. La asociación de MP2.5 con velocidad del viento cambia de signo: Spearman **{wind.loc["Ventanas","spearman"]:.3f}** en Ventanas, **{wind.loc["Concón","spearman"]:.3f}** en Concón, **{wind.loc["La Greda","spearman"]:.3f}** en La Greda y **{wind.loc["Centro Quintero","spearman"]:.3f}** en Centro Quintero. Se calcula con todos los pares disponibles dentro de cada estación. No permite afirmar que el viento cause el cambio ni identificar una fuente emisora.',
        *sections,
        '## Meteorología y dimensiones adicionales',
        markdown_table(met[met.n_pares.gt(0)][['estacion','predictor','n_pares','spearman']]),
        'Temperatura y humedad se analizan solo en Concón. La tabla de sectores del viento conserva n por sector y una convención de ocho sectores de 45 grados sobre la dirección reportada en Deg.M. No se calcula una media aritmética de direcciones.',
        '## Límites de interpretación',
        '- Registros de contaminantes no validados: revisar calibraciones y contexto antes de interpretar extremos.\n- Las unidades no se convierten ni se mezclan entre contaminantes.\n- Las horas conservan la etiqueta original de SINCA, sin offset UTC confirmado.\n- Las horas comunes reducen diferencias de disponibilidad, pero el subconjunto puede seguir teniendo sesgo de selección.\n- Las observaciones horarias están autocorrelacionadas. Las correlaciones son descriptivas, sin pruebas de significancia ni causalidad.\n- Las medias diarias usan al menos 18 horas como criterio de EDA, no normativo.\n- Las concentraciones se observan en puntos de monitoreo, no sobre toda la población comunal.',
        '## Siguiente revisión analítica',
        'Comprobar perfiles por año y época del año, investigar los meses con menor cobertura, revisar extremos contra los TXT y evaluar relaciones con dirección del viento. Mantener pendiente la clasificación de episodios hasta verificar el indicador y la validación necesaria.',
        '## Fuentes',
        '[SINCA, estaciones de Valparaíso](https://sinca.mma.gob.cl/index.php/region/index/id/V). [Clasificación de validación](https://sinca.mma.gob.cl/index.php/pagina/index/id/validacion). Las URLs exactas y hashes de cada serie están en docs/download_manifest.json.',
    ])
    (reports/'hallazgos.md').write_text(report,encoding='utf8')
    charts = {'01_cobertura':eda.coverage_chart(df,'mp25_ug_m3'),
              '02_distribucion':eda.histogram_chart(mp25,'mp25_ug_m3'),
              '03_comparacion':eda.box_chart(mp25,'mp25_ug_m3'),
              '04_serie_diaria':eda.daily_chart(df,'mp25_ug_m3'),
              '05_perfil_horario':eda.hourly_chart(mp25,'mp25_ug_m3'),
              '06_mes_hora':eda.month_hour_chart(df,'mp25_ug_m3','Ventanas'),
              '07_viento':eda.scatter_chart(df,'mp25_ug_m3')}
    for name, fig in charts.items():
        fig.write_html(figures/f'{name}.html',include_plotlyjs='directory',full_html=True)
    # Figura estática exportable para revisar simultáneamente comparación y horario.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig, axes = plt.subplots(1,2,figsize=(13,5.5),layout='constrained')
    axes[0].bar(med.index,med.values,color=[eda.COLORS[s] for s in med.index])
    axes[0].set(title='Mediana de MP2.5 en horas comunes',ylabel='MP2.5 (µg/m³)')
    axes[0].tick_params(axis='x',rotation=18)
    for i,val in enumerate(med.values):axes[0].text(i,val+.35,f'{val:.0f}',ha='center')
    for station,g in profile.groupby('estacion',observed=True):
        axes[1].plot(g.hora,g.mediana,label=station,color=eda.COLORS[station],linewidth=2)
    axes[1].set(title='Perfil horario mediano de MP2.5',xlabel='Hora según SINCA',ylabel='MP2.5 (µg/m³)',xticks=range(0,24,3))
    axes[1].legend(fontsize=9,frameon=False)
    for ax in axes:ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.suptitle('Calidad del aire CQP · 2023–2025',fontsize=17)
    fig.supxlabel(f'{mp25.fecha_hora.nunique():,} horas comunes · Registros no validados · Comparación descriptiva',fontsize=10)
    fig.savefig(figures/'resumen_mp25.png',dpi=180);plt.close(fig)
    return {'horas_comunes_mp25':mp25.fecha_hora.nunique(),'graficos_html':len(charts),'archivo_hallazgos':str(reports/'hallazgos.md')}

if __name__ == '__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
