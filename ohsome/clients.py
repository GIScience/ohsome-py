#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome client class """

import requests
from ohsome import OhsomeException, OhsomeResponse
import utils


OHSOME_BASE_API_URL = "https://api.ohsome.org/v1/"


class OhsomeClient:
    """
    Client for sending ohsome requests

    Documentation of query parameters: https://api.ohsome.org/v1/
    """

    base_api_url = OHSOME_BASE_API_URL

    def __init__(self, cache=None):
        self._cache = cache or []
        self.parameters = None
        self.url = None
        self.metadata = None

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
        self.parameters = self._format_parameters(params)
        try:
            response = requests.post(self.url, data=self.parameters)
        except requests.RequestException as e:
            raise OhsomeException(message=e, url=self.url, params=self.parameters)
        return self.handle_response(response)

    @staticmethod
    def _format_parameters(params):
        """
        Check and if necessary format parameters
        :param input_params:
        :return:
        """
        formatted_params = params.copy()
        utils.check_boundary_parameter(formatted_params)
        utils.check_time_parameter(formatted_params)
        return formatted_params

    def handle_response(self, response):
        """
        Converts the ohsome response to an OhsomeResponse Object if query was successfull.
        Otherwise throws OhsomeException.
        :param response:
        :return:
        """
        if response.status_code == 200:
            return OhsomeResponse(response, url=self.url, params=self.parameters)
        else:
            raise OhsomeException(
                response=response,
                url=self.url,
                params=self.parameters,
            )

    def construct_resource_url(self):
        """
        Constructs the full url of the ohsome request
        :return:
        """
        return self.base_api_url + "/".join(self._cache)

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
        self.metadata = self.handle_response(response).data

    def __getattr__(self, name):
        """
        This function is called whenever a method of OhsomeClient is called that does not exist.
        The name of the method is forwarded to add_api_component() and stored in the cache of api components.
        :param name:
        :return:
        """
        return self.add_api_component(name)

    def __repr__(self):
        return "<OhsomeClient: %s>" % self.construct_resource_url()

    def __del__(self):
        pass
