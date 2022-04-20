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
#%% [markdown]
# Load simple study and plot parameters vs time by country
#%%
from study import CovidCountryStudy
import matplotlib.pylab as plt

st = CovidCountryStudy.from_csv('./../data/timeseries_by_country.csv',
                                downsampling=7)

min_datapoints_in_country = 10

param_groups_vs_time = st.study_groups
for country in set(st.data.index.get_level_values(1)):
    for param_group in param_groups_vs_time:
        # Get df only for country, the group of parameters and remove index level for the country
        df_to_plot = st.data.loc[
            st.data.index.get_level_values(1) == country,
            param_group].reset_index('administrative_area_level_1').drop(
                columns=['administrative_area_level_1'])

        # Skip if empty, all values are null or not minimum data points
        if df_to_plot.empty:
            continue
        if df_to_plot.isnull().values.all():
            continue
        if len(df_to_plot) < min_datapoints_in_country:
            continue

        # Plot
        plt.figure()
        ax = df_to_plot.plot(title=country)
        plt.show()

#%% [markdown]
# Create CovidCountryStudyGroupby with interesting data aggregations & localizations
#%%
from groupby import CovidCountryStudyGroupby

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
