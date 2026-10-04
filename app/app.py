from shared import st, pd, eda, setup, controls, chart

setup('Contexto y calidad de datos')
st.subheader('Pregunta de análisis')
st.write(eda.QUESTION)
st.write('Y: concentraciones horarias. X: estación, horario y meteorología disponible. T: 2023–2025. Las mediciones describen puntos de monitoreo; no equivalen a la exposición completa de cada comuna.')
with st.expander('Alcance y decisiones de preparación'):
    st.write('Cuatro estaciones históricas publicadas en SINCA. Concón reemplaza explícitamente a Concón Oeste. Centro Quintero es el nombre oficial usado en los datos. Temperatura y humedad solo se analizan en Concón. No se comparan estas estaciones como si fueran las 14 de la nueva red pública.')
    st.write('Los faltantes siguen vacíos. No se interpolan ni se reemplazan por cero. Se preservan SO₂ en ppb, MP10 en µg/m³N y MP2.5 en µg/m³. Se mantienen los valores extremos dentro de rango. Las horas conservan la etiqueta de la fuente, sin conversión de zona horaria.')
df, variable = controls()
summary = eda.station_summary(df, variable)
c1, c2, c3 = st.columns(3)
c1.metric('Posiciones hora/estación', f'{len(df):,}')
c2.metric('Mediciones disponibles', f'{df[variable].count():,}')
c3.metric('Cobertura de la selección', f'{100*df[variable].notna().mean():.1f}%')
chart(eda.coverage_chart(df, variable), 'coverage')
st.write('Los espacios sin mediciones pueden afectar la comparación. La cobertura usa como denominador todas las horas esperadas dentro del periodo y las estaciones seleccionadas.')
st.dataframe(summary[['estacion','horas_esperadas','n','cobertura_pct']], hide_index=True)
with st.expander('Estado de validación y fuentes'):
    st.dataframe(df.groupby(['estacion',variable+'_estado'], observed=True).size().rename('horas').reset_index(),hide_index=True)
    st.markdown('[Fichas y series oficiales de SINCA](https://sinca.mma.gob.cl/index.php/region/index/id/V) · [Significado de la validación](https://sinca.mma.gob.cl/index.php/pagina/index/id/validacion)')
st.download_button('Descargar resumen de cobertura', summary.to_csv(index=False).encode('utf-8-sig'), 'cobertura_seleccion.csv', 'text/csv')
