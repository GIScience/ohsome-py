#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ohsome utility functions"""

import datetime
import json
import re
from typing import Tuple, Union, List

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from ohsome import OhsomeException


def convert_arrays(params: dict) -> dict:
    """Convert arrays to lists.

    params: the request parameters
    """
    for i in params.keys():
        if isinstance(params[i], np.ndarray):
            assert (
                params[i].ndim == 1
            ), f"Only one dimensional arrays are supported for parameter {i}"
            params[i] = list(params[i])

    return params


def format_time(time: any) -> str:
    """
    Formats the 'time' parameter
    :param time:
    :return:
    """
    if isinstance(time, str):
        return time
    if isinstance(time, datetime.datetime) or isinstance(time, datetime.date):
        return time.isoformat()
    elif isinstance(time, list):
        return ",".join([format_time(t) for t in time])
    if isinstance(time, pd.DatetimeIndex) or isinstance(time, pd.Series):
        return format_time(time.to_list())
    else:
        raise ValueError(
            f"The given time format {type(time)} is not supported. Feel free to open an issue in "
            "the ohsome-py repository for a feature request."
        )


def format_boundary(params: dict) -> dict:
    """
    Formats the boundary parameters 'bboxes', 'bcircles' and 'bpolys'
    :param params:
    :return:
    """
    if params["bboxes"] is not None:
        params["bboxes"] = format_bboxes(params["bboxes"])
    elif params["bpolys"] is not None:
        params["bpolys"] = format_bpolys(params["bpolys"])
    elif params["bcircles"] is not None:
        params["bcircles"] = format_bcircles(params["bcircles"])
    else:
        raise OhsomeException(
            message="No valid boundary parameter is given. Specify one of the parameters 'bboxes', 'bpolys' or "
            "'bcircles'.",
            error_code=440,
            params=params,
        )

    return params


def format_bcircles(
    bcircles: Union[
        str,
        List[str],
        List[float],
        List[List[str]],
        List[List[float]],
        dict,
        gpd.GeoDataFrame,
        pd.DataFrame,
    ]
) -> str:
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
        if isinstance(bcircles[0], list):
            return "|".join([",".join([str(x) for x in box]) for box in bcircles])
        elif isinstance(bcircles[1], float) or isinstance(bcircles[1], int):
            return ",".join([str(x) for x in bcircles])
        elif isinstance(bcircles[0], str) and (bcircles[0].find(",") != -1):
            return "|".join([str(c) for c in bcircles])
        else:
            raise OhsomeException("'bcircles' parameter has invalid format.")
    elif isinstance(bcircles, dict):
        return "|".join(
            [
                f"{bcircle_id}:" + ",".join([str(c) for c in coords])
                for bcircle_id, coords in bcircles.items()
            ]
        )
    elif isinstance(bcircles, gpd.GeoDataFrame):
        if (bcircles.geometry.geom_type.unique() != ["Point"]) or (
            "radius" not in bcircles.columns
        ):
            raise OhsomeException(
                message="The geometry of the 'bcircles' GeoDataFrame may only include 'Point' geometry types and "
                "requires a 'radius' column."
            )
        formatted = bcircles.apply(
            lambda r: f"{int(r.name)}:{r.geometry.x},{r.geometry.y},{r['radius']}",
            axis=1,
        )
        return "|".join(formatted.to_list())
    elif isinstance(bcircles, pd.DataFrame):
        try:
            formatted = bcircles.apply(
                lambda r: f"{int(r.name)}:{r['lon']},{r['lat']},{r['radius']}",
                axis=1,
            )
            return "|".join(formatted.to_list())
        except KeyError as e:
            raise OhsomeException(
                message=f"Column {e} is missing in the dataframe provided as 'bboxes'."
            )
    else:
        raise OhsomeException(message="'bcircles' parameter has invalid format.")


def format_bboxes(
    bboxes: Union[
        str,
        dict,
        pd.DataFrame,
        List[str],
        List[float],
        List[List[str]],
        List[List[float]],
    ]
) -> str:
    """
    Formats bboxes parameter to comply with ohsome API
    :param
    bboxes: Bounding boxes given as
        string: lon1,lat1,lon2,lat2|lon1,lat1,lon2,lat2|… or id1:lon1,lat1,lon2,lat2|id2:lon1,lat1,lon2,lat2|…
        list: [[id1,lon1,lat1,lon2,lat2],[id2,lon1,lat1,lon2,lat2],...] or [lon1,lat1,lon2,lat2] if it's just one box
        pandas.DataFrame: with columns minx, miny, maxx, maxy. These columns can be created from a GeoDataFrame using
        the 'GeoDataFrame.bounds' method.
    :return: Bounding boxes formatted as a string compliant with ohsome API
    """
    if isinstance(bboxes, list) or isinstance(bboxes, tuple):
        if isinstance(bboxes[0], list):
            return "|".join([",".join([str(x) for x in box]) for box in bboxes])
        elif isinstance(bboxes[1], float) or isinstance(bboxes[1], int):
            return ",".join([str(x) for x in bboxes])
        elif isinstance(bboxes[0], str) and (bboxes[0].find(",") != -1):
            return "|".join([str(c) for c in bboxes])
        else:
            raise OhsomeException(message="'bboxes' parameter has invalid format.")
    elif isinstance(bboxes, dict):
        return "|".join(
            [
                f"{bbox_id}:" + ",".join([str(c) for c in coords])
                for bbox_id, coords in bboxes.items()
            ]
        )
    elif isinstance(bboxes, str):
        return bboxes
    elif isinstance(bboxes, gpd.GeoDataFrame) or isinstance(bboxes, gpd.GeoSeries):
        raise OhsomeException(
            message="Use the 'bpolys' parameter to specify the boundaries using a geopandas object."
        )
    elif isinstance(bboxes, pd.DataFrame):
        try:
            formatted = bboxes.apply(
                lambda r: f"{r.name}:{r['minx']},{r['miny']},{r['maxx']},{r['maxy']}",
                axis=1,
            )
            return "|".join(formatted.to_list())
        except KeyError as e:
            raise OhsomeException(
                message=f"Column {e} is missing in the dataframe provided as 'bboxes'."
            )
    else:
        raise OhsomeException(
            message="'bboxes' must be given as string, list or pandas.DataFrame."
        )


def format_bpolys(
    bpolys: Union[
        gpd.GeoDataFrame, gpd.GeoSeries, shapely.Polygon, shapely.MultiPolygon, str
    ]
) -> str:
    """
    Formats bpolys parameter to comply with ohsome API
    :param
    bpolys: Polygons given as geopandas.GeoDataFrame, geopandas.GeoSeries, Shapely.Polygon or GeoJSON FeatureCollection as string.
    :return:
    """
    if isinstance(bpolys, gpd.GeoDataFrame):
        return bpolys.to_json(na="drop", show_bbox=False, drop_id=False, to_wgs84=True)
    elif isinstance(bpolys, gpd.GeoSeries):
        return format_bpolys(bpolys.to_frame("geometry"))
    elif isinstance(bpolys, shapely.Polygon) or isinstance(
        bpolys, shapely.MultiPolygon
    ):
        return format_bpolys(gpd.GeoDataFrame(geometry=[bpolys], crs="EPSG:4326"))
    elif isinstance(bpolys, str):
        try:
            return format_bpolys(
                gpd.GeoDataFrame.from_features(json.loads(bpolys), crs="EPSG:4326")
            )
        except Exception as e:
            raise OhsomeException(message="Invalid geojson.") from e
    else:
        raise OhsomeException(
            message="bpolys must be a geojson string, a shapely polygonal object or a geopandas object"
        )


def format_list_parameters(parameters: dict) -> dict:
    """Converts parameters of type list to strings using ',' as seperator."""
    list_parameters = ["groupByKeys", "groupByValues", "properties"]
    for param in list_parameters:
        if isinstance(parameters.get(param), list):
            parameters[param] = ",".join(parameters[param])

    return parameters


def find_groupby_names(url):
    """
    Get the groupBy names
    :return:
    """
    return [name.strip("/") for name in url.split("groupBy")[1:]]


def extract_error_message_from_invalid_json(responsetext: str) -> Tuple[int, str]:
    """
    Extract error code and error message from invalid json returned from ohsome API
    Otherwise throws OhsomeException.
    :param responsetext:
    :return:

    """
    message = "A broken response has been received"

    m = re.search('"message" : "(.*)"', responsetext)
    if m:
        message += ": " + m.group(1)

    m = re.search('"error" : "(.*)"', responsetext)
    if m:
        message += "; " + m.group(0)

    m = re.search('"timestamp" : "(.*)"', responsetext)
    if m:
        message += "; " + m.group(0)

    m = re.search('"path" : "(.*)"', responsetext)
    if m:
        message += "; " + m.group(0)

    m = re.search('"requestUrl" : "(.*)"', responsetext)
    if m:
        message += "; " + m.group(0)

    m = re.search(r'"status" : (\d+|".*")', responsetext)
    if m:
        status = m.group(1)
        message += "; " + m.group(0)
    else:
        status = None

    if status and status.isdigit() and not (int(status) == 200):
        error_code = int(status)
    elif "OutOfMemoryError" in message:
        error_code = 507
    else:
        error_code = 500

    return error_code, message
