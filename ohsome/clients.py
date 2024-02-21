#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OhsomeClient classes to build and handle requests to ohsome API"""
import datetime as dt
import json
from functools import cached_property
from pathlib import Path
from typing import Union, Optional, List
from urllib.parse import urljoin

import geopandas as gpd
import pandas as pd
import requests
import shapely
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from urllib3 import Retry

from ohsome import OhsomeException, OhsomeResponse
from ohsome.constants import (
    DEFAULT_LOG_DIR,
    DEFAULT_LOG,
    OHSOME_BASE_API_URL,
    OHSOME_VERSION,
)
from ohsome.helper import (
    extract_error_message_from_invalid_json,
    format_boundary,
    format_time,
    convert_arrays,
    format_list_parameters,
)


class _OhsomeBaseClient:
    def __init__(
        self,
        base_api_url: Optional[str] = None,
        log: Optional[bool] = DEFAULT_LOG,
        log_dir: Optional[Union[str, Path]] = DEFAULT_LOG_DIR,
        cache: Optional[list] = None,
        user_agent: Optional[str] = None,
        retry: Optional[Retry] = None,
    ):
        """
        Initialize _OhsomeInfoClient object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        :param user_agent: User agent passed with the request to the ohsome API
        :param retry: Set a custom retry mechanism for requests. Be aware that ohsome-py will call the API once more
        after all retries have failed. This overcomes the problem that the cause of the retries is shadowed behind a
        RetryError by the underlying library.
        """
        self.log = log
        self.log_dir = Path(log_dir or DEFAULT_LOG_DIR)
        if self.log:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL
        self._cache = cache or []

        agent_list = [f"ohsome-py/{OHSOME_VERSION}"]
        if user_agent is not None:
            agent_list.append(user_agent)
        self.user_agent = " ".join(agent_list)

        if retry is None:
            self.__retry = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
                backoff_factor=1,
            )
        else:
            self.__retry = retry or Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
                backoff_factor=1,
            )
        self.__session = None

    def _session(self):
        """
        Set up request session
        :return:
        """
        if self.__session is None:
            adapter = HTTPAdapter(max_retries=self.__retry)
            self.__session = Session()
            self.__session.mount("https://", adapter)
            self.__session.mount("http://", adapter)
            self.__session.headers["user-agent"] = self.user_agent
        return self.__session

    def __repr__(self):
        return f"<OhsomeClient: {self._base_api_url}>"


class _OhsomeInfoClient(_OhsomeBaseClient):
    """Client for metadata of ohsome API"""

    def __init__(
        self,
        base_api_url: Optional[str] = None,
        log: Optional[bool] = DEFAULT_LOG,
        log_dir: Optional[Union[str, Path]] = DEFAULT_LOG_DIR,
        cache: Optional[list] = None,
        user_agent: Optional[str] = None,
        retry: Optional[Retry] = None,
    ):
        """
        Initialize _OhsomeInfoClient object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        :param user_agent: User agent passed with the request to the ohsome API
        :param retry: Set a custom retry mechanism for requests. Be aware that ohsome-py will call the API once more
        after all retries have failed. This overcomes the problem that the cause of the retries is shadowed behind a
        RetryError by the underlying library.
        """
        super(_OhsomeInfoClient, self).__init__(
            base_api_url, log, log_dir, cache, user_agent, retry
        )
        self._parameters = None
        self._metadata_url = f"{self.base_api_url}metadata"

    @property
    def base_api_url(self):
        return self._base_api_url

    @property
    def start_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        return dt.datetime.fromisoformat(
            self.metadata["extractRegion"]["temporalExtent"]["fromTimestamp"].strip("Z")
        )

    @property
    def end_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        return dt.datetime.fromisoformat(
            self.metadata["extractRegion"]["temporalExtent"]["toTimestamp"].strip("Z")
        )

    @property
    def api_version(self):
        """
        Returns the version of the ohsome API
        :return:
        """
        return self.metadata["apiVersion"]

    @cached_property
    def metadata(self):
        """
        Send ohsome GET request
        :return:
        """
        try:
            response = self._session().get(self._metadata_url)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise OhsomeException(
                message="Connection Error: Query could not be sent. Make sure there are no network "
                f"problems and that the ohsome API URL {self._metadata_url} is valid.",
                url=self._metadata_url,
                params=self._parameters,
            )
        except requests.exceptions.HTTPError as e:
            raise OhsomeException(
                message=e.response.json()["message"],
                url=self._metadata_url,
                params=self._parameters,
                error_code=e.response.status_code,
            )
        else:
            return response.json()


class _OhsomePostClient(_OhsomeBaseClient):
    """Client for sending requests to ohsome API"""

    def __init__(
        self,
        base_api_url: Optional[str] = None,
        log: Optional[bool] = DEFAULT_LOG,
        log_dir: Optional[Union[str, Path]] = DEFAULT_LOG_DIR,
        cache: Optional[list] = None,
        user_agent: Optional[str] = None,
        retry: Optional[Retry] = None,
    ):
        """
        Initialize _OhsomePostClient object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        :param user_agent: User agent passed with the request to the ohsome API
        :param retry: Set a custom retry mechanism for requests. Be aware that ohsome-py will call the API once more
        after all retries have failed. This overcomes the problem that the cause of the retries is shadowed behind a
        RetryError by the underlying library.
        """
        super(_OhsomePostClient, self).__init__(
            base_api_url, log, log_dir, cache, user_agent, retry
        )
        self._parameters = None
        self._url = None

    def post(
        self,
        bboxes: Optional[
            Union[
                str,
                dict,
                pd.DataFrame,
                List[str],
                List[float],
                List[List[str]],
                List[List[float]],
            ]
        ] = None,
        bcircles: Optional[
            Union[
                str,
                List[str],
                List[float],
                List[List[str]],
                List[List[float]],
                dict,
                gpd.GeoDataFrame,
                pd.DataFrame,
            ]
        ] = None,
        bpolys: Optional[
            Union[
                gpd.GeoDataFrame,
                gpd.GeoSeries,
                shapely.Polygon,
                shapely.MultiPolygon,
                str,
            ]
        ] = None,
        time: Optional[
            Union[str, dt.datetime, dt.date, list, pd.DatetimeIndex, pd.Series]
        ] = None,
        filter: Optional[str] = None,
        filter2: Optional[str] = None,
        format: Optional[str] = None,
        showMetadata: Optional[bool] = None,
        timeout: Optional[int] = None,
        groupByKey: Optional[str] = None,
        groupByKeys: Optional[Union[str, List[str]]] = None,
        groupByValues: Optional[Union[str, List[str]]] = None,
        properties: Optional[Union[str, List[str]]] = None,
        clipGeometry: Optional[bool] = None,
        endpoint: Optional[str] = None,
    ) -> OhsomeResponse:
        """
        Sends request to ohsome API

        :param bboxes: Bounding boxes given as
        - str e.g. lon1,lat1,lon2,lat2|lon1,lat1,lon2,lat2|… or id1:lon1,lat1,lon2,lat2|id2:lon1,lat1,lon2,lat2|…
        - list e.g. [[id1:lon1,lat1,lon2,lat2],[id2:lon1,lat1,lon2,lat2],...]
        - pandas.DataFrame with columns minx, miny, maxx, maxy. These columns can be created from a GeoDataFrame using
        the 'GeoDataFrame.bounds' method.

        :param bcircles: Coordinate pair and radius in meters to define a circular polygon given as
        - str e.g. lon,lat,radius|lon,lat,radius|… or id1:lon,lat,radius|id2:lon,lat,radius|…
        - list e.g. [[lon1,lat1,radius],[lon1,lat1,radius],...]
        - dict e.g. {"A": [lon1,lat1,radius], "B": [lon1,lat1,radius]}
        - pandas.DataFrame with columns 'lon', 'lat' and 'radius'
        - geopandas.GeoDataFrame with geometry column with Point geometries only and a column 'radius'.

        :param bpolys: Polygons given as geopandas.GeoDataFrame, geopandas.GeoSeries, shapely.Polygon, shapely.MultiPolygon, GeoJSON FeatureCollection or str
        e.g. "8.65821,49.41129,8.65821,49.41825,8.70053,8.65821|8.67817,49.42147,8.67817,49.4342,8.67817"

        :param time: One or more ISO-8601 conform timestring(s) given as str, list, pandas.Series, pandas.DateTimeIndex,
        datetime.datetime, e.g. '2014-01-01T00:00:00,2015-07-01T00:00:00,2018-10-10T00:00:00,...'

        :param filter: (str) Combines several attributive filters: OSM type, geometry (simple feature) type, OSM tag

        :param filter2: (str) Combines several attributive filters. Only for ratio queries.

        :param format: (str)  ‘json’ or ‘csv’; default: ‘json’

        :param showMetadata: (str, bool) add additional metadata information to the response: ‘true’, ‘false’, ‘yes’,
        ‘no’; default: ‘false’

        :param timeout: (str, int) custom timeout to limit the processing time in seconds; default: dependent on server
        settings, retrievable via the /metadata request

        :param groupByKey: (str) OSM key, no default value (only one groupByKey can be defined),
        non-matching objects (if any) will be summarised in a ‘remainder’ category. Only for groupByKey queries.

        :param groupByKeys: (str, list) OSM key(s) given as a list and combined with the ‘AND’ operator; default: empty;

        :param groupByValues: (str, list) OSM value(s) for the specified key given as a list and combined with the
        ‘AND’ operator, default: no value.  Only for groupByKey queries. Only for groupByTag queries.

        :param properties: (str) specifies what properties should be included for each feature representing an OSM
        element: ‘tags’ and/or ‘metadata’; multiple values can be delimited by commas; default: empty

        :parm clipGeometry: (bool, str) boolean operator to specify whether the returned geometries of the features
        should be clipped to the query’s spatial boundary (‘true’), or not (‘false’); default: ‘true’

        :param endpoint: (str) Url of the endpoint if post is called directly e.g. OhsomeClient().post("elements/count")

        :return: Response from ohsome API (OhsomeResponse)
        """
        params = locals().copy()
        del params["self"], params["endpoint"]
        self._construct_resource_url(endpoint)
        self._format_parameters(params)
        return self._handle_request()

    def _handle_request(self) -> OhsomeResponse:
        """
        Handles request to ohsome API
        :return:
        """
        ohsome_exception = None
        response = None

        try:
            response = self._session().post(url=self._url, data=self._parameters)
            response.raise_for_status()
            response.json()

        except requests.exceptions.HTTPError as e:
            try:
                error_message = e.response.json()["message"]
            except json.decoder.JSONDecodeError:
                error_message = f"Invalid URL: Is {self._url} valid?"

            ohsome_exception = OhsomeException(
                message=error_message,
                url=self._url,
                params=self._parameters,
                error_code=e.response.status_code,
                response=e.response,
            )

        except requests.exceptions.ConnectionError as e:
            ohsome_exception = OhsomeException(
                message="Connection Error: Query could not be sent. Make sure there are no network "
                f"problems and that the ohsome API URL {self._url} is valid.",
                url=self._url,
                params=self._parameters,
                response=e.response,
            )

        except requests.exceptions.RequestException as e:
            if isinstance(e, RetryError):
                # retry one last time without retries, this will raise the original error instead of a cryptic retry
                # error (or succeed)
                self._OhsomeBaseClient__session = None
                self._OhsomeBaseClient__retry = False
                self._handle_request()

            ohsome_exception = OhsomeException(
                message=str(e),
                url=self._url,
                params=self._parameters,
                response=e.response,
            )

        except KeyboardInterrupt:
            ohsome_exception = OhsomeException(
                message="Keyboard Interrupt: Query was interrupted by the user.",
                url=self._url,
                params=self._parameters,
                error_code=440,
            )

        except ValueError as e:
            if response:
                error_code, message = extract_error_message_from_invalid_json(
                    response.text
                )
            else:
                message = str(e)
                error_code = None
            ohsome_exception = OhsomeException(
                message=message,
                url=self._url,
                error_code=error_code,
                params=self._parameters,
                response=response,
            )

        except AttributeError:
            ohsome_exception = OhsomeException(
                message=f"Seems like {self._url} is not a valid endpoint.",
                url=self._url,
                error_code=404,
                params=self._parameters,
            )

        # If there has been an error and logging is enabled, write it to file
        if ohsome_exception:
            if self.log:
                ohsome_exception.log(self.log_dir)
            raise ohsome_exception

        return OhsomeResponse(response, url=self._url, params=self._parameters)

    def _format_parameters(self, params):
        """
        Check and format parameters of the query
        :param params: Parameters for request
        :return:
        """
        self._parameters = params.copy()

        self._parameters = convert_arrays(self._parameters)

        self._parameters = format_boundary(self._parameters)

        if self._parameters.get("time") is not None:
            self._parameters["time"] = format_time(self._parameters.get("time"))

        self._parameters = format_list_parameters(self._parameters)

    def _construct_resource_url(self, endpoint=None):
        """
        Constructs the full url of the ohsome request
        :param endpoint: Endpoint of ohsome API
        :return:
        """
        if endpoint:
            self._url = urljoin(self._base_api_url, endpoint.strip("/"))
        else:
            self._url = urljoin(self._base_api_url, "/".join(self._cache))

    def _(self, name):
        # Enables method chaining
        return _OhsomePostClient(
            base_api_url=None,
            log=DEFAULT_LOG,
            log_dir=DEFAULT_LOG_DIR,
            cache=self._cache + [name],
        )

    def __getattr__(self, name):
        valid_endpoints = [
            "elements",
            "users",
            "elementsFullHistory",
            "metadata",
            "area",
            "count",
            "length",
            "perimeter",
            "density",
            "ratio",
            "groupBy",
            "boundary",
            "tag",
            "type",
            "key",
            "bbox",
            "centroid",
            "geometry",
        ]
        if name not in valid_endpoints:
            raise AttributeError(f"'OhsomeClient' object has no attribute {name}.")
        else:
            return self._(name)


class OhsomeClient(_OhsomeInfoClient, _OhsomePostClient):
    """Class to handle requests to the ohsome API"""

    @property
    def elements(self):
        """Return elements objects."""
        return _OhsomeClientElements(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["elements"],
        )

    @property
    def elementsFullHistory(self):
        """Return full history elements."""
        return _OhsomeClientElementsFullHistory(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["elementsFullHistory"],
        )

    @property
    def contributions(self):
        """Return contrubioins object."""
        return _OhsomeClientContributions(
            self._base_api_url, self.log, self.log_dir, self._cache + ["contributions"]
        )

    @property
    def users(self):
        """Return users object."""
        return _OhsomeClientUsers(
            self._base_api_url, self.log, self.log_dir, self._cache + ["users"]
        )

    def __repr__(self):
        return f"<OhsomeClient: {self._base_api_url}>"


class _OhsomeClientElements(_OhsomeBaseClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def area(self):
        return _OhsomeClientElementsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["area"]
        )

    @property
    def count(self):
        return _OhsomeClientElementsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["count"]
        )

    @property
    def length(self):
        return _OhsomeClientElementsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["length"]
        )

    @property
    def perimeter(self):
        return _OhsomeClientElementsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["perimeter"]
        )

    @property
    def bbox(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["bbox"]
        )

    @property
    def centroid(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["centroid"]
        )

    @property
    def geometry(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["geometry"]
        )


class _OhsomeClientElementsAggregated(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def density(self):
        return _OhsomeClientElementsAggregatedDensity(
            self._base_api_url, self.log, self.log_dir, self._cache + ["density"]
        )

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsAggregatedDensityGroupByBoundary(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )

    @property
    def ratio(self):
        return _OhsomeClientElementsAggregatedRatio(
            self._base_api_url, self.log, self.log_dir, self._cache + ["ratio"]
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )

    @property
    def groupByType(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "type"],
        )

    @property
    def groupByKey(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "key"]
        )


class _OhsomeClientElementsAggregatedDensity(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsAggregatedDensityGroupByBoundary(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )

    @property
    def groupByType(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "type"],
        )


class _OhsomeClientElementsAggregatedDensityGroupByBoundary(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )


class _OhsomeClientElementsAggregatedRatio(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )


class _OhsomeClientElementsFullHistory(_OhsomeBaseClient):
    """Subclass of _OhsomeBaseClient to define endpoints of ohsome API for full history analyses."""

    @property
    def bbox(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["bbox"]
        )

    @property
    def centroid(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["centroid"]
        )

    @property
    def geometry(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["geometry"]
        )


class _OhsomeClientContributions(_OhsomeBaseClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def bbox(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["bbox"]
        )

    @property
    def centroid(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["centroid"]
        )

    @property
    def geometry(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["geometry"]
        )

    @property
    def latest(self):
        return _OhsomeClientContributionsLatest(
            self._base_api_url, self.log, self.log_dir, self._cache + ["latest"]
        )

    @property
    def count(self):
        return _OhsomeClientContributionsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["count"]
        )


class _OhsomeClientContributionsAggregated(_OhsomePostClient):
    @property
    def density(self):
        return _OhsomeClientContributionsAggregatedDensity(
            self._base_api_url, self.log, self.log_dir, self._cache + ["density"]
        )

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )


class _OhsomeClientContributionsAggregatedDensity(_OhsomePostClient):
    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )


class _OhsomeClientContributionsLatest(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API for contribution analyses."""

    @property
    def bbox(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["bbox"]
        )

    @property
    def centroid(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["centroid"]
        )

    @property
    def geometry(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["geometry"]
        )

    @property
    def count(self):
        return _OhsomeClientContributionsAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["count"]
        )


class _OhsomeClientUsers(_OhsomeBaseClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def count(self):
        return _OhsomeClientUsersAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["count"]
        )


class _OhsomeClientUsersAggregated(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def density(self):
        return _OhsomeClientUsersAggregatedDensity(
            self._base_api_url, self.log, self.log_dir, self._cache + ["density"]
        )

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )

    @property
    def groupByType(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "type"],
        )

    @property
    def groupByKey(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "key"]
        )


class _OhsomeClientUsersAggregatedDensity(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )

    @property
    def groupByType(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "type"],
        )
