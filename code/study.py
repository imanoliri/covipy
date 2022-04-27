"""
This module contains the Study class that allows to analyze a given dataset.
"""

from dataclasses import dataclass
from matplotlib.axes import Axes
from itertools import product
import pandas as pd
from typing import List, Tuple
import matplotlib.pylab as plt
import seaborn as sns
from groupby import CovidCountryStudyGroupby
import numpy as np
from covid import CovidStudyMixin


@dataclass
class Study():
    """
    The concrete analysis of the dataset found in the `data` attribute.
    """

    data: pd.DataFrame = None

    # data parameters
    downsampling: int = 1
    indexes: list = None
    study_params: list = None

    def __post_init__(self):

        if self.downsampling != 1:
            self.data = self.data.iloc[::self.downsampling]

    def plot(self) -> List[Axes]:
        """
        Generates the necessary plots from the data and returns the figures

        Returns:
            List[Axes]: _description_
        """
        pass

    @classmethod
    def from_df(cls, df: pd.DataFrame, **kwargs) -> 'Study':
        """
        Create instance from given DataFrame. Deletes columns that aren't either the
        indexes or the study_params.
        """
        return cls(data=df, **kwargs)

    @classmethod
    def from_csv(cls, path: str, **kwargs) -> 'Study':
        """
        Create instance from given path.
        """
        return cls.from_df(pd.read_csv(path), **kwargs)


@dataclass
class CovidCountryStudy(CovidStudyMixin, Study):
    """
    Study of the covid pandemic by country.
    """

    downsampling: int = 7

    # country_params: list = field(default_factory=lambda: ['latitude', 'longitude', 'population']) They are in `locations`, just ignore them

    # Plotting
    # --params
    plot_size: int = 6
    plot_kind: str = 'hist'  #'kde'
    plot_bins: int = 20

    # --relationships
    pair_plots: bool = True
    corr_plots: bool = False

    def __post_init__(self):

        super().__post_init__()

        # Plotting
        # --params
        self.plot_kwargs = {"kind": self.plot_kind}
        if self.plot_kind == 'hist':
            self.plot_kwargs = {"bins": 20, **self.plot_kwargs}

        # --relationships
        self.rel_groups_to_study = [self.covid_params]
        self.rel_groups_to_pair_with = [
            self.protection_params, self.health_sys_params, self.policy_params,
            self.index_params
        ]

    @property
    def group_pairs(self) -> Tuple[list]:

        return product(self.rel_groups_to_study, self.rel_groups_to_pair_with)

    def plot_parameters(self) -> List[Axes]:
        """
        Plots regarding the parameters themselves.
        """

        print("Plot parameter distributions.")

        plot_axes = []

        for group in self.study_groups:
            num_subplots = len(group)
            _, axs = plt.subplots(num_subplots,
                                  1,
                                  figsize=(self.plot_size, self.plot_size *
                                           (num_subplots - 0.5)))
            for c, col in enumerate(group):

                try:
                    self.data[col].plot(title=f'Value distribution for: {col}',
                                        ax=axs[c],
                                        **self.plot_kwargs)
                except:
                    plt.plot(title=f'EMPTY distribution for: {col}')

            plot_axes.append(axs)

        return plot_axes

    def plot_relationships(self) -> List[Axes]:
        """
        Plots regarding the relationships between parameters.
        """

        print("Plot parameter relationships.")

        rel_axes = []
        for params_to_study, params_to_pair_with in self.group_pairs:
            print(f'Relate:\n\t- {params_to_study}\n\t- {params_to_pair_with}')
            try:
                df_current = self.data[params_to_study + params_to_pair_with]
            except:
                continue

            if self.pair_plots:
                try:
                    rel_axes.append(sns.pairplot(df_current))
                    plt.show()
                except:
                    pass

            if self.corr_plots:
                try:
                    df_corr_current = df_current.dropna().corr()
                    rel_axes.append(sns.heatmap(df_corr_current, annot=True))
                except:
                    pass

        return rel_axes

    def plot(self) -> List[Axes]:
        """
        Plots the necessary
        """

        plot_axes = []

        plot_axes += self.plot_parameters()

        plot_axes += self.plot_relationships()

        return plot_axes


@dataclass
class CovidByCountryStudy(CovidStudyMixin, Study):
    """
    Grouped data from an ObjectDataset object.
    """

    groupby_data: CovidCountryStudyGroupby = None
    min_datapoints_in_country: int = 20

    def __post_init__(self):
        return super().__post_init__()

    def plot_parameters_by_country(self) -> List[Axes]:
        """
        Plot the parameters of each country.
        """

        print("Plot parameters for each country.")

        plot_axes = []
        param_groups_vs_time = self.study_groups
        for country in set(self.data.index.get_level_values(1)):
            for param_group in param_groups_vs_time:
                # Get df only for country, the group of parameters and remove index level for the country
                df_to_plot = self.data.loc[
                    self.data.index.get_level_values(1) == country,
                    param_group].reset_index(
                        'administrative_area_level_1').drop(
                            columns=['administrative_area_level_1'])

                # Skip if empty, all values are null or not minimum data points
                if df_to_plot.empty:
                    continue
                if df_to_plot.isnull().values.all():
                    continue
                if len(df_to_plot) < self.min_datapoints_in_country:
                    continue

                # Plot
                plt.figure()
                ax = df_to_plot.plot(title=country)
                plt.show()

                plot_axes.append(ax)

        return plot_axes

    def plot_groupby_parameters(self) -> List[Axes]:
        """
        Plots regarding the parameters themselves.
        """

        print("Plot parameters from groupby.")

        plot_axes = []
        for col in self.data.columns:
            plt.figure()
            xy_values = np.array(
                [[x, y]
                 for (x,
                      y) in zip(self.data.index.values, self.data[col].values)
                 if not pd.isnull(x) and not pd.isnull(y)],
                dtype='object')

            if xy_values.size != 0:
                df_to_plot = pd.DataFrame(xy_values[:, 1],
                                          columns=[col],
                                          index=xy_values[:, 0]).T
                ax = df_to_plot.plot(title=col, kind='bar')
                plot_axes.append(ax)

            plt.show()

        return plot_axes

    def plot(self) -> List[Axes]:
        """
        Plots.
        """

        plot_axes = []

        plot_axes += self.plot_parameters_by_country()

        plot_axes += self.plot_groupby_parameters()

        return plot_axes

    @classmethod
    def from_df(cls, df: pd.DataFrame, study_kwargs: dict,
                groupby_kwargs: dict) -> 'CovidByCountryStudy':
        """
        This methods creates a new instance of `ObjectPairDatasetGroupby` from the 'pair_dataset'
        given and extracting and adding extra data from it. Which parameters to be extracted can be
        input as keyword arguments and will be saved as attributes of the instance.
        """
        return cls(data=df,
                   groupby_data=CovidCountryStudyGroupby.from_df(
                       df, **groupby_kwargs),
                   **study_kwargs)

    @classmethod
    def from_csv(cls, path: str, **kwargs) -> 'CovidByCountryStudy':
        """
        Create instance from given path.
        """
        return cls.from_df(pd.read_csv(path), **kwargs)