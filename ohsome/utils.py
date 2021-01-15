#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome utility functions """

from ohsome import OhsomeException
import geopandas as gpd
import pandas as pd


def check_parameters(params):
    """
    Checks whether the parameters of the query are valid
    :param params:
    :return:
    """
    pass


def check_time_parameter(params):
    """
    Checks time parameter and converts it if necessary
    :param params:
    :return:
    """

    if "time" not in params.keys():
        return params
    if isinstance(params["time"], pd.DatetimeIndex):
        params["time"] = params["time"].strftime("%Y-%m-%dT%H:%M:%S").tolist()
    return params


def check_boundary_parameter(params):
    """
    Checks whether a valid boundary parameter is given
    :param params:
    :return:
    """

    if "bboxes" in params.keys():
        return params
    elif "bpolys" in params.keys():
        if isinstance((params["bpolys"]), gpd.GeoDataFrame):
            params["bpolys"] = format_bpolys(params["bpolys"])
        return params
    elif "bcircles" in params.keys():
        if isinstance((params["bcircles"]), pd.DataFrame) or isinstance(
            (params["bcircles"]), gpd.GeoDataFrame
        ):
            params["bcircles"] = format_bcircles(params["bcircles"])
        return params
    else:
        OhsomeException(
            message="No valid boundary parameter is given. Specify one of the parameters 'bboxes', "
            "'bpolys' or 'bcircles'."
        )


def format_bcircles(bcircles):
    """
    Format geodataframe containing centroid and radius for bcircles parameter
    :param geodataframe:
    :return:
    """
    assert all(
        [x in bcircles.columns for x in ["id", "lon", "lat", "radius"]]
    ), "The columns 'id', 'lon', 'lat' and 'radius' must be given in the dataframe for 'bcircles'."
    formatted_bcircles = bcircles.apply(
        lambda r: "id {}:{},{},{}".format(
            int(r["id"]), r["lon"], r["lat"], r["radius"]
        ),
        axis=1,
    )
    return "|".join(formatted_bcircles.to_list())


def format_bpolys(bpolys):
    """
    Converts a geodataframe to a json object to be passed to an ohsome request
    :param bpolys:
    :return:
    """
    if "id" not in bpolys.columns:
        UserWarning(
            "Dataframe does not contain an 'id' column. Joining the ohsome query results and the geodataframe will not be possible."
        )

    # Create a json object which holds geometry, id and osmid for ohsome query
    return bpolys.to_json(na="drop")


def find_groupby_names(url):
    """
    Get the groupBy names
    :return:
    """
    return [name.strip("/") for name in url.split("groupBy")[1:]]
