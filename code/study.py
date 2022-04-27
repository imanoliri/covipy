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


@dataclass
class Study():
    """
    The concrete analysis of the dataset found in the `data` attribute.
    """

    data: pd.DataFrame

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
class CovidCountryStudy(Study):
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

        # Indexes
        self.indexes = ['date', 'administrative_area_level_1']

        # Parameters
        self.covid_params = ['confirmed', 'deaths', 'recovered']
        self.protection_params = [
            'tests', 'vaccines', 'people_vaccinated', 'people_fully_vaccinated'
        ]
        self.health_sys_params = ['hosp', 'icu', 'vent']
        self.policy_params = [
            'school_closing', 'workplace_closing', 'cancel_events',
            'gatherings_restrictions', 'transport_closing',
            'stay_home_restrictions', 'internal_movement_restrictions',
            'international_movement_restrictions', 'information_campaigns',
            'testing_policy', 'contact_tracing', 'facial_coverings',
            'vaccination_policy', 'elderly_people_protection'
        ]
        self.index_params = [
            'government_response_index', 'stringency_index',
            'containment_health_index', 'economic_support_index'
        ]

        # Parameters
        self.study_groups = [
            self.covid_params, self.protection_params, self.health_sys_params,
            self.policy_params, self.index_params
        ]
        self.study_params = [
            elem for group in self.study_groups for elem in group
        ]

        # Drop non relevant columns & set index
        if self.indexes is not None and self.study_params is not None:
            self.data = self.data[self.indexes + self.study_params]
        if self.indexes is not None:
            self.data = self.data.set_index(self.indexes)

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

        param_axes = []

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

            param_axes.append(axs)

        return param_axes

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


class CovidByCountryStudy(Study):
    """
    Grouped data from an ObjectDataset object.
    """
    data: CovidCountryStudyGroupby

    def plot_parameters(self) -> List[Axes]:
        """
        Plots regarding the parameters themselves.
        """

        print("Plot parameter values.")

        param_axes = []
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
                param_axes.append(ax)

            plt.show()

        return param_axes

    def plot(self) -> List[Axes]:
        """
        Plots the necessary
        """

        plot_axes = []

        plot_axes += self.plot_parameters()

        return plot_axes

    @classmethod
    def from_df(cls, df: pd.DataFrame, study_kwargs: dict,
                groupby_kwargs: dict) -> 'CovidByCountryStudy':
        """
        This methods creates a new instance of `ObjectPairDatasetGroupby` from the 'pair_dataset'
        given and extracting and adding extra data from it. Which parameters to be extracted can be
        input as keyword arguments and will be saved as attributes of the instance.
        """
        return Study.from_df(df=CovidCountryStudyGroupby.from_df(
            df, **groupby_kwargs),
                             **study_kwargs)
