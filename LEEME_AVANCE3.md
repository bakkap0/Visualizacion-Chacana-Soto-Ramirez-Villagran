# Avance 3 · Pronóstico horario de MP2.5

Usamos el CSV del Avance 2, ubicado en `data/processed/dataset_horario_cqp_2023_2025.csv`. Si tienen el código en ZIP, descomprímanlo en la raíz del repositorio conservando la carpeta `src/`.

Desde la raíz, con Python 3.12 o posterior:

```powershell
python -m venv .venv-avance3
.\.venv-avance3\Scripts\python.exe -m pip install -r requirements-avance3.txt
.\.venv-avance3\Scripts\python.exe src/avance3_pipeline.py
```

El script guarda la tabla de métricas, el resumen de resultados y las figuras en `reports/avance3/`. Las opciones `--data` y `--out` permiten usar otras rutas. La opción `--jobs 1` ejecuta el bosque con un solo proceso de trabajo.

## Evaluación

- Pronosticamos el MP2.5 de la hora siguiente suponiendo que tenemos la medición de la hora previa. Calculamos los rezagos por estación y hora exacta. La media móvil usa las seis horas anteriores.
- Comparamos Ridge y Random Forest con las mismas entradas y usamos la última medición de MP2.5 como referencia. Validamos con cinco cortes cronológicos en 2023–2024 y reservamos 2025 para la prueba.
- Elegimos el modelo con menor RMSE medio de validación. Estimamos los valores SHAP con 40 permutaciones y filas de entrenamiento como referencia. Comprobamos que el valor base y los aportes sumen la predicción de cada caso.
- Se probó con Python 3.14.6, NumPy 2.4.6, pandas 3.0.3, Matplotlib 3.11.0 y scikit-learn 1.9.0.

La presentación PPTX es el archivo para entregar. Estos archivos permiten reproducir la evidencia.
