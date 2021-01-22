#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome client class """

import requests
from ohsome import OhsomeException, OhsomeResponse, utils
import json

OHSOME_BASE_API_URL = "https://api.ohsome.org/v1/"


class OhsomeClient:
    """
    Client for sending ohsome requests

    """

    def __init__(self, cache=None, base_api_url=None):
        self._cache = cache or []
        self.parameters = None
        self.metadata = None
        self.url = None
        if base_api_url is not None:
            self.base_api_url = base_api_url
        else:
            self.base_api_url = OHSOME_BASE_API_URL

    def add_api_component(self, name):
        """
        Builds the cache and handles special cases. Each part of the url is appended to the url components stored in
        the cache e.g. [elements, area]
        :param name: name of the method as string
        :return:
        """
        # Enables method chaining
        return OhsomeClient(self._cache + [name])

    def post(self, **params):
        """
        Sends POST request to ohsome API
        :param Parameters of the request to the ohsome API. See https://docs.ohsome.org/ohsome-api/v1/ for details

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
        self._construct_resource_url()
        self._format_parameters(params)
        try:
            response = requests.post(url=self.url, data=self.parameters)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self.url, params=self.parameters)
        return self._handle_response(response)

    def _format_parameters(self, params):
        """
        Check and format parameters of the query
        :param input_params:
        :return:
        """
        self.parameters = params.copy()
        try:
            utils.format_boundary(self.parameters)
        except OhsomeException as e:
            raise OhsomeException(
                message=e.message, status=300, params=self.parameters, url=self.url
            )
        utils.format_time(self.parameters)

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
                url=self.url,
                params=self.parameters,
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
                url=self.url,
                params=self.parameters,
                status=status_code,
            )
        else:
            return OhsomeResponse(response, url=self.url, params=self.parameters)

    def _construct_resource_url(self):
        """
        Constructs the full url of the ohsome request
        :return:
        """
        self.url = self.base_api_url + "/".join(self._cache)

    @property
    def start_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        if self.metadata is None:
            self.get_metadata()
        return self.metadata["extractRegion"]["temporalExtent"]["fromTimestamp"]

    @property
    def end_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        if self.metadata is None:
            self.get_metadata()
        return self.metadata["extractRegion"]["temporalExtent"]["toTimestamp"]

    @property
    def api_version(self):
        """
        Returns the version of the ohsome API
        :return:
        """
        if self.metadata is None:
            self.get_metadata()
        return self.metadata["apiVersion"]

    def get_metadata(self):
        """
        Send ohsome GET request
        :param params: parameters of the request as in ohsome documentation
        :return:
        """
        self.url = self.base_api_url + "/metadata"
        try:
            response = requests.get(self.url)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self.url, params=self.parameters)
        if not response.ok:
            raise OhsomeException(
                message="Forbidden",
                status=response.status_code,
                url=self.url,
                params=self.parameters,
            )
        self.metadata = self._handle_response(response).data

    @property
    def elements(self):
        return self.add_api_component("elements")

    @property
    def elementsFullHistory(self):
        return self.add_api_component("elementsFullHistory")

    @property
    def users(self):
        return self.add_api_component("users")

    @property
    def area(self):
        return self.add_api_component("area")

    @property
    def count(self):
        return self.add_api_component("count")

    @property
    def length(self):
        return self.add_api_component("length")

    @property
    def perimeter(self):
        return self.add_api_component("perimeter")

    @property
    def density(self):
        return self.add_api_component("density")

    @property
    def ratio(self):
        return self.add_api_component("ratio")

    @property
    def groupBy(self):
        return self.add_api_component("groupBy")

    @property
    def tag(self):
        return self.add_api_component("tag")

    @property
    def type(self):
        return self.add_api_component("type")

    @property
    def key(self):
        return self.add_api_component("key")

    @property
    def boundary(self):
        return self.add_api_component("boundary")

    @property
    def bbox(self):
        return self.add_api_component("bbox")

    @property
    def centroid(self):
        return self.add_api_component("centroid")

    @property
    def geometry(self):
        return self.add_api_component("geometry")

    def __getattr__(self, name):
        """
        This function is called whenever a method of OhsomeClient is called that does not exist.
        The name of the method is forwarded to add_api_component() and stored in the cache of api components.
        :param name:
        :return:
        """
        return self.add_api_component(name)

    def __repr__(self):
        return "<OhsomeClient: %s>" % self._construct_resource_url()

    def __del__(self):
        pass
