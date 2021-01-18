#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome response class"""

import geopandas as gpd
import pandas as pd
import json
from ohsome.utils import find_groupby_names


class OhsomeResponse:
    """
    Parses the response of an Ohsome request
    """

    def __init__(self, response, url=None, params=None):

        self.url = url
        self.params = params
        self.data = response.json()

    def as_dataframe(self):
        """
        Converts the result to a Pandas DataFrame
        :return: pandas dataframe
        """
        assert (
            "features" not in self.data.keys()
        ), "GeoJSON object cannot be converted to a pandas.Dataframe. Use response.as_geodataframe() instead."

        if "result" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["result"])
            if "timestamp" in result_df.columns:
                result_df["timestamp"] = pd.to_datetime(
                    result_df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                result_df.set_index("timestamp", inplace=True)
            else:
                result_df["fromTimestamp"] = pd.to_datetime(
                    result_df["fromTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                result_df["toTimestamp"] = pd.to_datetime(
                    result_df["toTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                result_df.set_index(["fromTimestamp", "toTimestamp"])
            return result_df
        elif "groupByResult" in self.data.keys():
            groupby_names = find_groupby_names(self.url)
            record_dfs = []
            if len(groupby_names) == 1:
                for record in self.data["groupByResult"]:
                    record_dict = {groupby_names[0]: record["groupByObject"]}
                    record_result = [{**record_dict, **x} for x in record["result"]]
                    record_dfs.extend(record_result)
            elif len(groupby_names) == 2:
                for record in self.data["groupByResult"]:
                    record_dict = {
                        groupby_names[0]: record["groupByObject"][0],
                        groupby_names[1]: record["groupByObject"][1],
                    }
                    record_result = [{**record_dict, **x} for x in record["result"]]
                    record_dfs.extend(record_result)
            df_all = pd.DataFrame().from_records(record_dfs)

            if df_all.empty:
                return df_all

            # Convert timestamps to date format and create Multi-Index
            if "timestamp" in df_all.columns:
                if len(groupby_names) == 2:
                    df_all["timestamp"] = pd.to_datetime(
                        df_all["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                    )
                    df_all.set_index(
                        [groupby_names[0], groupby_names[1], "timestamp"], inplace=True
                    )
                else:
                    df_all["timestamp"] = pd.to_datetime(
                        df_all["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                    )
                    df_all.set_index([groupby_names[0], "timestamp"], inplace=True)
            else:
                df_all["fromTimestamp"] = pd.to_datetime(
                    df_all["fromTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                df_all["toTimestamp"] = pd.to_datetime(
                    df_all["toTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                if len(groupby_names) == 2:
                    df_all.set_index(
                        [
                            groupby_names[0],
                            groupby_names[1],
                            "fromTimestamp",
                            "toTimestamp",
                        ],
                        inplace=True,
                    )
                else:
                    df_all.set_index(
                        [groupby_names[0], "fromTimestamp", "toTimestamp"], inplace=True
                    )

            return df_all

        elif "shareResult" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["shareResult"])
            if "timestamp" in result_df.columns:
                result_df["timestamp"] = pd.to_datetime(
                    result_df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                result_df.set_index("timestamp", inplace=True)
            return result_df
        elif "ratioResult" in self.data.keys():
            result_df = pd.DataFrame().from_records(self.data["ratioResult"])
            if "timestamp" in result_df.columns:
                result_df["timestamp"] = pd.to_datetime(
                    result_df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
                )
                result_df.set_index("timestamp", inplace=True)
            return result_df
        else:
            raise TypeError(
                "This result type cannot be converted to a Pandas dataframe."
            )

    def as_geodataframe(self):
        """
        Returns the result as a GeoPandas dataframe
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

        if features.empty:
            return features

        if "@validFrom" in features.columns:
            features["@validFrom"] = pd.to_datetime(
                features["@validFrom"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features["@validTo"] = pd.to_datetime(
                features["@validTo"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["@osmId", "@validFrom", "@validTo"])
            return features

        if "@snapshotTimestamp" in features.columns:
            features["@snapshotTimestamp"] = pd.to_datetime(
                features["@snapshotTimestamp"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["@osmId", "@snapshotTimestamp"])
            return features

        if "timestamp" in features.columns and "groupByBoundaryId" in features.columns:
            features["timestamp"] = pd.to_datetime(
                features["timestamp"], format="%Y-%m-%dT%H:%M:%SZ"
            )
            features = features.set_index(["groupByBoundaryId", "timestamp"])

            return features

    def to_file(self, outfile):
        """
        Write response to file
        :return:
        """
        assert outfile.endswith("json"), "Output file must be json or geojson"
        with open(outfile, "w") as dst:
            json.dump(self.data, dst, indent=2)
