"""
This module contains the Study class that allows to analyze a given dataset.
"""

from dataclasses import dataclass
from itertools import product
from typing import Callable, List, Tuple

import pandas as pd
from matplotlib.axes import Axes

from covid import CovidStudyMixin
from groupby import CovidCountryStudyGroupby
from plot import PlotStudyMixin

Column = Tuple[str]


@dataclass
class Study():
    """
    The concrete analysis of the dataset found in the `data` attribute.
    """

    data: pd.DataFrame = None

    # data parameters
    downsampling: int = 1

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
    def from_csv(cls, path: str, **kwargs) -> 'Study':
        """
        Create instance from given path.
        """
        return cls(data=pd.read_csv(path), **kwargs)


@dataclass
class CovidCountryStudy(CovidStudyMixin, PlotStudyMixin, Study):
    """
    Study of the covid pandemic by country.
    """

    downsampling: int = 7

    # Plotting
    plot_parameters: bool = True
    plot_correlation_plots: bool = True

    def __post_init__(self):

        super().__post_init__()

        # Plotting
        #TODO: these attributes should be in the PlotMixin and be input by the user!
        infection_correlations = (('covid', 'status', 'confirmed'), [
            ('policy', 'protection', 'facial_coverings'),
            ('policy', 'movement_restrictions',
             'international_movement_restrictions'),
            ('policy', 'social_distance', 'stay_home_restrictions')
        ])
        protection_policy_correlations = ([('covid', 'status')],
                                          [('policy', 'protection')])
        self.correlation_parameters = [
            infection_correlations, protection_policy_correlations
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
    min_datapoints_in_country: int = 10
    standard_parameter_groupbys: List[Tuple[Callable, str]] = None
    located_parameter_groupbys: List[Tuple[str, Callable, str]] = None

    # Plotting
    plot_parameters_by_country: bool = True
    plot_groupby_parameters: bool = True

    def __post_init__(self):
        super().__post_init__()

        # Calculate groupby_data
        if self.data is not None:
            self.groupby_data = CovidCountryStudyGroupby.from_df(
                self.data,
                standard_parameter_groupbys=self.standard_parameter_groupbys,
                located_parameter_groupbys=self.located_parameter_groupbys)
