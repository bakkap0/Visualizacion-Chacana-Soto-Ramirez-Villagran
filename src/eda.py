"""Análisis descriptivo compartido por el notebook y la aplicación."""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
VARIABLES = {
    'mp25_ug_m3': ('MP2.5', 'µg/m³'),
    'mp10_ug_m3n': ('MP10', 'µg/m³N'),
    'so2_ppb': ('SO₂', 'ppb'),
}
STATIONS = ['Centro Quintero', 'Concón', 'La Greda', 'Ventanas']
COLORS = dict(zip(STATIONS, ['#147D92', '#BD622A', '#7965AA', '#315CB2']))
METEOROLOGY = {
    'velocidad_viento_m_s': ('Velocidad del viento', 'm/s'),
    'temperatura_c': ('Temperatura, solo Concón', '°C'),
    'humedad_relativa_pct': ('Humedad relativa, solo Concón', '%'),
}
QUESTION = ('¿Cómo varían las concentraciones horarias de MP2.5, MP10 y SO₂ entre '
            'Ventanas, La Greda, Centro Quintero y Concón, según hora del día, época '
            'del año y condiciones meteorológicas disponibles, durante 2023–2025?')

def load_data():
    return pd.read_csv(ROOT / 'data/processed/dataset_horario_cqp_2023_2025.csv',
                       parse_dates=['fecha_hora'], low_memory=False)

def select_data(df, variable, stations=None, start=None, end=None, only_validated=False):
    out = df.copy()
    if stations is not None:
        out = out[out.estacion.isin(stations)]
    if start is not None:
        out = out[out.fecha_hora >= pd.Timestamp(start)]
    if end is not None:
        out = out[out.fecha_hora < pd.Timestamp(end) + pd.Timedelta(days=1)]
    if only_validated:
        out.loc[out[variable + '_estado'].ne('validado'), variable] = np.nan
    return out

def common_hours(df, variable):
    """Misma población temporal para las estaciones seleccionadas, sin imputar."""
    if df.empty:
        return df.copy()
    pivot = df.pivot(index='fecha_hora', columns='estacion', values=variable)
    times = pivot.dropna().index
    return df[df.fecha_hora.isin(times)].copy()

def station_summary(df, variable):
    summary = df.groupby('estacion', observed=True)[variable].agg(
        horas_esperadas='size', n='count', media='mean', mediana='median',
        desviacion='std', minimo='min', maximo='max')
    summary['p95'] = df.groupby('estacion', observed=True)[variable].quantile(.95)
    summary['cobertura_pct'] = 100 * summary.n / summary.horas_esperadas
    return summary.reset_index()

def daily_values(df, variable, minimum_hours=18):
    out = df.assign(fecha=df.fecha_hora.dt.floor('D')).groupby(
        ['estacion', 'fecha'], observed=True)[variable].agg(media='mean', n='count').reset_index()
    out.loc[out.n < minimum_hours, 'media'] = np.nan
    return out

def monthly_coverage(df, variable):
    d = df.assign(periodo=df.fecha_hora.dt.strftime('%Y-%m'))
    out = d.groupby(['estacion', 'periodo'], observed=True)[variable].agg(
        n='count', esperadas='size').reset_index()
    out['cobertura_pct'] = 100 * out.n / out.esperadas
    return out

def hourly_profile(df, variable, minimum_hours=24):
    out = df.groupby(['estacion', 'hora'], observed=True)[variable].agg(
        mediana='median', n='count').reset_index()
    out.loc[out.n < minimum_hours, 'mediana'] = np.nan
    return out

def relationships(df, variable, predictor='velocidad_viento_m_s'):
    rows = []
    for station, g in df.groupby('estacion', observed=True):
        pair = g[[variable, predictor]].dropna()
        # Spearman = Pearson de rangos medios; evita una dependencia adicional.
        rho = pair.rank(method='average').corr().iloc[0, 1] if len(pair) >= 3 else np.nan
        rows.append({'estacion': station, 'n_pares': len(pair), 'spearman': rho})
    return pd.DataFrame(rows)

def style(fig, y_label=None):
    fig.update_layout(template='plotly_white', font=dict(family='Arial', size=14),
                      height=460, margin=dict(l=60, r=30, t=65, b=65),
                      legend_title_text='Estación', hovermode='closest')
    if y_label:
        fig.update_yaxes(title=y_label)
    return fig

def axis_label(variable):
    label, unit = VARIABLES[variable]
    return f'{label} ({unit})'

def coverage_chart(df, variable):
    out = monthly_coverage(df, variable)
    pivot = out.pivot(index='estacion', columns='periodo', values='cobertura_pct')
    fig = px.imshow(pivot, zmin=0, zmax=100, aspect='auto', color_continuous_scale='Blues',
                    labels=dict(x='Mes', y='Estación', color='Cobertura (%)'),
                    title=f'Cobertura mensual de {VARIABLES[variable][0]}')
    fig.update_traces(hovertemplate='%{y}<br>%{x}<br>Cobertura: %{z:.1f}%<extra></extra>')
    return style(fig)

def histogram_chart(df, variable):
    fig = px.histogram(df.dropna(subset=[variable]), x=variable, color='estacion',
                       histnorm='percent', nbins=60, opacity=.55, barmode='overlay',
                       color_discrete_map=COLORS,
                       labels={variable: axis_label(variable), 'estacion': 'Estación'},
                       title=f'Distribución horaria de {VARIABLES[variable][0]}')
    fig.update_traces(bingroup='concentracion')
    return style(fig, 'Porcentaje dentro de cada estación (%)')

def box_chart(df, variable):
    fig = px.box(df, x='estacion', y=variable, color='estacion', points=False,
                 color_discrete_map=COLORS, category_orders={'estacion': STATIONS},
                 labels={'estacion': 'Estación', variable: axis_label(variable)},
                 title=f'Concentraciones de {VARIABLES[variable][0]} por estación')
    fig.update_layout(showlegend=False)
    return style(fig)

def daily_chart(df, variable, minimum_hours=18):
    out = daily_values(df, variable, minimum_hours)
    fig = px.line(out, x='fecha', y='media', color='estacion', color_discrete_map=COLORS,
                  custom_data=['n'], labels={'fecha': 'Fecha', 'media': axis_label(variable)},
                  title=f'Media diaria exploratoria de {VARIABLES[variable][0]}')
    fig.update_traces(connectgaps=False, hovertemplate='%{x|%d-%m-%Y}<br>Media: %{y:.2f}<br>Horas: %{customdata[0]}<extra>%{fullData.name}</extra>')
    return style(fig)

def hourly_chart(df, variable):
    out = hourly_profile(df, variable)
    fig = px.line(out, x='hora', y='mediana', color='estacion', markers=True,
                  color_discrete_map=COLORS, custom_data=['n'],
                  labels={'hora': 'Hora según SINCA', 'mediana': axis_label(variable)},
                  title=f'Perfil horario mediano de {VARIABLES[variable][0]}')
    fig.update_xaxes(dtick=2, range=[0, 23])
    fig.update_traces(connectgaps=False, hovertemplate='Hora: %{x}<br>Mediana: %{y:.2f}<br>Observaciones: %{customdata[0]}<extra>%{fullData.name}</extra>')
    return style(fig)

def month_hour_chart(df, variable, station, minimum_hours=12):
    out = df[df.estacion.eq(station)].groupby(['mes', 'hora'], observed=True)[variable].agg(
        mediana='median', n='count').reset_index()
    out.loc[out.n < minimum_hours, 'mediana'] = np.nan
    matrix = out.pivot(index='mes', columns='hora', values='mediana').reindex(index=range(1,13),columns=range(24))
    counts = out.pivot(index='mes', columns='hora', values='n').reindex(index=range(1,13),columns=range(24))
    fig = go.Figure(go.Heatmap(z=matrix.to_numpy(), x=list(range(24)), y=list(range(1,13)),
                  colorscale='YlOrRd', customdata=counts.to_numpy(),
                  colorbar=dict(title=axis_label(variable)),
                  hovertemplate='Mes: %{y}<br>Hora: %{x}<br>Mediana: %{z:.2f}<br>n: %{customdata}<extra></extra>'))
    fig.update_layout(title=f'{station}: mediana de {VARIABLES[variable][0]} por mes y hora')
    fig.update_xaxes(title='Hora según SINCA', dtick=2)
    fig.update_yaxes(title='Mes', dtick=1, autorange='reversed')
    return style(fig)

def scatter_chart(df, variable, predictor='velocidad_viento_m_s', max_per_station=1500):
    parts = []
    for _, g in df.dropna(subset=[variable, predictor]).groupby('estacion', observed=True):
        parts.append(g.sample(n=min(len(g), max_per_station), random_state=42))
    sample = pd.concat(parts) if parts else df.iloc[:0]
    label, unit = METEOROLOGY[predictor]
    fig = px.scatter(sample, x=predictor, y=variable, color='estacion', opacity=.4,
                     color_discrete_map=COLORS, hover_data=['fecha_hora'],
                     labels={predictor: f'{label} ({unit})', variable: axis_label(variable)},
                     title=f'{VARIABLES[variable][0]} y {label.lower()}')
    fig.update_traces(marker=dict(size=4))
    return style(fig)
