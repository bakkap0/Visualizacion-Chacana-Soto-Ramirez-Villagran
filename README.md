# Calidad del Aire en Concón, Quintero y Puchuncaví

Proyecto del curso **EIN092B Visualización** — UTFSM, Profesor Jesús A. Parra, Proyecto 2026-II.

## Integrantes

- Chacana [Nombre]
- Soto [Nombre]
- Ramírez [Nombre]
- Villagrán [Nombre]

> *(Completar con nombres completos y, si se requiere, correos institucionales)*

## Descripción breve del problema

Concón, Quintero y Puchuncaví conforman lo que comúnmente se conoce como una **"zona de sacrificio"** ambiental de Chile: una zona con alta concentración de industria pesada (termoeléctricas, refinerías, fundiciones) que ha registrado episodios recurrentes de contaminación atmosférica, incluyendo intoxicaciones masivas desde 2018. A pesar de que existe un Plan de Prevención y Descontaminación Atmosférica (PPDA) vigente desde 2019 y una nueva red pública de monitoreo implementada entre 2024 y 2025, sigue siendo difícil para la comunidad y las autoridades locales visualizar de forma clara cuándo, dónde y bajo qué condiciones empeora la calidad del aire en la zona.

## Motivación

Parte del equipo es de Quintero y ha vivido de cerca la preocupación por los episodios de contaminación en la zona. Creemos que transformar los datos de monitoreo —hoy dispersos entre varias estaciones y portales— en visualizaciones claras puede ayudar a que la comunidad, la prensa y las autoridades entiendan mejor los patrones de contaminación y apoyen la toma de decisiones del PPDA.

## Pregunta inicial

> ¿Cómo varían las concentraciones de contaminantes atmosféricos (MP2.5, MP10, SO2) según estación de monitoreo, hora del día y condiciones meteorológicas, y qué comunas/estaciones presentan mayor frecuencia de episodios críticos, durante el período 2023–2025?

**Estructura X, Y, T:**

| Componente | Descripción |
|---|---|
| **X** (información disponible) | Estación de monitoreo, comuna, hora del día, día de la semana, temperatura, velocidad/dirección del viento, humedad |
| **Y** (objetivo) | Concentración de MP2.5, MP10 y SO2; número de episodios sobre norma |
| **T** (contexto temporal) | 2023–2025, con foco en comparar el período previo y posterior a la entrada en operación de la nueva red pública (2024–2025) |

## Alcance

- **Fenómeno específico:** niveles de MP2.5, MP10 y SO2 (los contaminantes históricamente más críticos en la zona).
- **Unidad de observación:** medición horaria/diaria por estación de monitoreo.
- **Población/contexto:** comunas de Concón, Quintero y Puchuncaví.
- **Periodo:** 2023–2025.
- **Estaciones foco:** un subconjunto representativo (ej. Ventanas, La Greda, Quintero Centro, Concón Oeste), en vez de las 14 estaciones completas, para mantener el análisis manejable durante el semestre.
- **Fuera de alcance (por ahora):** modelamiento predictivo, contaminantes no normados, comparación con otras zonas del país.

## Fuente del dataset

- **Portal Aire Concón–Quintero–Puchuncaví** (Ministerio del Medio Ambiente): https://airecqp.mma.gob.cl/ — red pública de 14 estaciones de monitoreo (5 en Quintero, 5 en Puchuncaví, 4 en Concón), con datos en línea de SO2, NO2, CO, O3, MP10 y MP2.5.
- **SINCA – Sistema de Información Nacional de Calidad del Aire**: https://sinca.mma.gob.cl/ — permite descargar series históricas por estación (incluye variables meteorológicas asociadas).

Ambas fuentes son datos públicos y abiertos del Estado de Chile. La descarga histórica se realiza estación por estación desde el sitio de SINCA (sección "Descarga de datos"), seleccionando el período y los contaminantes de interés.

## Breve descripción de los datos

- **Qué representa una observación:** una medición horaria (o promedio móvil de 24h para MP10/MP2.5) de un contaminante en una estación específica.
- **Variables principales:** fecha/hora, estación, comuna, contaminante, concentración, y variables meteorológicas asociadas (temperatura, viento, humedad) cuando estén disponibles.
- **Cobertura temporal:** se buscará reunir datos desde 2023 en adelante; la nueva red pública opera con datos completos recién desde 2024–2025, por lo que se evaluará complementar con datos de la red privada histórica.
- **Cobertura espacial:** hasta 14 estaciones distribuidas en las tres comunas, geolocalizadas (lat/lon).
- **Historia que se busca explorar:** identificar patrones horarios/estacionales de contaminación, comparar comunas y estaciones, y visibilizar la frecuencia de episodios que superan la norma.

## Estructura general del repositorio

```
Vizualizacion-Chacana-Soto-Ramirez-Villagran/
|
|-- data/
|   |-- raw/            # datos originales descargados de SINCA / airecqp, sin modificar
|   `-- processed/      # datos limpios y transformados
|
|-- notebooks/
|   `-- 01_exploracion.ipynb
|
|-- src/                # funciones y código reutilizable
|
|-- figures/             # gráficos y recursos visuales generados
|
|-- app/                 # futura aplicación Streamlit / dashboard
|
|-- README.md
`-- .gitignore
```

> **Nota sobre los datos:** dado que las descargas históricas de SINCA pueden ser pesadas o requerir selección manual por estación, no se incluyen directamente en `data/raw/`. En su lugar, `data/raw/README.md` documentará el procedimiento exacto de descarga (URL, estaciones, contaminantes y rango de fechas seleccionados) para que el proceso sea reproducible por cualquier integrante del equipo o el profesor.

---

*Este README corresponde al Avance 1 (Formulación del proyecto). Se espera que evolucione con los siguientes avances: EDA y visualización, producto analítico, y presentación final.*
