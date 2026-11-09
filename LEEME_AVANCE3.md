# Avance 3 · Pronóstico horario de MP2.5

Para incorporar el análisis a su copia del proyecto, descompriman esta actualización sobre la raíz del repositorio y conserven la carpeta `src/`. El CSV que ya viene en el repositorio debe seguir en `data/processed/dataset_horario_cqp_2023_2025.csv`.

Desde la raíz, con Python 3.12 o posterior:

```powershell
python -m venv .venv-avance3
.\.venv-avance3\Scripts\python.exe -m pip install -r requirements-avance3.txt
.\.venv-avance3\Scripts\python.exe src/avance3_pipeline.py
```

El script guarda la tabla de métricas, el resumen de resultados y las figuras en `reports/avance3/`. Las opciones `--data` y `--out` permiten usar otras rutas. La opción `--jobs 1` ejecuta el bosque con un solo proceso de trabajo.

## Evaluación

- Pronóstico de MP2.5 de la hora siguiente, suponiendo disponible la medición de la hora previa. Cada rezago usa la hora exacta y la misma estación. La media móvil excluye la hora objetivo.
- Ridge y Random Forest reciben las mismas entradas. La persistencia usa el MP2.5 de una hora antes como referencia. Los cinco cortes de validación separan por hora completa en 2023–2024. La prueba común es 2025.
- Se elige entre Ridge y Random Forest por el RMSE medio de validación. Los SHAP aproximan contribuciones mediante 40 permutaciones con un fondo tomado de entrenamiento. El script comprueba que el valor base y las contribuciones sumen a la predicción en cada caso.
- Se probó con Python 3.14.6, NumPy 2.4.6, pandas 3.0.3, Matplotlib 3.11.0 y scikit-learn 1.9.0.

La presentación PPTX es el archivo para entregar. Estos archivos permiten reproducir la evidencia.
