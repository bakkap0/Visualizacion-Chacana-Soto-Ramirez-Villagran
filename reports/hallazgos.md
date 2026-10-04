# Hallazgos preliminares del EDA · Aire CQP

Fuente: descarga SINCA del 4 de octubre de 2026. Periodo 2023–2025. Cuatro estaciones históricas. Todas las mediciones disponibles de contaminantes en esta versión están clasificadas como no validadas. Los hallazgos son descriptivos y provisionales.

## Pregunta ajustada

¿Cómo varían las concentraciones horarias de MP2.5, MP10 y SO₂ entre Ventanas, La Greda, Centro Quintero y Concón, según hora del día, época del año y condiciones meteorológicas disponibles, durante 2023–2025?

La frecuencia de episodios críticos queda pendiente de una definición analítica y normativa verificada. Concón sustituye explícitamente el foco Concón Oeste y no se presume identidad entre ambas. El análisis no evalúa un efecto de la nueva red pública.

## Calidad y cobertura

105.216 posiciones hora/estación y 309.217 mediciones de contaminantes disponibles. No se imputan faltantes, no se eliminan extremos dentro de rango y no hay claves duplicadas. La menor cobertura mensual de MP2.5 corresponde a Ventanas, 2025-11: **72.36%** (521/720 horas). Esta pérdida de información puede afectar la comparación y la evolución anual.

## Hallazgos que responden a la pregunta

1. En horas comunes, Ventanas tiene la mayor mediana de MP2.5: **16 µg/m³**. Centro Quintero y La Greda tienen 13 y 13 µg/m³, y Concón 12 µg/m³. Esto describe las estaciones seleccionadas, no una exposición total por comuna.

2. El orden entre estaciones cambia según contaminante. Ventanas presenta la mayor mediana de MP10 y Concón la mayor mediana de SO₂. Por tanto, la pregunta debe tratar cada contaminante por separado.

3. En Ventanas, el perfil mediano de MP2.5 alcanza **24 µg/m³ a las 14:00**, frente a 10 µg/m³ a las 07:00. Los perfiles usan las mismas horas entre estaciones. La diferencia horaria merece explorarse por año y época antes de considerarla estable.

4. La asociación de MP2.5 con velocidad del viento cambia de signo: Spearman **0.235** en Ventanas, **0.096** en Concón, **-0.209** en La Greda y **-0.214** en Centro Quintero. Se calcula con todos los pares disponibles dentro de cada estación. No permite afirmar que el viento cause el cambio ni identificar una fuente emisora.

## MP2.5 (µg/m³)

Comparación sobre **22,671 horas comunes** entre las cuatro estaciones. No se imputan valores.

| estacion | n | media | mediana | p95 | maximo |
| --- | --- | --- | --- | --- | --- |
| Centro Quintero | 22671 | 15.895 | 13.000 | 41.000 | 157.000 |
| Concón | 22671 | 13.855 | 12.000 | 29.000 | 126.000 |
| La Greda | 22671 | 15.874 | 13.000 | 37.000 | 118.000 |
| Ventanas | 22671 | 18.221 | 16.000 | 41.000 | 192.000 |

La mediana describe el centro de la distribución; el percentil 95 describe su cola superior. Los máximos son registros puntuales que requieren revisión, no episodios oficialmente constatados.

## MP10 (µg/m³N)

Comparación sobre **25,223 horas comunes** entre las cuatro estaciones. No se imputan valores.

| estacion | n | media | mediana | p95 | maximo |
| --- | --- | --- | --- | --- | --- |
| Centro Quintero | 25223 | 38.050 | 35.000 | 71.000 | 223.000 |
| Concón | 25223 | 31.871 | 29.000 | 67.000 | 261.000 |
| La Greda | 25223 | 39.024 | 34.000 | 86.000 | 554.000 |
| Ventanas | 25223 | 43.603 | 40.000 | 87.000 | 396.000 |

La mediana describe el centro de la distribución; el percentil 95 describe su cola superior. Los máximos son registros puntuales que requieren revisión, no episodios oficialmente constatados.

## SO₂ (ppb)

Comparación sobre **24,993 horas comunes** entre las cuatro estaciones. No se imputan valores.

| estacion | n | media | mediana | p95 | maximo |
| --- | --- | --- | --- | --- | --- |
| Centro Quintero | 24993 | 3.566 | 2.920 | 7.660 | 222.050 |
| Concón | 24993 | 4.544 | 3.620 | 10.694 | 191.940 |
| La Greda | 24993 | 2.914 | 2.770 | 4.830 | 90.040 |
| Ventanas | 24993 | 2.913 | 2.710 | 4.250 | 87.580 |

La mediana describe el centro de la distribución; el percentil 95 describe su cola superior. Los máximos son registros puntuales que requieren revisión, no episodios oficialmente constatados.

## Meteorología y dimensiones adicionales

| estacion | predictor | n_pares | spearman |
| --- | --- | --- | --- |
| Concón | temperatura_c | 25309 | 0.019 |
| Concón | humedad_relativa_pct | 25309 | -0.102 |

Temperatura y humedad se analizan solo en Concón. La tabla de sectores del viento conserva n por sector y una convención de ocho sectores de 45 grados sobre la dirección reportada en Deg.M. No se calcula una media aritmética de direcciones.

## Límites de interpretación

- Registros de contaminantes no validados: revisar calibraciones y contexto antes de interpretar extremos.
- Las unidades no se convierten ni se mezclan entre contaminantes.
- Las horas conservan la etiqueta original de SINCA, sin offset UTC confirmado.
- Las horas comunes reducen diferencias de disponibilidad, pero el subconjunto puede seguir teniendo sesgo de selección.
- Las observaciones horarias están autocorrelacionadas. Las correlaciones son descriptivas, sin pruebas de significancia ni causalidad.
- Las medias diarias usan al menos 18 horas como criterio de EDA, no normativo.
- Las concentraciones se observan en puntos de monitoreo, no sobre toda la población comunal.

## Siguiente revisión analítica

Comprobar perfiles por año y época del año, investigar los meses con menor cobertura, revisar extremos contra los TXT y evaluar relaciones con dirección del viento. Mantener pendiente la clasificación de episodios hasta verificar el indicador y la validación necesaria.

## Fuentes

[SINCA, estaciones de Valparaíso](https://sinca.mma.gob.cl/index.php/region/index/id/V). [Clasificación de validación](https://sinca.mma.gob.cl/index.php/pagina/index/id/validacion). Las URLs exactas y hashes de cada serie están en docs/download_manifest.json.