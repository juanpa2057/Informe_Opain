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


#df = df[df['month'] !=11 ]
df = df[df['month'] !=1 ]


# In[9]:


# The most important variables for the report are created
ea_total = df.query("variable== 'ea-consumo-total-hora'").copy()
ea_sistema_hvac = df.query("variable== 'ea-control-sistema-hvac-hora'").copy()
ea_tablero_normal = df.query("variable== 'ea-oficinas-tablero-normal-hora'").copy()
ea_tablero_regulado = df.query("variable== 'ea-oficinas-tablero-regulado-hora'").copy()


# In[10]:


#This step is to clean the data
ea_total = cln.remove_outliers_by_zscore(ea_total, zscore=3)
ea_sistema_hvac = cln.remove_outliers_by_zscore(ea_sistema_hvac, zscore=4)
ea_tablero_normal = cln.remove_outliers_by_zscore(ea_tablero_normal, zscore=4)
ea_tablero_regulado = cln.remove_outliers_by_zscore(ea_tablero_regulado, zscore=4)

df_ea = df.copy()
df_ea = cln.remove_outliers_by_zscore(df_ea, zscore=4)



# In[11]:


df_month = df_ea.groupby(by=["variable"]).resample('M').sum().reset_index().set_index('datetime')
df_month = pro.datetime_attributes(df_month)

ea_diaria = df_ea.groupby(by=["variable"]).resample('D').sum().reset_index().set_index('datetime')
ea_diaria = pro.datetime_attributes(ea_diaria)


ea_hour = df_ea.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
ea_hour = pro.datetime_attributes(ea_hour)

df_hora = ea_total.groupby(by=["variable"]).resample('H').mean().reset_index().set_index('datetime')
df_hora = pro.datetime_attributes(df_hora)

df_hora = df_hora[df_hora['month'] !=11 ]

#df_ea = df_ea.groupby(["hour", "dow"])["value"].mean().reset_index()
#df_ea['value'] = df_ea['value'].round(2)


# In[12]:


# Supongamos que df es tu DataFrame con índice datetime
df_hora['festivo'] = df_hora.index.to_series().apply(lambda x: x in holidays.Colombia())

# Supongamos que df es tu DataFrame con índice datetime y la columna 'festivo'
df_hora['dow'] = df_hora.apply(lambda row: 'festivo' if row['festivo'] else row['dow'], axis=1)


# In[13]:


# Agrupar por día de la semana y hora, calcular el promedio
#df_hora = df_hora.groupby(["dow", "hour"])["value"].mean().reset_index()

# Ordenar los días de la semana en el orden deseado (por ejemplo, lunes primero)
dias_ordenados = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo", "festivo"]
df_hora['dow'] = pd.Categorical(df_hora['dow'], categories=dias_ordenados, ordered=True)
df_hora = df_hora.sort_values(["dow", "hour"])



# In[14]:


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

mapeo2 = {
    "ea-consumo-total-hora": 'Energía Total Medido',
    "ea-control-sistema-hvac-hora": "Energía Sistema HVCA",
    "ea-oficinas-tablero-normal-hora": "Energía Tablero Normal",
    "ea-oficinas-tablero-regulado-hora": "Energía Tablero Regulado"

}


# In[15]:


df_month = df_month[df_month['variable'].isin(valores_a_buscar)]
ea_diaria = ea_diaria[ea_diaria['variable'].isin(valores_a_buscar)]


# In[16]:


ea_diaria['month_day'] = ea_diaria['month'].astype(str) + '-' + ea_diaria['day'].astype(str)
ea_diaria = ea_diaria.sort_values('datetime')

# Agregamos los valores de las dos variables por month_day
agg_df = ea_diaria.groupby(['month_day', 'variable'])['value'].sum().reset_index()


# ## Informe Consumos de Energía

# A continuación se presenta un informe del monitoreo energético llevado en Opain desde el 11 de noviembre al 31 de diciembre de 2023. En la siguiente tabla resumen, se visualizan los consumos por mes de cada una de las cargas que se presentan en el monitoreo.
# 

# In[17]:


df_month_2 =df_month.copy()

df_month_2["variable"] = df_month_2["variable"].replace(mapeo2)

# Pivotar la columna "month"
df_pivoted = df_month_2.pivot_table(index='variable', columns='month', values='value', aggfunc='sum')

# Ordenar el DataFrame por el mes 12 en orden descendente
df_pivoted = df_pivoted.sort_values(by=12, ascending=False)

# Redondear y formatear los valores sin decimales
df_pivoted = df_pivoted.round(0).applymap(lambda x: f'{x:,.0f}')

# Crear la tabla
fig = go.Figure(data=[go.Table(
    header=dict(values=['Proceso', 'Noviembre', 'Diciembre']),  # Cambiar '11' y '12' por los nombres reales de tus meses
    cells=dict(values=[df_pivoted.index,
                       df_pivoted[11],
                       df_pivoted[12]]))
])

# Ajustar el diseño y formato
fig.update_layout(
    title='Consumo de Energía por Mes',
    font=dict(size=11),  # Ajustar el tamaño del texto
    template='plotly_white',  # Cambiar el tema a plotly_white
    height=300  # Ajustar la altura de la tabla
)

# Mostrar la tabla
fig.show()


# Se identificó que el consumo de energía es menor los días sábado, domingo y festivo. Esto basados en el consumo total, donde la curva de demanda es influenciada significativamente por la carga de Consumo Tablero Normal. Además, se aprecia que la carga del Control Sistema HVAC mantiene un consumo constante y no varía significativamente según el tipo de día.

# In[18]:


ea_diaria['variable'] = ea_diaria['variable'].replace(mapeo)

list_vars = [
    "Consumo Energía Total Medido",
    "Consumo Energía Sistema HVCA",
    "Consumo Energía Tablero Normal",
    "Consumo Energía Tablero Regulado"
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


# El consumo de energía es menor los días sábado, domingo y festivo, correspondiente al consumo total, donde la curva de demanda es influenciada por la carga de consumo de energía en el tablero normal. Además, se aprecia que la carga del sistema HVAC mantiene un consumo constante y no varía según el tipo de día.

# In[19]:


ea_barra = ea_diaria[ea_diaria["variable"] == "Consumo Energía Total Medido"]
ea_diaria['variable'] = ea_diaria['variable'].replace(mapeo)

ea_hour['variable'] = ea_hour['variable'].replace(mapeo)
consumo_hour = ea_hour[ea_hour["variable"] == "Consumo Energía Total Medido"]


# In[20]:


# los valores unicos de esta columa consumo_hour["dow"]  
dow = consumo_hour["dow"].unique()   
print(dow)


# - Energía Tablero Normal: esta área tiene la mayor parte del consumo con un 73% del total
# - Energía Control Sistema HVCA: esta área tiene el segundo mayor consumo con un 18% del total
# - Energía Tablero Regulado: esta área el restante del consumo con un 8.7% del total.

# In[21]:


df_month["variable"] = df_month["variable"].replace(mapeo)

# Agrupar por area y sumar la energía
df_grouped = df_month.groupby('variable').sum().reset_index()
df_grouped = df_grouped[(df_grouped['variable'] != 'Consumo Energía Total Medido')]



# Crear el gráfico de torta
fig = px.pie(df_grouped, values='value', names='variable', 
             title='Distribución del Consumo de Energía por Área [kWh]',
             labels={'variable': 'Máquina', 'value': 'Consumo de Energía'},
             color_discrete_sequence=px.colors.qualitative.Set1)

# Habilitar la interactividad para agregar/quitar máquinas
fig.update_traces(hoverinfo='label+percent', textinfo='value+percent', pull=[0.1]*len(df_grouped))

# Mostrar el gráfico
fig.show()


# Al analizar las tres áreas medidas, se observa que la carga de Consumo Tablero Normal representa el mayor porcentaje en el consumo de energía. Es importante destacar que, de todo el consumo acumulado, el 73% se concentra en esta área. Esto sugiere que un manejo eficiente y control del consumo de las cargas asociadas a esta carga puede representar impacto positivo en la gestión de energía. 

# In[22]:


consumo_hour2 = consumo_hour.copy()
consumo_hour2 = consumo_hour2[consumo_hour2["month"] != 11]
matrix = consumo_hour2.pivot(index='day', columns='hour', values='value')

if (matrix.shape[0] > 0) & (matrix.shape[1] > 0):
    data = grp.pivoted_dataframe_to_plotly_heatmap(matrix)
    grp.hourly_heatmap(
        data,
        title=f"Consumo total de energía activa [kWh] en Diciembre"
    )


# In[23]:


import plotly.graph_objects as go

# Supongamos que df_ea es tu DataFrame original

# Lista de días de la semana en el orden deseado
dias_ordenados = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo', 'festivo']
colores_Celsia = ['#f37620', '#585a5b', '#fec431', '#1fa1db', '#00be91', '#ca1e48', '#19459a', '#ef966e', '#949495', '#fae364']
# Crear una lista de Box para cada día de la semana
traces = []
for dia in dias_ordenados:
    trace = go.Box(
        y=df_hora[df_hora['dow'] == dia]['value'],
        boxpoints='all',
        name=dia.capitalize(),
        marker_color=colores_Celsia[dias_ordenados.index(dia)]  # Asignar un color correspondiente
    )
    traces.append(trace)

# Crear el layout
layout = go.Layout(
    title='Consumo de Energía Activa Diario [kWh]',
    xaxis=dict(title='Día de la Semana'),
    yaxis=dict(title='Consumo de Energía [kWh]'),
)

# Crear la figura
fig = go.Figure(data=traces, layout=layout)

# Mostrar la figura
fig.show()


# En el grafico es posible evidenciar que en el día Martes y Miercoles, se presenta el rango más amplio de consumo energético en la semana. Por otro lado, los días Sábado y Domingo presentan un patrón de consumo más bajos, lo que podría sugerir una menor demanda de energía durante los fines de semana.
