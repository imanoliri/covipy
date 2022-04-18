#%% [markdown]
# # Explore data
# This notebook explores the data imported in cell #1 in a standard way. It's useful to have a first contact with a dataset before continuing with more specific analysis and visualizations.
# It's assumed that the data is already fairly clean and there are no duplicate columns or rows.

#%%
# Imports
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

#%% [markdown]
# ## Country data
# Load country data from csv
#%%
df = pd.read_csv('./../data/timeseries_by_country.csv')

#%%
# Define index
indexes = ['id', 'date', 'administrative_area_level_1']
df = df.set_index(indexes)
#%% Prepare data to be memory-efficient
# Define parameters
covid_params = ['confirmed', 'deaths', 'recovered']
protection_params = [
    'tests', 'vaccines', 'people_vaccinated', 'people_fully_vaccinated'
]
health_sys_params = ['hosp', 'icu', 'vent']
policy_params = [
    'school_closing', 'workplace_closing', 'cancel_events',
    'gatherings_restrictions', 'transport_closing', 'stay_home_restrictions',
    'internal_movement_restrictions', 'international_movement_restrictions',
    'information_campaigns', 'testing_policy', 'contact_tracing',
    'facial_coverings', 'vaccination_policy', 'elderly_people_protection'
]
index_params = [
    'government_response_index', 'stringency_index',
    'containment_health_index', 'economic_support_index'
]
# country_params = ['latitude', 'longitude', 'population'] They are in `locations`, just ignore them
study_params = covid_params + protection_params + health_sys_params + policy_params + index_params

# Drop columns not to be studied
df = df[study_params]
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
# ### Parameter values
#%%
num_subplots = len(df.columns)
DEFAULT_PLOT_SIZE = 6
PLOT_KIND = 'hist'  #'kde'
#%%
_, axs = plt.subplots(num_subplots,
                      1,
                      figsize=(DEFAULT_PLOT_SIZE,
                               DEFAULT_PLOT_SIZE * (num_subplots - 0.5)))
for c, col in enumerate(df.columns):

    try:
        kwargs = {"kind": PLOT_KIND}
        if PLOT_KIND == 'hist':
            kwargs = {"kind": PLOT_KIND, "bins": 20}

        df[col].plot(title=f'Value distribution for: {col}',
                     ax=axs[c],
                     **kwargs)
    except:
        plt.plot(title=f'Value distribution for: {col}')
plt.plot()

#%% [markdown]
# ### Parameter relationships
#%%
sns.pairplot(df)
plt.show()
#%%
df_corr = df.dropna().corr()
df_corr
#%%
sns.heatmap(df_corr, annot=True)
#%%
