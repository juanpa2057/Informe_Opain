#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import json
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


# In[3]:


periodo_de_estudio = cfg.STUDY


# In[4]:


def show_response_contents(df):
    print("The response contains:")
    print(json.dumps(list(df['variable'].unique()), sort_keys=True, indent=4))
    print(json.dumps(list(df['device'].unique()), sort_keys=True, indent=4))


# In[5]:


DEVICE_NAME = 'Reporte Energía Opain'


# In[6]:


df = pd.read_pickle(project_path / 'data' / _PICKLED_DATA_FILENAME)
#df = df.query("device_name == @DEVICE_NAME")
show_response_contents(df)


# In[7]:


df = df.sort_values(by=['variable','datetime'])
df = pro.datetime_attributes(df)


# In[8]:


df = df[df['month'] !=1 ]


# In[9]:


# The most important variables for the report are created
ea_total = df.query("variable== 'ea-consumo-total-hora'").copy()
ea_sistema_hvac = df.query("variable== 'ea-control-sistema-hvac-hora'").copy()
ea_tablero_normal = df.query("variable== 'ea-oficinas-tablero-normal-hora'").copy()
ea_tablero_regulado = df.query("variable== 'ea-oficinas-tablero-regulado-hora'").copy()


# In[10]:


#This step is to clean the data
ea_total = cln.remove_outliers_by_zscore(ea_total, zscore=4)
ea_sistema_hvac = cln.remove_outliers_by_zscore(ea_sistema_hvac, zscore=4)
ea_tablero_normal = cln.remove_outliers_by_zscore(ea_tablero_normal, zscore=4)
ea_tablero_regulado = cln.remove_outliers_by_zscore(ea_tablero_regulado, zscore=4)

df_ea = df.copy()
df_ea = cln.remove_outliers_by_zscore(df_ea, zscore=3)


# In[11]:


df_month = df_ea.groupby(by=["variable"]).resample('M').sum().reset_index().set_index('datetime')
df_month = pro.datetime_attributes(df_month)

ea_diaria = df_ea.groupby(by=["variable"]).resample('D').sum().reset_index().set_index('datetime')
ea_diaria = pro.datetime_attributes(ea_diaria)

df_ea['value'] = df_ea['value'].round(2)
df_ea = df_ea.groupby(["hour", "dow"])["value"].mean().reset_index()


# In[12]:


df_ea['value'] = df_ea['value'].round(2)
df_ea = df_ea.groupby(["hour", "dow"])["value"].mean().reset_index()


# In[13]:


valores_a_buscar = [
    "ea-consumo-total-hora",
    "ea-control-sistema-hvac-hora",
    "ea-oficinas-tablero-normal-hora",
    "ea-oficinas-tablero-regulado-hora"
]

mapeo = {
    "ea-consumo-total-hora": 'Consumo Energía Total Medido',
    "ea-control-sistema-hvac-hora": "Consumo Energía Sistema HVCA",
    "ea-oficinas-tablero-normal-hora": "Consumo Energía Tablero Normal",
    "ea-oficinas-tablero-regulado-hora": "Consumo Energía Tablero Regulado"

}


# In[14]:


df_month = df_month[df_month['variable'].isin(valores_a_buscar)]
ea_diaria = ea_diaria[ea_diaria['variable'].isin(valores_a_buscar)]


# In[15]:


ea_diaria['month_day'] = ea_diaria['month'].astype(str) + '-' + ea_diaria['day'].astype(str)
ea_diaria = ea_diaria.sort_values('datetime')

# Agregamos los valores de las dos variables por month_day
agg_df = ea_diaria.groupby(['month_day', 'variable'])['value'].sum().reset_index()


# ## Informe Consumos de energía

# A continuacíon se presenta un informe del monitoreo energetico llevado en Opain desde el 11 noviembre al 31 diciemmbre 2023

# In[16]:


ea_diaria['variable'] = ea_diaria['variable'].replace(mapeo)


list_vars = [
    "Consumo energía total Medido",
    "Consumo energía Sistema HVCA",
    "Consumo energía Tablero normal",
    "Consumo energía Tablero Regulado"
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    df_var = ea_diaria.query("variable == @variable")
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
    title=f"{DEVICE_NAME}: Consumo de energía activa [kWh]",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Consumo Activa [kWh]")
)

fig.update_traces(mode='lines')
# fig.update_xaxes(rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# El gráfico muestra el consumo de energía activa en kWh del 11 de noviembre al 31 de diciembre de 2023, con la línea naranja representando el consumo total y gráficos distintos para las áreas HVCA, Consumo tablero normal y Regulado. El consumo total destaca alrededor de 300 kWh/día, el control HVCA se mantiene bajo 200 kWh/día, y las oficinas oscilan alrededor de 50 kWh/día, ofreciendo una clara visión del patrón de consumo y diferencias entre las áreas.

# In[17]:


df_month['variable'] = df_month['variable'].replace(mapeo)

#df_month = df_month.query("month != 1 and variable != 'ea-consumo-total-hora'")
# Ordenar el DataFrame por variable y mes de manera descendente
df_month = df_month.sort_values(by=['variable', 'month'], ascending=[True, False])

# Redondear y formatear los valores sin decimales
df_month['value_formatted'] = df_month['value'].round(0).apply(lambda x: f'{x:,.0f}')

# Crear la tabla
fig = go.Figure(data=[go.Table(
    header=dict(values=['Proceso', 'Consumo Energía (kWh)', 'Mes']),
    cells=dict(values=[df_month['variable'], 
                       df_month['value_formatted'],  # Usar los valores formateados
                       df_month['month']]))
])

# Ajustar el diseño y formato
fig.update_layout(
    title='Datos de Consumo de Energía por Mes',
    font=dict(size=13),  # Ajustar el tamaño del texto
    template='plotly_white'  # Cambiar el tema a plotly_white
)

# Mostrar la tabla
fig.show()


# Se representa el consumo acumulado de energía en kWh por area durante los meses de noviembre y diciembre del 2023:
# 
# - Energía Tablero Nomal: Esta area tiene la mayor parte del consumo con un 73% del total.
# 
# - Energía Sistema HVCA: Esta area tiene el segundo mayor consumo con un 18% del total.
# 
# - Energía Tablero Regulado: Esta area el restante del consumo con un 8.7% del total.

# In[18]:


# Agrupar por area y sumar la energía
df_grouped = df_month.groupby('variable').sum().reset_index()
df_grouped = df_grouped[(df_grouped['variable'] != 'Consumo energía total Medido')]



# Crear el gráfico de torta
fig = px.pie(df_grouped, values='value', names='variable', 
             title='Distribución del Consumo de Energía por Area',
             labels={'variable': 'Máquina', 'value': 'Consumo de Energía'},
             color_discrete_sequence=px.colors.qualitative.Set1)

# Habilitar la interactividad para agregar/quitar máquinas
fig.update_traces(hoverinfo='label+percent', textinfo='value+percent', pull=[0.1]*len(df_grouped))

# Mostrar el gráfico
fig.show()


# Al analizar las tres áreas medidas, se observa que el "Tablero Normal" representa el mayor porcentaje en el consumo de energía. Es importante destacar que de todo el consumo acumulado el 73% se concentra en esta área. Esto sugiere que un manejo eficiente y control del sistema de aire acondicionado podrían resultar en una mayor eficiencia en el consumo de energía."

# In[19]:


fig = px.box(df_ea, x="dow", y="value", color="dow", points='all', category_orders={"dow": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]})
fig.update_layout(
    title='Consumo por tipo de día',
    width=800,
    height=600,
    yaxis_title="Consumo kWh",
    title_font_size=12,
    xaxis_title="Día"
)


# Se puede notar que el 'martes' es el rango más amplio de consumo energético en la semana. Por otro lado, el 'sábado' y el 'domingo' presentan un patrón de consumo  más bajos, lo que podría sugerir una menor demanda de energía durante los fines de semana. Este análisis detallado del patrón de consumo por día.

# In[27]:


import pandas as pd

# Calcular el promedio por combinación de hour y dow
promedio_por_hora_dia = df_ea.groupby(['hour', 'dow'])['value'].mean().reset_index()



# In[21]:


import pandas as pd

# Supongamos que tu DataFrame se llama ea_total
# Si ya tienes definido el DataFrame, no necesitas esta línea
# ea_total = ...

# Convertir la columna 'datetime' al formato adecuado (si aún no está en datetime)
#ea_total['datetime'] = pd.to_datetime(ea_total['datetime'])

# Agrupar por día de la semana y hora, calcular el promedio de 'value'
ea_avg_per_day_hour = ea_total.groupby(['dow', 'hour'])['value'].mean().reset_index()

# Puedes ajustar el índice si lo prefieres
# ea_avg_per_day_hour = ea_avg_per_day_hour.set_index(['dow', 'hour'])

# Imprimir el nuevo DataFrame con el promedio por día y hora


