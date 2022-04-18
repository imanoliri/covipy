"""
This module contains the Study class that allows to analyze a given dataset.
"""

from dataclasses import dataclass, field
from matplotlib.axes import Axes
from itertools import product
import pandas as pd
from typing import List, Tuple
import matplotlib.pylab as plt
import seaborn as sns


@dataclass
class Study():
    """
    The concrete analysis of the dataset found in the `data` attribute.
    """

    data: pd.DataFrame
    indexes: list = None

    def plot(self) -> List[Axes]:
        """
        Generates the necessary plots from the data and returns the figures

        Returns:
            List[Axes]: _description_
        """
        pass

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> 'Study':
        """
        Create instance from given DataFrame.
        """
        if cls.indexes is not None:
            return cls(data=df.set_index(cls.indexes))
        else:
            return cls(data=df)

    @classmethod
    def from_csv(cls, path: str) -> 'Study':
        """
        Create instance from given path.
        """
        return cls.from_df(pd.read_csv(path))


@dataclass
class CovidCountryStudy(Study):

    # Indexes
    indexes: list = field(
        default_factory=lambda: ['id', 'date', 'administrative_area_level_1'])

    # Parameters
    covid_params: list = field(
        default_factory=lambda: ['confirmed', 'deaths', 'recovered'])
    protection_params: list = field(
        default_factory=lambda:
        ['tests', 'vaccines', 'people_vaccinated', 'people_fully_vaccinated'])
    health_sys_params: list = field(
        default_factory=lambda: ['hosp', 'icu', 'vent'])
    policy_params: list = field(default_factory=lambda: [
        'school_closing', 'workplace_closing', 'cancel_events',
        'gatherings_restrictions', 'transport_closing',
        'stay_home_restrictions', 'internal_movement_restrictions',
        'international_movement_restrictions', 'information_campaigns',
        'testing_policy', 'contact_tracing', 'facial_coverings',
        'vaccination_policy', 'elderly_people_protection'
    ])
    index_params: list = field(default_factory=lambda: [
        'government_response_index', 'stringency_index',
        'containment_health_index', 'economic_support_index'
    ])

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

        # Parameters
        self.study_groups = [
            self.covid_params, self.protection_params, self.health_sys_params,
            self.policy_params, self.index_params
        ]
        self.study_params = [
            elem for group in self.study_groups for elem in group
        ]

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
