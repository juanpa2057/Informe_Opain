#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import json
import holidays
from datetime import datetime

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

pio.renderers.default = "notebook"
pio.templates.default = "plotly_white"


# this enables relative path imports
import os
from dotenv import load_dotenv
load_dotenv()
_PROJECT_PATH: str = os.environ["_project_path"]
_PICKLED_DATA_FILENAME: str = os.environ["_pickled_data_filename"]

import sys
from pathlib import Path
project_path = Path(_PROJECT_PATH)
sys.path.append(str(project_path))

import config_v2 as cfg


from library_report_v2 import Cleaning as cln
from library_report_v2 import Graphing as grp
from library_report_v2 import Processing as pro
from library_report_v2 import Configuration as repcfg


# In[2]:


import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

periodo_de_estudio = cfg.STUDY


# In[3]:


def show_response_contents(df):
    print("The response contains:")
    print(json.dumps(list(df['variable'].unique()), sort_keys=True, indent=4))
    print(json.dumps(list(df['device'].unique()), sort_keys=True, indent=4))


df = pd.read_pickle(project_path / 'data' / _PICKLED_DATA_FILENAME)
#df = df.query("device_name == @DEVICE_NAME")
#show_response_contents(df)


# In[4]:


df = df.sort_values(by=['variable','datetime'])
df = pro.datetime_attributes(df)


# In[5]:


# The most important variables for the report are created
ea_tablero = df.query("variable== 'ea-control-sistema-hvac-hora'").copy()
fp_tablero = df.query("variable== 'factor-de-potencia'").copy()
corriente_1 = df.query("variable== 'corriente-l1-hvac'").copy()
corriente_2 = df.query("variable== 'corriente-l2-hvac'").copy()
corriente_3 = df.query("variable== 'corriente-l3-hvac'").copy()
tension_1 = df.query("variable== 'tension-fase-l1-hvac'").copy()
tension_2 = df.query("variable== 'tension-fase-l2-hvac'").copy()
tension_3 = df.query("variable== 'tension-fase-l3-hvac'").copy()


# In[6]:


#This step is to clean the data
ea_tablero = cln.remove_outliers_by_zscore(ea_tablero, zscore=3)
fp_tablero = cln.remove_outliers_by_zscore(fp_tablero, zscore=3)
corriente_1 = cln.remove_outliers_by_zscore(corriente_1, zscore=3)
corriente_2 = cln.remove_outliers_by_zscore(corriente_2, zscore=3)
corriente_3 = cln.remove_outliers_by_zscore(corriente_3, zscore=3)
tension_1 = cln.remove_outliers_by_zscore(tension_1, zscore=3)
tension_2 = cln.remove_outliers_by_zscore(tension_2, zscore=3)
tension_3 = cln.remove_outliers_by_zscore(tension_3, zscore=3)


# In[7]:


ea_tablero_h = ea_tablero.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
ea_tablero_h = pro.datetime_attributes(ea_tablero_h)

ea_tablero_d = ea_tablero.groupby(by=["variable"]).resample('D').sum().reset_index().set_index('datetime')
ea_tablero_d = pro.datetime_attributes(ea_tablero_d)

fp_tablero_h = fp_tablero.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
fp_tablero_h = pro.datetime_attributes(fp_tablero_h)

corriente_1_h = corriente_1.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
corriente_1_h = pro.datetime_attributes(corriente_1_h)

corriente_2_h = corriente_2.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
corriente_2_h = pro.datetime_attributes(corriente_2_h)

corriente_3_h = corriente_3.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
corriente_3_h = pro.datetime_attributes(corriente_3_h)

tension_1_h = tension_1.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
tension_1_h = pro.datetime_attributes(tension_1_h)

tension_2_h = tension_2.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
tension_2_h = pro.datetime_attributes(tension_2_h)

tension_3_h = tension_3.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
tension_3_h = pro.datetime_attributes(tension_3_h)


# ## Control Sistema HVAC

# Analizaremos la carga Tablero normal Oficinas la cual tuvo un consumo de energía:
# - Noviembre: 814 kWh/mes
# - Diciembre: 1,454 kWh/mes

# In[8]:


ea_tablero_d = ea_tablero_d[ea_tablero_d['month'] !=1 ]
ea_tablero_d = ea_tablero_d[ea_tablero_d['month'] !=11 ]
ea_tablero_d['month_day'] = ea_tablero_d['month'].astype(str) + '-' + ea_tablero_h['day'].astype(str)
ea_tablero_d = ea_tablero_d.sort_values('datetime')

# Agregamos los valores de las dos variables por month_day
agg_df = ea_tablero_d.groupby(['month_day', 'variable'])['value'].sum().reset_index()


# In[9]:


fig = px.bar(
    ea_tablero_d,
    x="month_day",
    y="value",
    barmode='group',
    color='variable',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'month_day':'Mes - Día', 'value':'Consumo [kWh]'},
    title=f"Consumo de Energía Activa Diario [kWh]",
)
 
 
# Ajustamos la escala y el formato del eje x
fig.update_xaxes(
    type='category',  # Usar una escala categórica en lugar de fecha
    tickvals=list(agg_df['month_day']),  # Valores en el eje x
    ticktext=list(agg_df['month_day']),  # Etiquetas en el eje x
    title_text='Mes - Día',  # Título del eje x
)
 
fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)
 
fig.show()


# In[10]:


print(f'La Carga presenta consumos máximo de {ea_tablero_d["value"].max():.2f} kWh/día y mínimo de {ea_tablero_d["value"].min():.2f} kWh/día. \nAunque la carga es variable, los valores medios son de alrededor de {ea_tablero_d["value"].mean():.2f} kWh/día.')


# In[11]:


#fp_tablero_h['value'] = fp_tablero_h['value'].round(2)

fig = px.box(
    fp_tablero_h,
    y="value",
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day': 'Día', 'value': 'Consumo [kWh/día]'},
    title="Factor de potencia promedio"
)

fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)

fig.show()


# In[12]:


# Filtrar los valores de 'value' que sean mayores que 0
valores_positivos = fp_tablero_h['value'][fp_tablero_h['value'] > 0]

# Calcular el promedio de los valores positivos
promedio_positivos = valores_positivos.mean().round(2)



# In[13]:


print("El Factor de Potencia Promedio es de", promedio_positivos, "lo cual es un fp bajo")


# In[14]:


df_plot = pd.concat([corriente_1_h, corriente_2_h, corriente_3_h])

df_plot['value'] = df_plot['value'].round(2)

df_plot = df_plot[df_plot['month'] !=1 ]
df_plot = df_plot[df_plot['month'] !=11 ]

list_vars = [
    'corriente-l1-hvac',
    'corriente-l2-hvac',
    'corriente-l3-hvac'
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    df_var = df_plot.query("variable == @variable")
    hex_color = repcfg.FULL_PALETTE[idx % len(repcfg.FULL_PALETTE)]
    rgba_color = grp.hex_to_rgb(hex_color, alpha)
    idx += 1

    if (len(df_var) > 0):
        fig.add_trace(go.Scatter(
            x=df_var.index,
            y=df_var.value,
            line_color=rgba_color,
            name=variable,
            showlegend=True,
        ))



fig.update_layout(
    title=f" Corrientes Tablero Normal [A]",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Corrientes [A]")
)

fig.update_traces(mode='lines')
# fig.update_xaxes(rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# In[15]:


# Utiliza pivot_table para pivotear la columna 'variable' y mostrar los valores de 'value'
desbalance_c = df_plot.pivot_table(values='value', columns='variable', index='datetime')

desbalance_c['promedio'] = desbalance_c[['corriente-l1-hvac', 'corriente-l2-hvac', 'corriente-l3-hvac']].mean(axis=1).round(2)

# Calcular el valor promedio
promedio = desbalance_c['promedio']

# Calcular el valor mínimo de las columnas 'corriente-l1', 'corriente-l2' y 'corriente-l3'
min_values = desbalance_c[['corriente-l1-hvac', 'corriente-l2-hvac', 'corriente-l3-hvac']].min(axis=1)

# Calcular el desbalance utilizando la fórmula dada
desbalance_c['desbalance_corriente'] = ((promedio - min_values) / promedio) * 100

desbalance_c['desbalance_corriente'] = desbalance_c['desbalance_corriente'].round(2)



# In[16]:


df_tension= pd.concat([tension_1_h, tension_2_h, tension_3_h])

df_tension['value'] = df_tension['value'].round(2)

df_tension = df_tension[df_tension['month'] !=1 ]
df_tension = df_tension[df_tension['month'] !=11 ]

list_vars = [
    'tension-fase-l1-hvac',
    'tension-fase-l1-hvac',
    'tension-fase-l1-hvac'
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    df_var = df_tension.query("variable == @variable")
    hex_color = repcfg.FULL_PALETTE[idx % len(repcfg.FULL_PALETTE)]
    rgba_color = grp.hex_to_rgb(hex_color, alpha)
    idx += 1

    if (len(df_var) > 0):
        fig.add_trace(go.Scatter(
            x=df_var.index,
            y=df_var.value,
            line_color=rgba_color,
            name=variable,
            showlegend=True,
        ))



fig.update_layout(
    title=f" Tensiones Tablero Normal [V]",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Tensiones [V]")
)

fig.update_traces(mode='lines')
fig.update_yaxes(range=[110, 130], rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# In[17]:


# Utiliza pivot_table para pivotear la columna 'variable' y mostrar los valores de 'value'
desbalance_t = df_tension.pivot_table(values='value', columns='variable', index='datetime')

desbalance_t['promedio'] = desbalance_t[['tension-fase-l1-hvac', 'tension-fase-l2-hvac', 'tension-fase-l3-hvac']].mean(axis=1).round(2)

# Calcular el valor promedio
promedio_t = desbalance_t['promedio']

# Calcular el valor mínimo de las columnas 'corriente-l1', 'corriente-l2' y 'corriente-l3'
min_values_t = desbalance_t[['tension-fase-l1-hvac', 'tension-fase-l2-hvac', 'tension-fase-l3-hvac']].min(axis=1)

# Calcular el desbalance utilizando la fórmula dada
desbalance_t['desbalance_tension'] = ((promedio_t - min_values_t) / promedio_t) * 100

desbalance_t['desbalance_tension'] = desbalance_t['desbalance_tension'].round(2)




# In[18]:


df_desbalance= pd.concat([desbalance_c, desbalance_t])

list_vars = [
    'desbalance_corriente',
    'desbalance_tension'
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    # Filtrar el DataFrame para obtener las filas con valores no nulos en la columna deseada
    df_var = df_desbalance.dropna(subset=[variable])
    hex_color = repcfg.FULL_PALETTE[idx % len(repcfg.FULL_PALETTE)]
    rgba_color = grp.hex_to_rgb(hex_color, alpha)
    idx += 1

    if (len(df_var) > 0):
        fig.add_trace(go.Scatter(
            x=df_var.index,
            y=df_var[variable],  # Acceder a la columna deseada
            line_color=rgba_color,
            name=variable,
            showlegend=True,
        ))

# Configuración del diseño del gráfico
fig.update_layout(
    title=f"Desbalance de Cargas",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Amperio [A] - Tensión [V]"), 
)

fig.update_traces(mode='lines')
# fig.update_xaxes(rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# Al analizar la gráfica de tendencia, se observa un desequilibrio de corriente superior al 20%; sin embargo, no se detecta un desequilibrio en la tensión que exceda los umbrales recomendados. Se sugiere realizar un balance de carga para reducir el desequilibrio de corriente. Aunque este desequilibrio no afecta actualmente el funcionamiento de los equipos, es importante considerarlo para futuras ampliaciones o repotenciaciones de las cargas
