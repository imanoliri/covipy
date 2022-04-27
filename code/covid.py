"""
This module contains information about the covid itself and can be inherited using the CovidStudyMixin class.
"""

from dataclasses import dataclass
import pandas as pd
from itertools import product


@dataclass
class CovidStudyMixin():
    """
    This class contains information about the covid itself.
    """

    def __post_init__(self):

        super().__post_init__()

        # Indexes
        self.indexes = ['date', 'administrative_area_level_1']

        # Parameters
        self.covid_params = list(
            product(*[['covid'], ['status'],
                      ['confirmed', 'deaths', 'recovered']]))
        self.protection_params = list(
            product(*[['covid'], ['protection'],
                      [
                          'tests', 'vaccines', 'people_vaccinated',
                          'people_fully_vaccinated'
                      ]]))
        self.health_sys_params = list(
            product(*[['health_system'], ['status'], ['hosp', 'icu', 'vent']]))

        self.policy_params = list(
            product(
                *[['policy'], ['social_distance'],
                  [
                      'school_closing', 'workplace_closing', 'cancel_events',
                      'gatherings_restrictions', 'stay_home_restrictions'
                  ]])
        ) + list(
            product(*[['policy'], ['movement_restrictions'],
                      [
                          'internal_movement_restrictions',
                          'international_movement_restrictions',
                          'transport_closing'
                      ]])
        ) + list(
            product(*[['policy'], ['information'], ['information_campaigns']])
        ) + list(
            product(*[['policy'], ['tracing'],
                      ['testing_policy', 'contact_tracing']])) + list(
                          product(
                              *[['policy'], ['protection'],
                                [
                                    'facial_coverings', 'vaccination_policy',
                                    'elderly_people_protection'
                                ]]))

        self.index_params = list(
            product(*[['index'], [''],
                      [
                          'government_response_index', 'stringency_index',
                          'containment_health_index', 'economic_support_index'
                      ]]))

        # Parameters
        self.study_groups = [
            self.covid_params, self.protection_params, self.health_sys_params,
            self.policy_params, self.index_params
        ]

        self.study_params = pd.MultiIndex.from_tuples(
            (tup for group in self.study_groups for tup in group))

        # Drop non relevant columns, set to multiindex & set index
        if self.indexes is not None and self.study_params is not None:
            self.data = self.data[
                self.indexes +
                self.study_params.get_level_values(-1).to_list()]
        if self.indexes is not None:
            self.data = self.data.set_index(self.indexes)

        if self.study_params is not None:
            self.data.columns = self.study_params

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
