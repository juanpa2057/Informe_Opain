#!/usr/bin/env python
# coding: utf-8

# In[1]:


# We import all the necesary packages
import time
import os
from dotenv import load_dotenv
load_dotenv()
_PROJECT_PATH: str = os.environ["_project_path"]
_PICKLED_DATA_FILENAME: str = os.environ["_pickled_data_filename"]

import sys
from pathlib import Path
project_path = Path(_PROJECT_PATH)
sys.path.append(str(project_path))


# In[2]:


#Import all your modules here
import json
import pandas as pd
import config_v2 as cfg
from library_ubidots_v2 import Ubidots as ubi


# In[3]:


#baseline=cfg.BASELINE
study=cfg.STUDY


# In[4]:


df_devices = ubi.get_available_devices_v2(label="opain", level="group", page_size=1000)
df_vars = ubi.get_available_variables(list(df_devices['device_id']))


# In[5]:


df_vars = df_vars[df_vars['variable_label'].isin(cfg.WHITELISTED_VAR_LABELS)]
VAR_IDS_TO_REQUEST = list(df_vars['variable_id'])
VAR_ID_TO_LABEL = dict(zip(df_vars['variable_id'], df_vars['variable_label']))


# In[6]:


CHUNK_SIZE = 100
DATE_INTERVAL_REQUEST = {'start': study[0], 'end': study[1]}
df = None
lst_responses = []
n_vars = len(VAR_IDS_TO_REQUEST)
print(f"Making request for the following interval: Study:{DATE_INTERVAL_REQUEST['start']}, Study:{DATE_INTERVAL_REQUEST['end']}")
for idx in range(0, ubi.ceildiv(len(VAR_IDS_TO_REQUEST), CHUNK_SIZE)):
    idx_start = idx * CHUNK_SIZE
    idx_end = (idx + 1) * CHUNK_SIZE
    chunk = VAR_IDS_TO_REQUEST[idx_start:idx_end]
    response = ubi.make_request(
        chunk, 
        DATE_INTERVAL_REQUEST, 
    )
    if response.status_code == 204 or response.status_code >= 500:
        print(f"Empty response for chunk {idx}")
        time.sleep(10)
        response = ubi.make_request(
        chunk, 
        DATE_INTERVAL_REQUEST,)
    current_idx = idx_end+1
    if (current_idx > n_vars):
        current_idx = n_vars
    print(f"Progress: {100*(current_idx)/n_vars:0.1f}%")
    print(f"Response status code: {response.status_code}")
    if response.status_code != 204:
        lst_responses.append(response)
    else: 
        print(f"Empty response for chunk {idx}")
df = ubi.parse_response(lst_responses, VAR_ID_TO_LABEL)


# In[7]:


pd.to_pickle(df, project_path / 'data'/ _PICKLED_DATA_FILENAME)
df.to_csv(project_path / 'data' / 'data.csv', index=False)

