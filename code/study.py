"""
This module contains the Study class that allows to analyze a given dataset.
"""

from dataclasses import dataclass
from itertools import product
from typing import List, Tuple

import pandas as pd
from matplotlib.axes import Axes

from covid import CovidStudyMixin
from groupby import CovidCountryStudyGroupby
from plot import PlotStudyMixin


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
class CovidCountryStudy(CovidStudyMixin, PlotStudyMixin, Study):
    """
    Study of the covid pandemic by country.
    """

    downsampling: int = 7

    # Plotting
    plot_parameters: bool = True
    pair_plots: bool = True

    def __post_init__(self):

        super().__post_init__()

        # Plotting
        self.rel_groups_to_study = [self.covid_params]
        self.rel_groups_to_pair_with = [
            self.protection_params, self.health_sys_params, self.policy_params,
            self.index_params
        ]

    @property
    def group_pairs(self) -> Tuple[list]:

        return product(self.rel_groups_to_study, self.rel_groups_to_pair_with)


@dataclass
class CovidByCountryStudy(CovidStudyMixin, PlotStudyMixin, Study):
    """
    Grouped data from an ObjectDataset object.
    """

    groupby_data: CovidCountryStudyGroupby = None
    min_datapoints_in_country: int = 20

    # Plotting
    plot_parameters_by_country: bool = True
    plot_groupby_parameters: bool = True

    def __post_init__(self):
        return super().__post_init__()

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
