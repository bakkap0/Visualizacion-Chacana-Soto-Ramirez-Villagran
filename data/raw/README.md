# Datos crudos (raw)

Los datos originales no se incluyen directamente en este repositorio porque:
- Requieren selección manual por estación en el portal SINCA.
- El volumen histórico puede ser pesado para GitHub.

## Cómo obtener los datos

1. Ir a https://sinca.mma.gob.cl/ → apretar la estacion que queremos y luego al seleccionar nos saldra para "Descarga de datos" (o directamente a https://airecqp.mma.gob.cl/ para la red específica de Concón-Quintero-Puchuncaví).
2. Seleccionar las estaciones de interés (ej. Ventanas, La Greda, Quintero Centro, Concón Oeste) y si queremos ver todos los datos historicos tenemos que ingresar a https://sinca.mma.gob.cl/index.php/region/index/id/V 
3. Seleccionar los contaminantes: MP2.5, MP10, SO2 (y variables meteorológicas si están disponibles).
4. Seleccionar el rango de fechas: 2023-01-01 a 2025-12-31.
5. Descargar el archivo (CSV/XLSX) y guardarlo en esta carpeta con el nombre `estacion_contaminante_periodo.csv`.


