#%%
from statistics import mean
import sys

sys.path.append('./..')
sys.path.append('./../code')

#%%
# Setup
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
#%% [markdown]
# # Analysis by country
#
#%%
from groupby import CovidCountryStudyGroupby
from study import CovidCountryStudy

st = CovidCountryStudy.from_csv('./../data/timeseries_by_country.csv',
                                downsampling=7)
st_gb = CovidCountryStudyGroupby.from_data(
    data=st.data,
    standard_parameter_groupbys=[(max, 'icu'), (mean, 'icu'), (max, 'deaths')],
    located_parameter_groupbys=[('vaccination_rate', max, 'icu'),
                                ('tests', max, 'confirmed'),
                                ('deaths', max, 'confirmed'),
                                ('confirmed', max, 'deaths'),
                                ('elderly_people_protection', max, 'deaths')])
#%%
st_gb.plot()

# %%
