#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome client class """

import requests
import geopandas as gpd
from ohsome import OhsomeException, OhsomeResponse
from ohsome.utils import format_geodataframe

OHSOME_API_VERSION = '1'
OHSOME_BASE_API_URL = 'https://api.ohsome.org/v1/'


class OhsomeClient:
    """
    Client for sending ohsome requests

    Documentation of query parameters: https://api.ohsome.org/v1/
    """
    api_version = OHSOME_API_VERSION
    base_api_url = OHSOME_BASE_API_URL

    def __init__(self, cache=None, ):
        self._cache = cache or []
        self.formatted_parameters = None
        self.url = None

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
        Sends an ohsome post request
        :param params: parameters of the request as in ohsome documentation
        :return:
        """

        self.url = self.construct_resource_url()

        self.formatted_parameters = self.format_parameters(params)

        try:
            response = requests.post(self.url, data=self.formatted_parameters)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self.url, params=self.formatted_parameters)
        return self.handle_response(response)

    def get(self, **params):
        """
        Send ohsome get request
        :param params: parameters of the request as in ohsome documentation
        :return:
        """
        url = self.construct_resource_url()
        self.formatted_parameters = self.format_parameters(params)
        try:
            response = requests.get(url, data=self.formatted_parameters)
        except requests.RequestException as e:
            raise OhsomeException(message=e, params=self.formatted_parameters)
        return self.handle_response(response)

    @staticmethod
    def format_parameters(input_params):
        """
        Reformat parameters for post request and store them in dictionary
        :param input_params:
        :return:
        """
        params = {}
        for k, v in list(input_params.items()):
            if isinstance(v, bool):
                if v:
                    params[k] = 'true'
                else:
                    params[k] = 'false'
            elif isinstance(v, list):
                params[k] = ','.join([str(x) for x in v])
            elif isinstance(v, tuple):
                params[k] = ','.join([str(x) for x in v])
            #elif isinstance(v, geojson.feature.FeatureCollection):
            #    params[k] = format_coordinates(v)
            elif isinstance(v, gpd.geodataframe.GeoDataFrame):
                params[k] = format_geodataframe(v)
            else:
                params[k] = v
        return params

    def handle_response(self, response):
        """
        Converts the ohsome response to an OhsomeResponse Object if query was successfull.
        Otherwise throws OhsomeException.
        :param response:
        :return:
        """
        if response.status_code == 200:
            return OhsomeResponse(response, url=self.url, params=self.formatted_parameters)
        else:
            raise OhsomeException(response=response, url=self.url, params=self.formatted_parameters)

    def construct_resource_url(self):
        """
        Constructs the full url of the ohsome request
        :return:
        """
        return self.base_api_url + "/".join(self._cache)

    def __getattr__(self, name):
        """
        This function is called whenever a method of OhsomeClient is called that does not exist.
        The name of the method is forwarded to add_api_component() and stored in the cache of api components.
        :param name:
        :return:
        """
        return self.add_api_component(name)

    def __repr__(self):
        return '<OhsomeClient: %s>' % self.construct_resource_url()

    def __del__(self):
        pass