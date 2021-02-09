#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OhsomeClient classes to build and handle requests to ohsome API """

import requests
from ohsome import OhsomeException, OhsomeResponse, utils
import json
import datetime as dt

OHSOME_BASE_API_URL = "https://api.ohsome.org/v1/"


class _OhsomeMetadataClient:
    """
    Client for querying and handling metadata of ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        self._parameters = None
        self._metadata = None
        self._url = None
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    @property
    def start_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        if self._metadata is None:
            self._get_metadata()
        start_timestamp = self._metadata["extractRegion"]["temporalExtent"][
            "fromTimestamp"
        ]
        return dt.datetime.fromisoformat(start_timestamp.strip("Z"))

    @property
    def end_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        if self._metadata is None:
            self._get_metadata()
        end_timestamp = self._metadata["extractRegion"]["temporalExtent"]["toTimestamp"]
        return dt.datetime.fromisoformat(end_timestamp.strip("Z"))

    @property
    def api_version(self):
        """
        Returns the version of the ohsome API
        :return:
        """
        if self._metadata is None:
            self._get_metadata()
        return self._metadata["apiVersion"]

    @property
    def metadata(self):
        if self._metadata is None:
            self._get_metadata()
        return self._metadata

    @property
    def base_api_url(self):
        return self._base_api_url

    def _get_metadata(self):
        """
        Send ohsome GET request
        :param params: parameters of the request as in ohsome documentation
        :return:
        """
        self._url = self._base_api_url + "/metadata"
        try:
            response = requests.get(self._url)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self._url, params=self._parameters)
        if not response.ok:
            raise OhsomeException(
                message="Forbidden",
                status=response.status_code,
                url=self._url,
                params=self._parameters,
            )
        self._metadata = self._handle_response(response).data

    def _handle_response(self, response):
        """
        Converts the ohsome response to an OhsomeResponse object, if the response is valid.
        Otherwise throws OhsomeException.
        :param response:
        :return:
        """
        if response.status_code != 200:
            raise OhsomeException(
                message=json.loads(response.text)["message"],
                url=self._url,
                params=self._parameters,
                status=response.status_code,
            )
        # Check if response is valid json format to catch errors which occured during data transmission e.g. time out
        try:
            response.json()
        except json.JSONDecodeError:
            message = response.text[
                response.text.find("message")
                + 12 : response.text.find("requestUrl")
                - 6
            ]
            status_code = response.text[
                response.text.find("status") + 10 : response.text.find("message") - 5
            ]
            raise OhsomeException(
                message=message,
                url=self._url,
                params=self._parameters,
                status=status_code,
            )
        else:
            return OhsomeResponse(response, url=self._url, params=self._parameters)


class _OhsomePostClient:
    """
    Client for sending requests to ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        self._parameters = None
        self._metadata = None
        self._url = None
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    def post(self, endpoint=None, **params):
        """
        Sends POST request to ohsome API
        :param Parameters of the request to the ohsome API. See https://docs.ohsome.org/ohsome-api/v1/ for details

        endpoint: Url of the endpoint as a string if post is called directly e.g. OhsomeClient().post("elements/count")
        Boundary parameters: Specifies the spatial boundary of the query
        bboxes: Bounding boxes given as
        - string (lon1,lat1,lon2,lat2|lon1,lat1,lon2,lat2|… or id1:lon1,lat1,lon2,lat2|id2:lon1,lat1,lon2,lat2|…),
        - list ([[id1:lon1,lat1,lon2,lat2],[id2:lon1,lat1,lon2,lat2],...] or
        - pandas.DataFrame with columns minx, miny, maxx, maxy. These columns can be created from a GeoDataFrame using the
        'GeoDataFrame.bounds' method.
        bcircles: Centroids and radius of the circles given as
        - string (lon,lat,radius|lon,lat,radius|… or id1:lon,lat,radius|id2:lon,lat,radius|…)
        - list ([[id1:lon1,lat1,radius],[id2:lon1,lat1,radius],...]
        - pandas.DataFrame with columns 'lon', 'lat' and 'radius' or
        - geopandas.GeoDataFrame with geometry column with Point geometries only and a column 'radius'.
        bpolys: Polygons given as
        - geopandas.GeoDataFrame or
        - string formatted as GeoJSON FeatureCollection.

        Time: One or more ISO-8601 conform timestring(s) given as
        - string ('2014-01-01T00:00:00,2015-07-01T00:00:00,2018-10-10T00:00:00,...')
        - list of dates
        - pandas.Series or
        - pandas.DateTimeIndex

        :return:
        """
        self._construct_resource_url(endpoint)
        self._format_parameters(params)
        try:
            response = requests.post(url=self._url, data=self._parameters)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self._url, params=self._parameters)
        return self._handle_response(response)

    def _format_parameters(self, params):
        """
        Check and format parameters of the query
        :param input_params:
        :return:
        """
        self._parameters = params.copy()
        try:
            utils.format_boundary(self._parameters)
        except OhsomeException as e:
            raise OhsomeException(
                message=e.message, status=300, params=self._parameters, url=self._url
            )
        utils.format_time(self._parameters)

    def _handle_response(self, response):
        """
        Converts the ohsome response to an OhsomeResponse object, if the response is valid.
        Otherwise throws OhsomeException.
        :param response:
        :return:
        """
        if response.status_code != 200:
            raise OhsomeException(
                message=json.loads(response.text)["message"],
                url=self._url,
                params=self._parameters,
                status=response.status_code,
            )
        # Check if response is valid json format to catch errors which occured during data transmission e.g. time out
        try:
            response.json()
        except json.JSONDecodeError:
            message = response.text[
                response.text.find("message")
                + 12 : response.text.find("requestUrl")
                - 6
            ]
            status_code = response.text[
                response.text.find("status") + 10 : response.text.find("message") - 5
            ]
            raise OhsomeException(
                message=message,
                url=self._url,
                params=self._parameters,
                status=status_code,
            )
        else:
            return OhsomeResponse(response, url=self._url, params=self._parameters)

    def _construct_resource_url(self, endpoint=None):
        """
        Constructs the full url of the ohsome request
        :return:
        """
        if endpoint:
            self._url = self._base_api_url + "/" + endpoint.strip("/")
        else:
            self._url = self._base_api_url + "/".join(self._cache)


class OhsomeClient(_OhsomeMetadataClient, _OhsomePostClient):
    """
    Main class to build and handle requests to ohsome API
    """

    @property
    def elements(self):
        return _OhsomeClientElements(self._cache + ["elements"], self._base_api_url)

    @property
    def elementsFullHistory(self):
        return _OhsomeClientElementsFullHistory(
            self._cache + ["elementsFullHistory"], self._base_api_url
        )

    @property
    def contributions(self):
        return _OhsomeClientContributions(
            self._cache + ["contributions"], self._base_api_url
        )

    @property
    def users(self):
        return _OhsomeClientUsers(self._cache + ["users"], self._base_api_url)


class _OhsomeClientElements:
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    @property
    def area(self):
        return _OhsomeClientElementsAggregated(
            self._cache + ["area"], self._base_api_url
        )

    @property
    def count(self):
        return _OhsomeClientElementsAggregated(
            self._cache + ["count"], self._base_api_url
        )

    @property
    def length(self):
        return _OhsomeClientElementsAggregated(
            self._cache + ["length"], self._base_api_url
        )

    @property
    def perimeter(self):
        return _OhsomeClientElementsAggregated(
            self._cache + ["perimeter"], self._base_api_url
        )

    @property
    def bbox(self):
        return _OhsomePostClient(self._cache + ["bbox"], self._base_api_url)

    @property
    def centroid(self):
        return _OhsomePostClient(self._cache + ["centroid"], self._base_api_url)

    @property
    def geometry(self):
        return _OhsomePostClient(self._cache + ["geometry"], self._base_api_url)


class _OhsomeClientElementsFullHistory:
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    @property
    def bbox(self):
        return _OhsomePostClient(self._cache + ["bbox"], self._base_api_url)

    @property
    def centroid(self):
        return _OhsomePostClient(self._cache + ["centroid"], self._base_api_url)

    @property
    def geometry(self):
        return _OhsomePostClient(self._cache + ["geometry"], self._base_api_url)


class _OhsomeClientContributions:
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    @property
    def bbox(self):
        return _OhsomePostClient(self._cache + ["bbox"], self._base_api_url)

    @property
    def centroid(self):
        return _OhsomePostClient(self._cache + ["centroid"], self._base_api_url)

    @property
    def geometry(self):
        return _OhsomePostClient(self._cache + ["geometry"], self._base_api_url)

    @property
    def latest(self):
        return _OhsomeClientContributionsLatest(
            self._cache + ["latest"], self._base_api_url
        )


class _OhsomeClientUsers:
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    @property
    def count(self):
        return _OhsomeClientUsersAggregated(self._cache + ["count"], self._base_api_url)


class _OhsomeClientUsersAggregated(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def density(self):
        return _OhsomeClientUsersDensity(self._cache + ["density"], self._base_api_url)

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._cache + ["groupBy", "boundary"], self._base_api_url
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(self._cache + ["groupBy", "tag"], self._base_api_url)

    @property
    def groupByType(self):
        return _OhsomePostClient(self._cache + ["groupBy", "type"], self._base_api_url)

    @property
    def groupByKey(self):
        return _OhsomePostClient(self._cache + ["groupBy", "key"], self._base_api_url)


class _OhsomeClientUsersDensity(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._cache + ["groupBy", "boundary"], self._base_api_url
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(self._cache + ["groupBy", "tag"], self._base_api_url)

    @property
    def groupByType(self):
        return _OhsomePostClient(self._cache + ["groupBy", "type"], self._base_api_url)


class _OhsomeClientContributionsLatest(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def bbox(self):
        return _OhsomePostClient(self._cache + ["bbox"], self._base_api_url)

    @property
    def centroid(self):
        return _OhsomePostClient(self._cache + ["centroid"], self._base_api_url)

    @property
    def geometry(self):
        return _OhsomePostClient(self._cache + ["geometry"], self._base_api_url)


class _OhsomeClientElementsAggregated(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def density(self):
        return _OhsomeClientDensity(self._cache + ["density"], self._base_api_url)

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsGroupByBoundary(
            self._cache + ["groupBy", "boundary"], self._base_api_url
        )

    @property
    def ratio(self):
        return _OhsomeClientElementsRatio(self._cache + ["ratio"], self._base_api_url)

    @property
    def groupByTag(self):
        return _OhsomePostClient(self._cache + ["groupBy", "tag"], self._base_api_url)

    @property
    def groupByType(self):
        return _OhsomePostClient(self._cache + ["groupBy", "type"], self._base_api_url)

    @property
    def groupByKey(self):
        return _OhsomePostClient(self._cache + ["groupBy", "key"], self._base_api_url)


class _OhsomeClientDensity(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsGroupByBoundary(
            self._cache + ["groupBy", "boundary"], self._base_api_url
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(self._cache + ["groupBy", "tag"], self._base_api_url)

    @property
    def groupByType(self):
        return _OhsomePostClient(self._cache + ["groupBy", "type"], self._base_api_url)


class _OhsomeClientElementsGroupByBoundary(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def groupByTag(self):
        return _OhsomePostClient(self._cache + ["groupBy", "tag"], self._base_api_url)


class _OhsomeClientElementsRatio(_OhsomePostClient):
    """
    Subclass of _OhsomePostClient to define endpoints of ohsome API
    """

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._cache + ["groupBy", "boundary"], self._base_api_url
        )
