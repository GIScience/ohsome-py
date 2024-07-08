#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class for ohsome API response"""

import json
from typing import Optional

import geopandas as gpd
import pandas as pd
from pandas import DataFrame

from ohsome.helper import find_groupby_names


class OhsomeResponse:
    """Contains the response of the request to the ohsome API"""

    def __init__(self, response=None, url=None, params=None):
        """Initialize the OhsomeResponse class."""
        self.response = response
        self.url = url
        self.parameters = params
        self.data = response.json()

    def as_dataframe(
        self, multi_index: Optional[bool] = True, explode_tags: Optional[tuple] = ()
    ):
        """
        Converts the ohsome response to a pandas.DataFrame or a geopandas.GeoDataFrame if the
        response contains geometries
        :param multi_index: If true returns the dataframe with a multi index
        :param explode_tags: By default, tags of extracted features are stored in a single dict-column. You can specify
        a tuple of tags that should be popped from this column. To disable it completely, pass None. Yet, be aware that
        you may get a large but sparse data frame.
        :return: pandas.DataFrame or geopandas.GeoDataFrame
        """
        if "features" not in self.data.keys():
            return self._as_dataframe(multi_index)
        else:
            return self._as_geodataframe(multi_index, explode_tags)

    def _as_dataframe(self, multi_index=True):
        """
        Converts the ohsome response to a pandas.DataFrame
        :param multi_index: If true returns the dataframe with a multi index
        :return: pandas.DataFrame
        """

        groupby_names = []
        if "result" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["result"])
        elif "ratioResult" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["ratioResult"])
        elif "groupByResult" in self.data.keys():
            groupby_names = find_groupby_names(self.url)
            result_df = self._create_groupby_dataframe(
                self.data["groupByResult"],
                groupby_names,
            )
        elif "groupByBoundaryResult" in self.data.keys():
            groupby_names = find_groupby_names(self.url)
            result_df = self._create_groupby_dataframe(
                self.data["groupByBoundaryResult"],
                groupby_names,
            )
        else:
            raise TypeError("This result type is not implemented.")

        time_columns = result_df.columns.intersection(
            ["timestamp", "fromTimestamp", "toTimestamp"]
        )
        result_df[time_columns] = result_df[time_columns].apply(self._format_timestamp)

        if multi_index:
            self._set_index(result_df, groupby_names)

        return result_df.sort_index()

    def _as_geodataframe(
        self, multi_index: Optional[bool] = True, explode_tags: Optional[tuple] = ()
    ):
        """
        Converts the ohsome response to a geopandas.GeoDataFrame
        :param multi_index: If true returns the dataframe with a multi index
        :return: geopandas.GeoDataFrame
        """

        if len(self.data["features"]) == 0:
            return gpd.GeoDataFrame(crs="epsg:4326", columns=["@osmId", "geometry"])

        try:
            if explode_tags is not None:
                for feature in self.data["features"]:
                    properties = feature["properties"]
                    tags = {}
                    new_properties = {k: None for k in explode_tags}
                    for k in properties.keys():
                        if (
                            (k.startswith("@"))
                            or (k == "timestamp")
                            or (k in explode_tags)
                        ):
                            new_properties[k] = properties.get(k)
                        else:
                            tags[k] = properties.get(k)
                    new_properties["@other_tags"] = tags
                    feature["properties"] = new_properties

            features = gpd.GeoDataFrame().from_features(self.data, crs="epsg:4326")

        except TypeError:
            raise TypeError(
                "This result type cannot be converted to a GeoPandas GeoDataFrame object."
            )

        time_columns = ["@validFrom", "@validTo", "@snapshotTimestamp", "@timestamp"]
        existing_time_columns = features.columns.intersection(time_columns)
        features[existing_time_columns] = features[existing_time_columns].apply(
            self._format_timestamp
        )

        if multi_index:
            index_columns = features.columns.intersection(
                ["@osmId"] + time_columns
            ).to_list()
            features = features.set_index(index_columns)

        return features.sort_index()

    def to_json(self, outfile):
        """
        Write response to json file
        :return:
        """
        assert outfile.endswith("json"), "Output file must be json"
        with open(outfile, "w", encoding="utf-8") as dst:
            json.dump(self.data, dst, indent=2, ensure_ascii=False)

    def _set_index(self, result_df, groupby_names):
        """
        Set multi-index based on groupby names and time
        :param result_df:
        :param groupby_names:
        :return:
        """
        if "timestamp" in result_df.columns:
            result_df.set_index([*groupby_names, "timestamp"], inplace=True)
        else:
            result_df.set_index(
                [*groupby_names, "fromTimestamp", "toTimestamp"], inplace=True
            )

    def _create_groupby_dataframe(self, data, groupby_names) -> DataFrame:
        """
        Formats groupby results
        :param data:
        :param groupby_names:
        :return:
        """
        keys = list(data[0].keys())
        keys.remove("groupByObject")
        record_dfs = []
        if len(groupby_names) == 1:
            for record in data:
                record_dict = {groupby_names[0]: record["groupByObject"]}
                record_result = [{**record_dict, **x} for x in record[keys[0]]]
                record_dfs.extend(record_result)
        elif len(groupby_names) == 2:
            for record in data:
                record_dict = {
                    groupby_names[0]: record["groupByObject"][0],
                    groupby_names[1]: record["groupByObject"][1],
                }
                record_result = [{**record_dict, **x} for x in record[keys[0]]]
                record_dfs.extend(record_result)
        return pd.DataFrame().from_records(record_dfs)

    @staticmethod
    def _format_timestamp(dt: pd.Series) -> pd.Series:
        """Format timestamp column as datetime."""
        return pd.to_datetime(dt.str.replace("Z", ""), format="ISO8601")
