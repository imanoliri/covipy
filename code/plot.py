"""
This module contains the plotting methods and can be inherited using the PlotStudyMixin class.
"""

from dataclasses import dataclass
from typing import List, Tuple

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

Column = Tuple[str]


@dataclass
class PlotStudyMixin():
    """
    This class provides plotting methods to its child class/es.
    """

    # --params
    plot_parameters: bool = False
    plot_size: int = 6
    plot_kind: str = 'hist'  #'kde'
    plot_bins: int = 20
    plot_kwargs: dict = None

    # --relationships
    plot_correlation_plots: bool = False
    correlation_parameters: List[Tuple[Column, List[Column]]] = None

    # --params by country
    plot_parameters_by_country: bool = False

    # --countrygroupby params
    plot_groupby_parameters: bool = False

    def __post_init__(self):

        super().__post_init__()

        # --params
        self.plot_kwargs = {"kind": self.plot_kind}
        if self.plot_kind == 'hist':
            self.plot_kwargs = {"bins": 20, **self.plot_kwargs}

    def parameter_plots(self) -> List[Axes]:
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
                    plt.plot()
                except:
                    plt.plot(title=f'EMPTY distribution for: {col}')

            plot_axes.append(axs)
            plt.show()

        return plot_axes

    def relationship_plots(self) -> List[Axes]:
        """
        Plots regarding the relationships between parameters.
        """

        print("Plot parameter relationships.")

        rel_axes = []
        for params, params_to_correlate_with in self.correlation_parameters:
            print(f'Correlate:\n\t- {params}\n\t- {params_to_correlate_with}')

            # Prepare column arguments
            params = self.prepare_columns(params, self.data)
            params_to_correlate_with = self.prepare_columns(
                params_to_correlate_with, self.data)

            df_current = self.data.loc[:, params + params_to_correlate_with]

            rel_axes.append(
                sns.pairplot(df_current,
                             x_vars=params,
                             y_vars=params_to_correlate_with))
            plt.show()

        return rel_axes

    def parameters_by_country_plots(self) -> List[Axes]:
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
                    param_group].reset_index('country').drop(
                        columns=['country'])

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

    def groupby_parameter_plots(self) -> List[Axes]:
        """
        Plots regarding the parameters themselves.
        """

        print("Plot parameters from groupby.")

        plot_axes = []
        data = self.groupby_data.data
        for col in data.columns:
            plt.figure()
            xy_values = np.array(
                [[x, y] for (x, y) in zip(data.index.values, data[col].values)
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
        Plots as defined in the flags.
        """

        plot_axes = []

        if self.plot_parameters:
            plot_axes += self.parameter_plots()

        if self.plot_correlation_plots:
            plot_axes += self.relationship_plots()

        if self.plot_parameters_by_country:
            plot_axes += self.parameters_by_country_plots()

        if self.plot_groupby_parameters:
            plot_axes += self.groupby_parameter_plots()

        return plot_axes
