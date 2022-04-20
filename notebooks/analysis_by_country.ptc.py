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

st = CovidCountryStudy.from_csv('./../data/timeseries_by_country.csv')
st_gb = CovidCountryStudyGroupby.from_data(
    data=st.data,
    standard_parameter_groupbys=[(max, 'icu'), (mean, 'icu'), (max, 'deaths')],
    located_parameter_groupbys=[('vaccination_rate', max, 'icu'),
                                ('tests', max, 'confirmed'),
                                ('deaths', max, 'confirmed'),
                                ('confirmed', max, 'deaths'),
                                ('elderly_people_protection', max, 'deaths')])

# %%
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
for col in st_gb.data.columns:
    try:
        plt.figure()
        xy_values = np.array(
            [[x, y]
             for (x, y) in zip(st_gb.data.index.values, st_gb.data[col].values)
             if not pd.isnull(x) and not pd.isnull(y)],
            dtype='object')

        df_to_plot = pd.DataFrame(xy_values[:, 1],
                                  columns=[col],
                                  index=xy_values[:, 0]).T
        df_to_plot.plot(title=col, kind='bar')
        plt.show()

    except:
        pass

# %%
