#%%
import sys

sys.path.append('./..')
sys.path.append('./../code')
#%% [markdown]
# # Explore data
# This notebook explores the data imported in cell #1 in a standard way. It's useful to have a first contact with a dataset before continuing with more specific analysis and visualizations.
# It's assumed that the data is already fairly clean and there are no duplicate columns or rows.

#%%
# Setup
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

#%% [markdown]
# ## Country data
# Load country data from csv
#%%
from study import CovidCountryStudy

st = CovidCountryStudy.from_csv('./../data/timeseries_by_country.csv',
                                downsampling=7)
df = st.data

#%%
df = df[st.study_params]
#%% [markdown]
# ### General
#%%
df.shape
#%%
df.columns
#%%
df.info()
#%%
df.head(10)
#%%
df.describe()
#%% [markdown]
st.plot()

#%%
