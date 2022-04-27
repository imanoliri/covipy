"""
This module contains information about the covid itself and can be inherited using the CovidStudyMixin class.
"""

from dataclasses import dataclass


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
