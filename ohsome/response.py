#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class for ohsome API response"""

import geopandas as gpd
import pandas as pd
import json
from ohsome.utils import find_groupby_names


class OhsomeResponse:
    """
    COntains the response of the request to the ohsome API
    """

    def __init__(self, response, url=None, params=None):

        self.url = url
        self.parameters = params
        self.data = response.json()

    def as_dataframe(self, multiindex=True):
        """
        Converts the ohsome response to a pandas.DataFrame
        :return: pandas dataframe
        """
        assert (
            "features" not in self.data.keys()
        ), "GeoJSON object cannot be converted to a pandas.Dataframe. Use response.as_geodataframe() instead."

        groupby_names = []
        if "result" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["result"])
        elif "ratioResult" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["ratioResult"])
        elif "groupByResult" in self.data.keys():
            groupby_names = find_groupby_names(self.url)
            result_df = create_groupby_dataframe(
                self.data["groupByResult"],
                groupby_names,
            )
        elif "groupByBoundaryResult" in self.data.keys():
            groupby_names = find_groupby_names(self.url)
            result_df = create_groupby_dataframe(
                self.data["groupByBoundaryResult"],
                groupby_names,
            )
        else:
            raise TypeError("This result type is not implemented.")

        format_time(result_df)
        if multiindex:
            set_index(result_df, groupby_names)
        return result_df

    def as_geodataframe(self):
        """
        Converts the ohsome response to a geopandas.GeoDataFrame
        :return:
        """

        assert (
            "features" in self.data.keys()
        ), "Response is not in geojson format. Use .as_dataframe() instead."

        try:
            features = gpd.GeoDataFrame().from_features(self.data)
            features.crs = {"init": "epsg:4326"}
        except TypeError():
            raise TypeError(
                "This result type cannot be converted to a GeoPandas dataframe."
            )

        if "@validFrom" in features.columns:
            features["@validFrom"] = pd.to_datetime(
                features["@validFrom"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features["@validTo"] = pd.to_datetime(
                features["@validTo"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["@osmId", "@validFrom", "@validTo"])
        elif "@snapshotTimestamp" in features.columns:
            features["@snapshotTimestamp"] = pd.to_datetime(
                features["@snapshotTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["@osmId", "@snapshotTimestamp"])
        elif (
            "timestamp" in features.columns and "groupByBoundaryId" in features.columns
        ):
            features["timestamp"] = pd.to_datetime(
                features["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["groupByBoundaryId", "timestamp"])
        elif "@timestamp" in features.columns:
            features["@timestamp"] = pd.to_datetime(
                features["@timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["@timestamp"])

        return features

    def to_json(self, outfile):
        """
        Write response to file
        :return:
        """
        assert outfile.endswith("json"), "Output file must be json or geojson"
        with open(outfile, "w") as dst:
            json.dump(self.data, dst, indent=2)


def set_index(result_df, groupby_names):
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


def create_groupby_dataframe(data, groupby_names):
    """
    Formats groupby results
    :param result_df:
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


def format_time(result_df):
    """
    Format timestamp as datetime
    :param dresult_dff:
    :return:
    """
    if "timestamp" in result_df.columns:
        result_df["timestamp"] = pd.to_datetime(
            result_df["timestamp"], format="%Y-%m-%dT%H:%M:%S"
        )
    else:
        result_df["fromTimestamp"] = pd.to_datetime(
            result_df["fromTimestamp"], format="%Y-%m-%dT%H:%M:%S"
        )
        result_df["toTimestamp"] = pd.to_datetime(
            result_df["toTimestamp"], format="%Y-%m-%dT%H:%M:%S"
        )
