"""
This module contains information about the covid itself and can be inherited using the CovidStudyMixin class.
"""

from dataclasses import dataclass
import pandas as pd
from itertools import product
from typing import List, Tuple
import numpy as np

Column = Tuple[str]


@dataclass
class CovidStudyMixin():
    """
    This class contains information about the covid itself.
    """

    country_data: pd.DataFrame = None
    country_filter: dict = None
    countries_to_study: List[str] = None

    def __post_init__(self):

        super().__post_init__()

        # Indexes
        self.indexes = ['date', 'administrative_area_level_1']

        # Country data
        self.set_countries_to_study()
        self.filter_countries()

        # Fix columns and indexes
        self.filter_columns()
        self.set_indexes()
        self.set_columns()

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

    # Parameters
    @property
    def covid_params(self) -> List[Column]:
        return list(
            product(*[['covid'], ['status'],
                      ['confirmed', 'deaths', 'recovered']]))

    @property
    def protection_params(self) -> List[Column]:
        return list(
            product(*[['covid'], ['protection'],
                      [
                          'tests', 'vaccines', 'people_vaccinated',
                          'people_fully_vaccinated'
                      ]]))

    @property
    def health_sys_params(self) -> List[Column]:
        return list(
            product(*[['health_system'], ['status'], ['hosp', 'icu', 'vent']]))

    @property
    def policy_params(self) -> List[Column]:
        return self.policy_social_distance_params + self.policy_movement_restrictions_params + self.policy_information_params + self.policy_tracing_params + self.policy_protection_params

    @property
    def policy_social_distance_params(self) -> List[Column]:
        return list(
            product(
                *[['policy'], ['social_distance'],
                  [
                      'school_closing', 'workplace_closing', 'cancel_events',
                      'gatherings_restrictions', 'stay_home_restrictions'
                  ]]))

    @property
    def policy_movement_restrictions_params(self) -> List[Column]:
        return list(
            product(*[['policy'], ['movement_restrictions'],
                      [
                          'internal_movement_restrictions',
                          'international_movement_restrictions',
                          'transport_closing'
                      ]]))

    @property
    def policy_information_params(self) -> List[Column]:
        return list(
            product(*[['policy'], ['information'], ['information_campaigns']]))

    @property
    def policy_tracing_params(self) -> List[Column]:
        return list(
            product(*[['policy'], ['tracing'],
                      ['testing_policy', 'contact_tracing']]))

    @property
    def policy_protection_params(self) -> List[Column]:
        return list(
            product(*[['policy'], ['protection'],
                      [
                          'facial_coverings', 'vaccination_policy',
                          'elderly_people_protection'
                      ]]))

    @property
    def index_params(self) -> List[Column]:
        return list(
            product(*[['index'], [''],
                      [
                          'government_response_index', 'stringency_index',
                          'containment_health_index', 'economic_support_index'
                      ]]))

    # Grouped parameters
    @property
    def study_groups(self) -> List[List[Column]]:
        return [
            self.covid_params, self.protection_params, self.health_sys_params,
            self.policy_params, self.index_params
        ]

    @property
    def study_params(self) -> pd.MultiIndex:
        return pd.MultiIndex.from_tuples(
            (tup for group in self.study_groups for tup in group))

    def filter_columns(self):
        """
        This method ensures that only the interesting columns and the indexes are kept
        in the data.
        """
        indexes = self.indexes
        study_params = self.study_params.to_list()
        if self.data.index.nlevels == 1:
            study_params = self.study_params.get_level_values(-1).to_list()

        elif self.data.index.nlevels == 3:
            indexes = pd.MultiIndex.from_tuples(
                ((index, '', '') for index in indexes))
        else:
            print(
                "Couldn't filter out columns because they aren't of depth 1 or 3."
            )
            return

        columns_to_keep = [
            col for col in indexes + study_params if col in self.data.columns
        ]
        if columns_to_keep:
            self.data = self.data[columns_to_keep]

    def set_indexes(self):
        """
        This method ensures that the indexes in the data are as defined.
        """

        indexes_to_set = [
            col for col in self.indexes
            if col in self.data.columns and col not in self.data.index.names
        ]
        if indexes_to_set:
            self.data = self.data.set_index(self.indexes)

    def set_columns(self):
        """
        This method ensures that the columns in the data are as defined.
        """

        lcols = len(self.data.columns)
        lparams = len(self.study_params)
        if lcols != lparams:
            print(
                f"Couldn't set_columns, because there are {lcols} columns in the data and there are {lparams} to be set!"
            )
            return

        if all((col in self.data.columns for col in self.study_params)):
            # print(f"Skipped set_columns, because the columns to be set are already the columns!")
            return

        self.data.columns = self.study_params

    def set_countries_to_study(self):
        """
        This method ensures that the countries to study are set correctly.
        If it's not defined but country_data and country_filter are, they are inferred.
        """
        if self.countries_to_study is None:
            """Nothig to set. Skip"""
            return

        if isinstance(self.countries_to_study, list):
            """Correctly defined. Skip"""
            return

        if self.country_data is None or self.country_filter is None:
            print("Couldn't set_countries_to_study, because it's not a dict!")
            return

        if not isinstance(self.country_filter, dict):
            print(
                "Couldn't set_countries_to_study, because country_filter is not a dict!"
            )
            return

        df = self.country_data
        mask = np.full((len(df)), False)
        for col, vals in self.country_filter.items():
            mask = np.logical_or(mask, [val in vals for val in df.loc[:, col]])

        self.countries_to_study = df.loc[mask].index.tolist()

    def filter_countries(self):
        """
        This method ensures that only the countries to study are in the data.
        """
        if self.countries_to_study is None:
            return

        country_header = self.indexes[1]
        c_values = None
        if country_header in self.data.columns:
            c_values = self.data.loc[:, country_header]
        elif self.data.index.names is not None:
            if country_header in self.data.index.names:
                c_values = self.data.index.get_level_values(country_header)

        if c_values is None:
            print(
                "Couldn't filter by countries because the country column/index couldn't be found!"
            )
            return
        mask_country = [c_id in self.countries_to_study for c_id in c_values]
        self.data = self.data.loc[mask_country]