# Proyecto de calidad del aire CQP, 2023–2025

## Avance 2: EDA y Streamlit

El notebook ejecutado está en `notebooks/02_eda.ipynb`, los hallazgos en `reports/hallazgos.md` y la aplicación en `app/app.py`. Tiene tres páginas: Contexto y calidad de datos, Exploración de concentraciones y Patrones y análisis de la pregunta. Incluye siete gráficos Plotly y filtros de contaminante, estaciones, fechas, horas comunes y meteorología.

Desde la raíz del proyecto, con Python 3.12:

```text
python -m pip install -r requirements.txt
python -m streamlit run app/app.py --global.developmentMode false --server.address 127.0.0.1 --browser.gatherUsageStats false
```

`requirements.txt` documenta las dependencias principales: pandas, numpy, Plotly, Streamlit, Matplotlib y herramientas de ejecución de notebooks. Las instrucciones de entorno virtual, la estructura completa, el alcance y el estado de las comprobaciones están en `LEEME_AVANCE2.md`. `docs/guion_exposicion.md` propone una demostración de 7–8 minutos. Los archivos están preparados localmente; el repositorio GitHub aún no se ha actualizado.

## Dataset

Base para el análisis exploratorio del Avance 2. Descarga realizada el 4 de octubre de 2026 desde SINCA, Ministerio del Medio Ambiente de Chile. Datos observados, sin mediciones simuladas ni imputación de faltantes.

## Archivo principal

`data/processed/dataset_horario_cqp_2023_2025.csv`

Una fila por fecha/hora y estación: **105.216 filas, 32 columnas**, incluyendo las horas sin mediciones. Periodo: 2023-01-01 00:00 a 2025-12-31 23:00. Cuatro estaciones y tres comunas. Los blancos son datos faltantes, nunca ceros.

| Estación oficial | Comuna | ID SINCA | Código de serie |
|---|---|---|---|
| Ventanas | Puchuncaví | 188 | 548 |
| La Greda | Puchuncaví | 278 | 503 |
| Centro Quintero | Quintero | 204 | 539 |
| Concón | Concón | 185 | 509 |

Centro Quintero corresponde al nombre oficial para el foco “Quintero Centro” de la presentación. La estación histórica Concón sustituye explícitamente el foco propuesto “Concón Oeste”: no se afirma que sean la misma estación. Este cambio debe explicarse en el alcance del proyecto. Las estaciones históricas son de propietarios privados y sus datos están publicados en SINCA. No representan las 14 estaciones de la nueva red pública del MMA. No permiten por sí solas evaluar un antes/después de esa red.

## Variables

| Columna | Unidad original SINCA | Disponibilidad |
|---|---|---|
| mp25_ug_m3 | ug/m3 | Cuatro estaciones |
| mp10_ug_m3n | ug/m3N | Cuatro estaciones |
| so2_ppb | ppb | Cuatro estaciones |
| velocidad_viento_m_s | m/s | Cuatro estaciones |
| direccion_viento_grados | Deg.M | Cuatro estaciones |
| temperatura_c | deg.C | Solo Concón |
| humedad_relativa_pct | % | Solo Concón |

Se preservan las unidades originales. No se convirtió SO2 de ppb a ug/m3 ni se equiparó MP10 en ug/m3N con MP2.5 en ug/m3. Se conserva literalmente Deg.M como etiqueta de la dirección. No se calculan medias aritméticas de direcciones del viento, porque son una variable circular.

Cada variable tiene columnas `_estado` y `_fuera_rango`. Año, mes, hora, día de semana y estación del año son atributos derivados del calendario de la fuente. `dia_semana` usa lunes=0 y domingo=6. Las estaciones del año son agrupaciones por mes: verano diciembre–febrero, otoño marzo–mayo, invierno junio–agosto y primavera septiembre–noviembre.

## Estado de validación: limitación central

**Las 309.217 mediciones de contaminantes con valor figuran como no validadas en las exportaciones descargadas.** Hay 6.431 posiciones sin dato entre las 12 series de contaminantes. No hay valores disponibles en las columnas de registros validados o preliminares de estas exportaciones. Esto describe el estado publicado en la descarga y no sustituye una auditoría instrumental.

Para meteorología, el TXT no entrega la misma clasificación; se usa `sin_clasificacion_en_exportacion`. En temperatura/humedad de las otras estaciones se usa `variable_no_descargada_para_estacion`: sus fichas revisadas no ofrecen esas series para el periodo.

Los datos permiten explorar patrones, sujetos a posibles errores instrumentales, calibraciones y revisiones posteriores. No se etiquetan “episodios críticos”, “excedencias oficiales” ni “incumplimientos”. Para esa parte del proyecto hace falta definir el indicador, verificar el criterio normativo aplicable, las unidades, la representatividad y disponer de validación suficiente.

## Preparación

1. Descargar las series horarias originales en TXT. Este formato conserva los encabezados, unidades y las tres columnas de clasificación de los contaminantes, que el CSV oficial puede dejar sin etiquetas completas.
2. Solicitar un margen temporal antes y después de 2023–2025 y recortar por los timestamps de las filas. El exportador puede incluir horas del día siguiente y empezar en 01:00. No se desplazan las horas arbitrariamente.
3. Interpretar YYMMDD y HHMM y conservar la hora tal como la entrega SINCA. La etiqueta “Huso horario 19” de las fichas corresponde a coordenadas UTM, no permite deducir una zona horaria temporal. No se convierte a UTC ni se asume un tratamiento de horario de verano. Confirmar este punto antes de cruzar con otras fuentes.
4. Mantener las columnas originales de valores en el formato largo. Priorizar validado, luego preliminar y luego no validado si existen varios valores para una hora.
5. Completar la grilla de horas para mostrar faltantes explícitamente, sin interpolar ni reemplazar por cero.
6. Comprobar duplicados y rangos básicos: concentraciones y velocidad no negativas, dirección 0–360, humedad 0–100. Temperaturas negativas son admisibles. El valor original se conserva; un valor fuera de estos rangos se excluye de `valor`. En esta descarga se encontraron cero valores fuera de esos rangos y cero timestamps duplicados por serie.
7. Conservar extremos dentro de rango. No se eliminan mediante IQR ni se presupone que son errores. El chequeo de rango no acredita validez instrumental ni elimina la necesidad de investigar anomalías.

## Archivos incluidos

- `data/raw/`: 22 TXT originales sin modificar.
- `data/processed/dataset_horario_cqp_2023_2025.csv`: tabla principal para Python y Streamlit.
- `data/processed/mediciones_largo_2023_2025.csv`: 578.688 posiciones hora/variable, incluyendo faltantes, unidades, estado, valores originales y archivo de procedencia.
- `data/processed/resumen_diario_eda.csv`: medias observadas y número de horas por día/variable. `media_diaria_eda` se entrega solo con al menos 18 observaciones horarias. Es un criterio exploratorio de 75 % de la grilla de 24 horas, **no un cálculo normativo**. La dirección del viento queda sin media diaria.
- `docs/calidad_por_serie.csv`: cobertura, faltantes, duplicados, clasificación y fechas efectivas.
- `docs/cobertura_mensual.csv`: cobertura mensual y estadísticas por serie. La dirección queda sin media ni mediana.
- `docs/download_manifest.json`: URLs exactas, parámetros, fecha de descarga y hashes SHA-256.
- `docs/estaciones.json`: identidad y fuentes de las estaciones.
- `docs/diccionario.csv`: significado de las 32 columnas principales.
- `docs/resumen.json`: conteos generales de preparación.
- `src/descargar.py` y `src/preparar.py`: scripts reproducibles.

## Uso en Python

Desde la carpeta `dataset_cqp`:

```python
import pandas as pd

df = pd.read_csv(
    'data/processed/dataset_horario_cqp_2023_2025.csv',
    parse_dates=['fecha_hora'],
    low_memory=False,
)
print(df.groupby('estacion')[['mp25_ug_m3', 'mp10_ug_m3n', 'so2_ppb']].count())
# Revisar la cobertura y la clasificación antes de comparar estaciones.
```

Para reconstruir desde los TXT incluidos, instalar pandas y numpy y ejecutar:

```text
python -m pip install -r requirements.txt
python src/preparar.py
```

Para descargar nuevamente, ejecutar `python src/descargar.py --refresh` y luego `python src/preparar.py`. Sin `--refresh`, se reutilizan los archivos originales locales. SINCA puede revisar datos históricos: una nueva descarga puede cambiar los resultados. Conservar el paquete original para reproducir esta versión.

## Fuentes

- Índice regional: https://sinca.mma.gob.cl/index.php/region/index/id/V
- Ventanas: https://sinca.mma.gob.cl/index.php/estacion/index/id/188
- La Greda: https://sinca.mma.gob.cl/index.php/estacion/index/id/278
- Centro Quintero: https://sinca.mma.gob.cl/index.php/estacion/index/id/204
- Concón: https://sinca.mma.gob.cl/index.php/estacion/index/id/185
- Clasificación SINCA: https://sinca.mma.gob.cl/index.php/pagina/index/id/validacion

## Continuación del proyecto

Se pueden estudiar distribuciones, diferencias entre estaciones, patrones por hora/mes y relaciones con velocidad/dirección del viento en las cuatro estaciones. Analizar temperatura y humedad exclusivamente en Concón. Comparar estaciones con periodos comunes y mostrar cobertura; no sumar registros de dos estaciones de Puchuncaví como si fuesen dos observaciones independientes de toda la comuna. La comparación espacial describe puntos de monitoreo y no una exposición comunal completa.

