#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome utility functions """


def format_coordinates(feature_collection):
    """
    Format coordinates of feature to match ohsome requirements
    :param feature:
    :return:
    """
    features = feature_collection["features"]

    geometry_strings = []
    for feature in features:

        if feature["geometry"]["type"] == "Polygon":
            outer_ring = feature["geometry"]['coordinates'][0]
            geometry_strings.append(",".join([str(c[0]) + "," + str(c[1]) for c in outer_ring]))
        elif feature["geometry"]["type"] == "MultiPolygon":
            outer_rings = feature["geometry"]['coordinates'][0]
            for ring in outer_rings:
                geometry_strings.append(",".join([str(c[0]) + "," + str(c[1]) for c in ring]))
        else:
            print("Geometry type is not implemented")

    return "|".join(geometry_strings)


def find_groupby_names(url):
    """
    Get the groupBy names
    :return:
    """
    return [name.strip("/") for name in url.split("groupBy")[1:]]


def format_geodataframe(geodataframe):
    """
    Converts a geodataframe to a json object to be passed to an ohsome request
    :param geodataframe:
    :return:
    """
    if not "id" in geodataframe.columns:
        UserWarning("Dataframe does not contain an 'id' column. Joining the ohsome query results and the geodataframe will not be possible.")

    # Create a json object which holds geometry, id and osmid for ohsome query
    return geodataframe.to_json(na="drop")

