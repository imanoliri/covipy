"""
This module contains the plotting methods and can be inherited using the PlotStudyMixin class.
"""

from dataclasses import dataclass
from typing import List, Tuple, Union

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

    @staticmethod
    def all_columns_for_partial(partial_column: Column, df: pd.DataFrame,
                                depth_of_columns: int) -> List[Column]:
        """
        Gets all columns in the dataframe related to the partial column.
        """
        column_with_slices = [slice(None)] * depth_of_columns
        levels_to_slice = [
            col_level
            for (_, col_level) in zip(column_with_slices, partial_column)
        ]
        depth_to_fill_with_nones = depth_of_columns - len(levels_to_slice)
        slicer = (*levels_to_slice, *[slice(None)] * depth_to_fill_with_nones)

        return df.loc[:, slicer].columns.tolist()

    def complete_column(self, partial_column: Column,
                        df: pd.DataFrame) -> Union[Column, List[Column]]:
        """
        If a partial column is passed, a list of all the subcolumns is returned.
        Else it's left as is.
        """
        depth_of_columns = 1
        if isinstance(df.columns, pd.MultiIndex):
            depth_of_columns = df.columns.nlevels

        if isinstance(partial_column,
                      tuple) and len(partial_column) == depth_of_columns:
            return partial_column

        return self.all_columns_for_partial(partial_column, self.data,
                                            depth_of_columns)

    def complete_columns(self, columns: List[Column],
                         df: pd.DataFrame) -> List[Column]:
        """
        Substitute any partial columns in the list by their related columns in the dataframe.
        """
        nested_columns = [[elem] if not isinstance(elem, list) else elem
                          for elem in (self.complete_column(col, df)
                                       for col in columns)]

        return [e for elem in nested_columns for e in elem]

    def prepare_columns(self, columns: List[Column],
                        df: pd.DataFrame) -> List[Column]:
        """
        Prepares all the columns in the list of lists of columns.

        Args:
            columns (List[Column]): List of of columns to prepare.
            df (pd.DataFrame): Dataframe used to complete missing levels in columns.

        Returns:
            List[List[Column]]: Prepared list of columns.
        """
        if not isinstance(columns, list):
            columns = [columns]
        return self.complete_columns(columns, df)

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

    def groupby_parameter_plots(self) -> List[Axes]:
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
