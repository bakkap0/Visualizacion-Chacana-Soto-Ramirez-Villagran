from shared import st, eda, setup, controls, chart, require_values, comparison

setup('Exploración de concentraciones')
df, variable = controls()
require_values(df, variable)
data = comparison(df, variable)
summary = eda.station_summary(data, variable)
st.subheader('Distribución y comparación entre estaciones')
chart(eda.histogram_chart(data, variable), 'histogram')
st.write('El histograma compara porcentajes dentro de cada estación. Una cola hacia valores altos indica que unos pocos registros pueden influir en la media; no demuestra que esos registros sean errores.')
chart(eda.box_chart(data, variable), 'box')
top = summary.loc[summary.mediana.idxmax()]
st.write(f'En esta selección, {top.estacion} tiene la mayor mediana: {top.mediana:.2f} {eda.VARIABLES[variable][1]}. Empates y dispersión se pueden revisar en la tabla. El boxplot usa todas las observaciones seleccionadas; sus puntos extremos no se dibujan individualmente.')
st.dataframe(summary.round(3),hide_index=True)
st.subheader('Valores extremos para revisar')
st.dataframe(data.nlargest(10,variable)[['fecha_hora','estacion',variable,variable+'_estado']],hide_index=True)
st.caption('Se conservan los valores extremos. Revisar registros originales y contexto antes de atribuirlos a episodios ambientales o fallas instrumentales.')
st.download_button('Descargar estadísticas de la selección',summary.to_csv(index=False).encode('utf-8-sig'),'estadisticas_seleccion.csv','text/csv')
