#%%
from statistics import mean
import sys

sys.path.append('./..')
sys.path.append('./../code')
#%% [markdown]
# # Analysis by country
#
#%%
from groupby import CovidCountryStudyGroupby
from study import CovidCountryStudy

st = CovidCountryStudy.from_csv('./../data/timeseries_by_country.csv')
st_gb = CovidCountryStudyGroupby.from_data(
    data=st.data,
    standard_parameter_groupbys=[(max, 'icu'), (mean, 'icu')],
    located_parameter_groupbys=[('vaccination_rate', max, 'icu'),
                                ('tests', max, 'confirmed'),
                                ('deaths', max, 'confirmed'),
                                ('confirmed', max, 'deaths'),
                                ('deaths', max, 'elderly_people_protection'),
                                ('elderly_people_protection', max, 'deaths')])

#%%
st_gb.data['nr_not_nans'] = [
    sum((val is not float('Nan') and val is not None for val in vals))
    for vals in st_gb.data.itertuples(index=False)
]
# %%
st_gb.data.nr_not_nans.max()
st_gb.data.nr_not_nans.min()

# %%
st.downsampling

# %%
len(st.data)

# %%
