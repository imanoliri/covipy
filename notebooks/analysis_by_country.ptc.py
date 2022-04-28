#%%
from statistics import mean
import sys
import pandas as pd

sys.path.append('./..')
sys.path.append('./../code')

#%%
# Setup
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
#%% [markdown]
# # Analysis by country
#
#%% [markdown]
# Load simple study and plot parameters vs time by country

#%% [markdown]
# Create CovidCountryStudyGroupby with interesting data aggregations & localizations
#%%
from study import CovidByCountryStudy

st_gb = CovidByCountryStudy.from_csv(
    path='./../data/timeseries_by_country.csv',
    study_kwargs={"downsampling": 7},
    groupby_kwargs={
        "standard_parameter_groupbys":
        [(max, ('health_system', 'status', 'icu')),
         (mean, ('health_system', 'status', 'icu')),
         (max, ('covid', 'status', 'deaths'))],
        "located_parameter_groupbys":
        [(('covid', 'protection', 'people_fully_vaccinated'), max,
          ('health_system', 'status', 'icu')),
         ('tests', max, ('covid', 'status', 'confirmed')),
         (('covid', 'status', 'deaths'), max, ('covid', 'status',
                                               'confirmed')),
         (('covid', 'status', 'confirmed'), max, ('covid', 'status',
                                                  'deaths')),
         (('policy', 'protection', 'elderly_people_protection'), max,
          ('covid', 'status', 'deaths'))]
    })
#%%
st_gb.plot()

# %%
