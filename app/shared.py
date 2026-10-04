from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import eda

@st.cache_data
def dataset():
    return eda.load_data()

def setup(title):
    st.set_page_config(page_title=f'{title} · Aire CQP', page_icon='🌊', layout='wide')
    st.title(title)
    st.caption('Calidad del aire · Concón, Quintero y Puchuncaví · 2023–2025')
    st.info('Análisis exploratorio de registros SINCA no validados. Las concentraciones publicadas pueden revisarse. Las figuras no acreditan incumplimientos normativos.')

def controls():
    df = dataset()
    st.sidebar.header('Selección del análisis')
    variable = st.sidebar.selectbox('Contaminante', list(eda.VARIABLES),
                                    format_func=lambda v: eda.VARIABLES[v][0], key='variable')
    stations = st.sidebar.multiselect('Estaciones', eda.STATIONS, default=eda.STATIONS, key='stations')
    dates = st.sidebar.date_input('Periodo', value=(df.fecha_hora.min().date(), df.fecha_hora.max().date()),
                                  min_value=df.fecha_hora.min().date(), max_value=df.fecha_hora.max().date(), key='dates')
    validated = st.sidebar.checkbox('Solo registros validados', value=False, key='validated')
    st.sidebar.caption('No hay mediciones de contaminantes clasificadas como validadas en esta descarga. El filtro permite comprobar esa limitación.')
    if not stations or len(dates) != 2:
        st.warning('Selecciona al menos una estación y las dos fechas del periodo.')
        st.stop()
    selected = eda.select_data(df, variable, stations, dates[0], dates[1], validated)
    if selected.empty:
        st.warning('No hay filas en el periodo seleccionado.')
        st.stop()
    return selected, variable

def require_values(df, variable):
    if df[variable].notna().sum() == 0:
        st.warning('La selección no tiene mediciones disponibles. Amplía el periodo o desactiva el filtro de registros validados.')
        st.stop()

def chart(fig, key):
    st.plotly_chart(fig, width='stretch', key=key)

def comparison(df, variable):
    matched = st.checkbox('Comparar usando solo horas con mediciones en todas las estaciones seleccionadas', value=True)
    data = eda.common_hours(df, variable) if matched else df
    st.caption(f'Comparación: {data.fecha_hora.nunique():,} horas distintas. ' +
               ('Las estaciones comparten exactamente las mismas horas.' if matched else 'Las estaciones pueden tener coberturas diferentes.'))
    require_values(data, variable)
    return data

