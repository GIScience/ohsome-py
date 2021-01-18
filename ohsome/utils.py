#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome utility functions """

from ohsome import OhsomeException
import geopandas as gpd
import pandas as pd
import datetime


def format_time(params):
    """
    Formats the 'time' parameter given as string, list of dates or pandas.Series or pandas.DateTimeIndex
    :param params:
    :return:
    """
    if "time" not in params.keys():
        return False
    if isinstance(params["time"], pd.DatetimeIndex):
        params["time"] = params["time"].strftime("%Y-%m-%dT%H:%M:%S").tolist()
    elif isinstance(params["time"], pd.Series):
        params["time"] = params["time"].tolist()
    elif isinstance((params["time"])[0], datetime.datetime):
        params["time"] = [x.strftime("%Y-%m-%dT%H:%M:%S") for x in params["time"]]


def format_boundary(params):
    """
    Formats the boundary parameters 'bboxes', 'bcircles' and 'bpolys'
    :param params:
    :return:
    """
    if "bboxes" in params.keys():
        params["bboxes"] = format_bboxes(params["bboxes"])
    elif "bpolys" in params.keys():
        params["bpolys"] = format_bpolys(params["bpolys"])
    elif "bcircles" in params.keys():
        params["bcircles"] = format_bcircles(params["bcircles"])
    else:
        raise OhsomeException(
            "No valid boundary parameter is given. Specify one of the parameters 'bboxes', 'bpolys' or 'bcircles'."
        )


def format_bcircles(bcircles):
    """
    Formats bcircles parameter to comply with ohsome API
    :param
    bcircles: Centroids and radius of the circles given as
        string (lon,lat,radius|lon,lat,radius|… or id1:lon,lat,radius|id2:lon,lat,radius|…)
        list ([[id1:lon1,lat1,radius],[id2:lon1,lat1,radius],...]
        pandas.DataFrame with columns 'lon', 'lat' and 'radius' or
        geopandas.GeoDataFrame with geometry column with Point geometries only and a column 'radius'.
    :return:
    """
    if isinstance(bcircles, str):
        return bcircles
    elif isinstance(bcircles, list) or isinstance(bcircles, tuple):
        bcircles_str = []
        if isinstance(bcircles[0], list):
            for b in bcircles:
                bcircles_str.append("{}:{},{},{}".format(*b))
            return "|".join(bcircles_str)
        else:
            return "{}:{},{},{}".format(*bcircles)
    elif isinstance(bcircles, gpd.GeoDataFrame):
        if bcircles.geometry.geom_type.unique() != ["Point"]:
            raise OhsomeException(
                "The geometry of the 'bcircles' GeoDataFrame may only include 'Point' geometry types."
            )
        formatted = bcircles.apply(
            lambda r: "{}:{},{},{}".format(
                int(r.name), r.geometry.y, r.geometry.x, r["radius"]
            ),
            axis=1,
        )
        return "|".join(formatted.to_list())
    elif isinstance(bcircles, pd.DataFrame):
        try:
            formatted = bcircles.apply(
                lambda r: "{}:{},{},{}".format(
                    int(r.name), r["lon"], r["lat"], r["radius"]
                ),
                axis=1,
            )
            return "|".join(formatted.to_list())
        except KeyError as e:
            raise OhsomeException(
                message="Column {} is missing in the dataframe provided as 'bboxes'.".format(
                    e
                )
            )
    else:
        raise OhsomeException(
            message="'bcircles' must be given as string, list, pandas.DataFrame or geopandas.GeoDataFrame."
        )


def format_bboxes(bboxes):
    """
    Formats bboxes parameter to comply with ohsome API
    :param
    bboxes: Bounding boxes given as
        string (lon1,lat1,lon2,lat2|lon1,lat1,lon2,lat2|… or id1:lon1,lat1,lon2,lat2|id2:lon1,lat1,lon2,lat2|…),
        list ([[id1:lon1,lat1,lon2,lat2],[id2:lon1,lat1,lon2,lat2],...] or
        pandas.DataFrame with columns minx, miny, maxx, maxy. These columns can be created from a GeoDataFrame using the
        'GeoDataFrame.bounds' method.
    :return: Bounding boxes formatted as a string compliant with ohsome API
    """
    if isinstance(bboxes, list) or isinstance(bboxes, tuple):
        bboxes_str = []
        if isinstance(bboxes[0], list):
            for b in bboxes:
                bboxes_str.append(",".join([str(c) for c in b]))
            return "|".join(bboxes_str)
        else:
            return ",".join([str(c) for c in bboxes])
    elif isinstance(bboxes, str):
        return bboxes
    elif isinstance(bboxes, gpd.GeoDataFrame):
        raise OhsomeException(
            message="Use the 'bpolys' parameter to specify the boundaries using a geopandas.GeoDataFrame."
        )
    elif isinstance(bboxes, pd.DataFrame):
        try:
            formatted = bboxes.apply(
                lambda r: "{}:{},{},{},{}".format(
                    r.name, r["minx"], r["miny"], r["maxx"], r["maxy"]
                ),
                axis=1,
            )
            return "|".join(formatted.to_list())
        except KeyError as e:
            raise OhsomeException(
                message="Column {} is missing in the dataframe provided as 'bboxes'.".format(
                    e
                )
            )
    else:
        raise OhsomeException(
            message="'bboxes' must be given as string, list or pandas.DataFrame."
        )


def format_bpolys(bpolys):
    """
    Formats bpolys parameter to comply with ohsome API
    :param
    bpolys: Polygons given as geopandas.GeoDataFrame or string formatted as GeoJSON FeatureCollection.
    :return:
    """
    if isinstance(bpolys, gpd.GeoDataFrame):
        return bpolys.to_json(na="drop")
    else:
        return bpolys


def list2string(list_param):
    """
    Convert bcircles or bboxes given as lists to a string
    :param list_param:
    :return:
    """
    bboxes_str = []
    if isinstance(list_param[0], list):
        for b in list_param:
            bboxes_str.append(",".join([str(c) for c in b]))
        return "|".join(bboxes_str)
    else:
        return ",".join([str(c) for c in list_param])


def find_groupby_names(url):
    """
    Get the groupBy names
    :return:
    """
    return [name.strip("/") for name in url.split("groupBy")[1:]]
