"""
This module contains the features regarding the grouping and aggregation of data.
"""
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Tuple

import pandas as pd


@dataclass
class GroupbyMixin(ABC):
    """
    This Mixin adds the capability of calculating some standard grouped data from the given
    pandas.DataFrame via the `calc_groupby_data` method and saving it to the `data` attribute.

    For this, the `standard_parameter_groupbys` and/or the `located_parameter_groupbys`
    attributes must be defined.
    """

    # Filtering parameters
    at_string: str = '@'
    standard_parameter_groupbys: List[Tuple[Callable, str]] = None
    located_parameter_groupbys: List[Tuple[str, Callable, str]] = None

    @staticmethod
    @abstractmethod
    def groupby(data: pd.DataFrame):
        """ Method to group the data. """
        NotImplementedError("")

    def calc_groupby_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        This method groups the data using the `groupby` method and adds extra standard data
        before returning it.

        There are two methods for this:
            1 - `self.calc_func_dynamic_param()` which uses the
                `self.standard_parameter_groupbys` attribute.
            2 - `self.calc_param_located_at_func_param()` which uses the
                `self.located_parameter_groupbys` attribute.

        Args:
            data (pd.DataFrame): Data to calculate the grouped data from.
        """

        if __debug__:
            print(
                f'\n----> Function {inspect.getframeinfo(inspect.currentframe()).function}\
                    \n\t- Standard_parameter_groupbys: {self.standard_parameter_groupbys}\
                    \n\t- Located_parameter_groupbys: {self.located_parameter_groupbys}'
            )

        if data is None:
            print("Data is 'None'! None will be returned.")
            return None
        elif data.empty:
            print("Data is empty! None will be returned.")
            return None
        elif not self.standard_parameter_groupbys and not self.located_parameter_groupbys:
            print("No grouping parameters defined! None will be returned.")
            return None

        groupby = self.groupby(data)

        dfs_to_concat = []
        # Calculate and add to list all standard groupbys
        if self.standard_parameter_groupbys:
            for func, param in self.standard_parameter_groupbys:
                dfs_to_concat.append(
                    groupby.apply(self.calc_func_dynamic_param, param, func))

        # Calculate and add to list all located groupbys
        if self.located_parameter_groupbys:
            for param_to_return, func, param_to_locate in self.located_parameter_groupbys:
                dfs_to_concat.append(
                    groupby.apply(self.calc_param_located_at_func_param,
                                  param_to_return,
                                  func,
                                  param_to_locate,
                                  at_string=self.at_string))

        # Concat all, ID pair column and return
        return pd.concat(dfs_to_concat, axis=1)

    @staticmethod
    def calc_func_dynamic_param(df: pd.DataFrame, parameter: str,
                                func: Callable) -> pd.Series:
        """
        This method applies the given function to the given 'parameter' of the given 'df' and
        returns the result as a pandas.Series.

        Args:
            df (pd.DataFrame): Dataframe to apply the function to.
            parameter (str): Column to apply the function to.
            func (Callable): Function to apply.

        Returns:
            pd.Series: Result of applying the function to the defined column of the given data.
        """
        parameter_str = parameter
        if isinstance(parameter, tuple):
            parameter_str = '_'.join((par for par in parameter if par != ""))
        column_name = '_'.join([func.__name__, parameter_str])

        return pd.Series(data=[func(df[parameter])], index=[column_name])

    @staticmethod
    def calc_param_located_at_func_param(df: pd.DataFrame,
                                         param_to_return: str, func: Callable,
                                         param_to_locate: str,
                                         at_string: str) -> pd.Series:
        """
        This method returns the 'param_to_return' column values at the rows where the
        locator function 'func' applied to the 'param_to_locate' column is True.

        Args:
            df (pd.DataFrame): Data to locate the parameters to return from.
            param_to_return (str): Column of 'df' from which to return the values.
            func (Callable): Locator function to apply to 'param_to_locate' column in 'df'.
            param_to_locate (str): Column of 'df' for which to apply 'func'.
            at_string (str): String to use for the name of the result Series instead of the
                '@' character.

        Returns:
            pd.Series: [description]
        """

        if param_to_locate in df.columns:
            param_to_locate_values = df[param_to_locate]
        elif param_to_locate in df.index.names:
            param_to_locate_values = df.index.get_level_values(param_to_locate)
        else:
            print(
                f'Parameter to locate "{param_to_locate}" not found. Skip it.')

        # Default value if not found
        value = None
        min_row = param_to_locate_values == func(param_to_locate_values)
        if max(min_row) is True:
            if param_to_return in df.columns:
                value = df.loc[min_row, [param_to_return]].values[0][0]
            elif param_to_return in df.index.names:
                value = df.loc[min_row].index.get_level_values(
                    param_to_return)[0]

        param_to_locate_str = param_to_locate
        if isinstance(param_to_locate, tuple):
            param_to_locate_str = '_'.join(
                (par for par in param_to_locate if par != ""))
        param_to_return_str = param_to_return
        if isinstance(param_to_return, tuple):
            param_to_return_str = '_'.join(
                (par for par in param_to_return if par != ""))
        column_name = '_'.join([
            param_to_return_str, at_string, func.__name__, param_to_locate_str
        ])
        return pd.Series(data=[value], index=[column_name])

    @classmethod
    def from_df(cls, df: pd.DataFrame, **kwargs):
        """
        This methods creates a new instance of `ObjectPairDatasetGroupby` from the 'pair_dataset'
        given and extracting and adding extra data from it. Which parameters to be extracted can be
        input as keyword arguments and will be saved as attributes of the instance.
        """
        groupby = cls(**kwargs)
        if df is None:
            return groupby
        if df.empty:
            return groupby
        groupby.data = groupby.calc_groupby_data(df)
        return groupby


class CovidCountryStudyGroupby(GroupbyMixin):
    """
    Grouped data from an ObjectDataset object.
    """

    def groupby(self, data: pd.DataFrame) -> pd.core.groupby.DataFrameGroupBy:
        """
        Method to groupby the given data.
        """

        return data.groupby('administrative_area_level_1')
