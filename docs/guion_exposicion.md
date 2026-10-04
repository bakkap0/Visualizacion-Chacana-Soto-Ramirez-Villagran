# Guion de demostración · 7–8 minutos

## 0:00–0:50 · Pregunta y alcance

En Contexto, explicar la preocupación por la calidad del aire en Concón, Quintero y Puchuncaví. Presentar la pregunta ajustada y las cuatro estaciones. Aclarar el reemplazo de Concón Oeste por Concón y que se usan estaciones históricas, no una comparación causal de la nueva red pública.

## 0:50–2:00 · Datos y calidad

Mostrar cobertura de MP2.5. Hay 105.216 posiciones horarias por estación y tiempo, y la base preserva faltantes. Ventanas tiene 89,85 % de cobertura en MP2.5 y noviembre de 2025 baja a 72,36 %. No se imputaron ni eliminaron extremos dentro de rango. Los registros de contaminantes figuran como no validados. Conservar unidades: MP2.5 en µg/m³, MP10 en µg/m³N y SO₂ en ppb.

## 2:00–3:30 · Distribución y comparación

Abrir Exploración con MP2.5 y todas las estaciones. Mantener activada la comparación por horas comunes: 22.671 timestamps. Mostrar histograma y boxplot. Ventanas tiene mediana 16 µg/m³; Centro Quintero y La Greda, 13; Concón, 12. Cambiar a SO₂: la mayor mediana pasa a Concón, 3,62 ppb. Esto muestra por qué analizar cada contaminante por separado.

## 3:30–5:00 · Tiempo y horario

Volver a MP2.5 y abrir Análisis de la pregunta. Mostrar serie diaria y cómo cambia al exigir 24 horas en vez de 18. El criterio es exploratorio. Mostrar el perfil horario: Ventanas tiene mediana máxima de 24 µg/m³ a las 14:00 y mínima de 10 a las 07:00–08:00. Los perfiles son distintos entre estaciones. El mapa mes/hora permite explorar variaciones dentro del año, sin dar por probada su estabilidad.

## 5:00–6:15 · Meteorología

Mostrar scatter y tabla de Spearman. La relación entre MP2.5 y velocidad del viento cambia de signo entre estaciones y no es una explicación causal. El gráfico muestra hasta 1.500 pares por estación, pero la tabla usa todos los pares disponibles. Si hay tiempo, seleccionar temperatura: solo Concón tiene datos.

## 6:15–7:15 · Hallazgos y límites

Resumir las diferencias por contaminante, los perfiles horarios y la relación variable con meteorología. Recordar la validación pendiente, los faltantes y que estaciones no representan por sí solas a toda una comuna. El conteo de episodios críticos queda pendiente de verificar su definición y la validación requerida. Proponer revisar perfiles por año, dirección del viento y meses incompletos.

## 7:15–7:45 · Reproducibilidad

Mostrar brevemente el repositorio cuando el equipo haya incorporado los archivos. Ubicar notebook, scripts, requirements y README. Explicar que las tablas y gráficos se regeneran con `python src/analizar.py` y Streamlit se ejecuta con `python -m streamlit run app/app.py`.

## Preguntas que deben poder responder

- ¿Por qué usamos horas comunes? Para que las estaciones comparadas compartan los mismos timestamps. No garantiza ausencia de sesgo.
- ¿Qué hicimos con faltantes? Los conservamos vacíos y mostramos cobertura.
- ¿Qué hicimos con extremos? Los conservamos y listamos para revisión, dada la validación pendiente.
- ¿Por qué mediana y percentil 95? Para distinguir el centro de la distribución de su cola superior.
- ¿La correlación prueba causalidad? No. Es descriptiva y puede depender de horario, época y condiciones locales.
- ¿Contamos incumplimientos? No. Falta verificar indicador, unidades, agregación y validación necesaria.
