# Avance 2 · Calidad del aire CQP

Proyecto local preparado para realizar la demostración del Avance 2. Incluye el dataset, el notebook ejecutado, una aplicación Streamlit de tres páginas y los hallazgos preliminares. Las mediciones de contaminantes publicadas en esta descarga figuran como no validadas, condición que se muestra en la aplicación y limita las conclusiones.

## Inicio

Se recomienda Python 3.12. Desde la carpeta `dataset_cqp`, crear un entorno local e instalar las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/app.py --global.developmentMode false --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Abrir la URL local indicada por Streamlit. La aplicación usa los CSV incluidos y no necesita descargar datos ni tener acceso a internet durante la exposición. El entorno `.venv` no debe subirse a GitHub.

Para regenerar las tablas, el informe y las figuras:

```powershell
.\.venv\Scripts\python.exe src/analizar.py
```

El notebook `notebooks/02_eda.ipynb` contiene los resultados de una ejecución completa. Se puede abrir en Jupyter o VS Code. Para volver a ejecutarlo desde su editor, seleccionar el intérprete del entorno `.venv`. El notebook detecta la raíz si se abre desde la carpeta del proyecto o desde `notebooks`.

## Pregunta y alcance

¿Cómo varían las concentraciones horarias de MP2.5, MP10 y SO₂ entre Ventanas, La Greda, Centro Quintero y Concón, según hora del día, época del año y condiciones meteorológicas disponibles, durante 2023–2025?

Se conserva el problema del Avance 1 y se explicita el reemplazo de Concón Oeste por la estación histórica Concón. Se estudian cuatro estaciones históricas publicadas en SINCA, no las 14 de la nueva red pública. Viento está disponible en las cuatro estaciones; temperatura y humedad, solo en Concón.

La frecuencia de episodios críticos queda pendiente de verificar el indicador, unidades, periodo de agregación y validación necesaria. El EDA ofrece evidencia preliminar y no clasifica incumplimientos normativos ni atribuye emisiones a empresas.

## Páginas de la aplicación

1. **Contexto y calidad de datos:** pregunta, alcance, cobertura mensual, conteos de registros y clasificación de validación.
2. **Exploración de concentraciones:** distribución, comparación entre estaciones, estadísticas y extremos para revisar.
3. **Patrones y análisis de la pregunta:** serie temporal, perfil horario, mapa de mes/hora y relaciones con meteorología.

Los filtros de contaminante, estaciones y fecha modifican los resultados. La opción de horas comunes permite comparar exactamente los mismos timestamps entre estaciones. El mínimo de horas diarias cambia qué días tienen una media exploratoria. La selección de meteorología adapta el scatter y la tabla de correlación.

Hay siete visualizaciones analíticas: mapa de cobertura, histograma, boxplot, líneas de medias diarias, perfil horario, mapa mes/hora y scatter. Todas usan Plotly y permiten interacción; la aplicación agrega controles que alteran el análisis. Esto cubre el mínimo de cinco gráficos, tres tipos de representación, dos gráficos interactivos y tres páginas.

## Archivos principales

```text
dataset_cqp/
  app/
    app.py
    shared.py
    pages/
      1_Exploracion.py
      2_Pregunta.py
  data/
    raw/
    processed/
  notebooks/02_eda.ipynb
  src/
    descargar.py
    preparar.py
    eda.py
    analizar.py
  docs/
  reports/hallazgos.md
  reports/*.csv
  figures/*.html
  figures/resumen_mp25.png
  requirements.txt
  README.md
  LEEME_AVANCE2.md
```

`README.md` explica el origen, unidades, limpieza y trazabilidad del dataset. `reports/hallazgos.md` desarrolla las interpretaciones y sus límites. Los HTML de `figures` son vistas independientes de MP2.5 para el periodo completo; conservar `plotly.min.js` junto a ellos para que funcionen sin internet.

## Repositorio y demostración

Esta entrega está preparada en archivos locales. **No se ha publicado ni actualizado el repositorio GitHub.** Para incorporarla al repositorio existente, copiar el contenido conservando la estructura, revisar los cambios y versionarlos. Los TXT originales preservan la trazabilidad; los CSV pueden reconstruirse con `src/preparar.py`.

Para la exposición de 7–8 minutos, usar `docs/guion_exposicion.md`. Mostrar las decisiones de limpieza y los hallazgos, sin recorrer cada línea de código. No hace falta un PowerPoint adicional ni un modelo de machine learning para este avance.

## Comprobaciones realizadas

Notebook ejecutado sin errores en sus 11 celdas de código. Tres páginas verificadas con las herramientas de prueba de Streamlit, incluyendo cambios de contaminante/estación, mínimo de horas, meteorología, selección vacía y filtro de validados sin mediciones. Figura PNG revisada visualmente. El servidor local arrancó, pero la revisión visual de la aplicación en el navegador integrado no pudo completarse por una falla de conexión de la herramienta.
