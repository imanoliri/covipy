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
        "standard_parameter_groupbys": [(max, 'icu'), (mean, 'icu'),
                                        (max, 'deaths')],
        "located_parameter_groupbys":
        [('vaccination_rate', max, 'icu'), ('tests', max, 'confirmed'),
         ('deaths', max, 'confirmed'), ('confirmed', max, 'deaths'),
         ('elderly_people_protection', max, 'deaths')]
    })
#%%
st_gb.plot()

# %%
