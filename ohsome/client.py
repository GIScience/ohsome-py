#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""OhsomeClient classes to build and handle requests to ohsome API"""

import requests
from ohsome import OhsomeException, OhsomeResponse
from ohsome.helper import (
    extract_error_message_from_invalid_json,
    format_boundary,
    format_time,
)
import os

OHSOME_BASE_API_URL = "https://api.ohsome.org/v1/"
DEFAULT_LOG = True
DEFAULT_LOG_DIR = "./ohsome_log"


class _OhsomeInfoClient:
    """Client for metadata of ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initialize _OhsomeInfoClient object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        self._parameters = None
        self._metadata = None
        self._url = None
        self.log = log
        self.log_dir = log_dir
        if self.log:
            if not os.path.exists(self.log_dir):
                os.mkdir(self.log_dir)
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
            self._query_metadata()
        return self._metadata["extractRegion"]["temporalExtent"]["fromTimestamp"]
        # return dt.datetime.fromisoformat(start_timestamp.strip("Z"))

    @property
    def end_timestamp(self):
        """
        Returns the temporal extent of the current ohsome API
        :return:
        """
        if self._metadata is None:
            self._query_metadata()
        return self._metadata["extractRegion"]["temporalExtent"]["toTimestamp"]
        # return dt.datetime.fromisoformat(end_timestamp.strip("Z"))

    @property
    def api_version(self):
        """
        Returns the version of the ohsome API
        :return:
        """
        if self._metadata is None:
            self._query_metadata()
        return self._metadata["apiVersion"]

    @property
    def metadata(self):
        if self._metadata is None:
            self._query_metadata()
        return self._metadata

    @property
    def base_api_url(self):
        return self._base_api_url

    def _query_metadata(self):
        """
        Send ohsome GET request
        :param params: parameters of the request as in ohsome documentation
        :return:
        """
        self._url = self._base_api_url + "/metadata"
        try:
            response = requests.get(self._url)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise OhsomeException(
                message="Connection Error: Query could not be sent. Make sure there are no network "
                f"problems and that the ohsome API URL {self._url} is valid.",
                url=self._url,
                params=self._parameters,
            )
        except requests.exceptions.HTTPError as e:
            raise OhsomeException(
                message=e.response.json()["message"],
                url=self._url,
                params=self._parameters,
                error_code=e.response.status_code,
            )
        else:
            self._metadata = response.json()


class _OhsomePostClient:
    """Client for sending requests to ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initialize _OhsomePostClient object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        self._parameters = None
        self._metadata = None
        self._url = None
        self.log = log
        self.log_dir = log_dir
        if self.log:
            if not os.path.exists(self.log_dir):
                os.mkdir(self.log_dir)
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL

    def post(
        self,
        bboxes=None,
        bcircles=None,
        bpolys=None,
        time=None,
        filter=None,
        filter2=None,
        format=None,
        showMetadata=None,
        timeout=None,
        groupByKey=None,
        groupByKeys=None,
        groupByValues=None,
        properties=None,
        clipGeometry=None,
        endpoint=None,
    ):
        """
        Sends request to ohsome API

        :param bboxes: Bounding boxes given as
        - str e.g. "lon1,lat1,lon2,lat2|lon1,lat1,lon2,lat2|… or id1:lon1,lat1,lon2,lat2|id2:lon1,lat1,lon2,lat2|…
        - list e.g. [[id1:lon1,lat1,lon2,lat2],[id2:lon1,lat1,lon2,lat2],...]
        - pandas.DataFrame with columns minx, miny, maxx, maxy. These columns can be created from a GeoDataFrame using the
        'GeoDataFrame.bounds' method.

        :param bcircles: Coordinate pair and radius in meters to define a circular polygon given as
        - str e.g. lon,lat,radius|lon,lat,radius|… or id1:lon,lat,radius|id2:lon,lat,radius|…
        - list e.g. [[lon1,lat1,radius],[lon1,lat1,radius],...]
        - dict e.g. {"A": [lon1,lat1,radius], "B": [lon1,lat1,radius]}
        - pandas.DataFrame with columns 'lon', 'lat' and 'radius'
        - geopandas.GeoDataFrame with geometry column with Point geometries only and a column 'radius'.

        :param bpolys: Polygons given as geopandas.GeoDataFrame, GeoJSON FeatureCollection or str
        e.g. "8.65821,49.41129,8.65821,49.41825,8.70053,8.65821|8.67817,49.42147,8.67817,49.4342,8.67817"

        :param time: One or more ISO-8601 conform timestring(s) given as str, list, pandas.Series, pandas.DateTimeIndex,
        datetime.datetime, e.g. '2014-01-01T00:00:00,2015-07-01T00:00:00,2018-10-10T00:00:00,...'

        :param filter: (str) Combines several attributive filters: OSM type, geometry (simple feature) type, OSM tag

        :param format: (str)  ‘json’ or ‘csv’; default: ‘json’

        :param showMetadata (str, bool) add additional metadata information to the response: ‘true’, ‘false’, ‘yes’,
        ‘no’; default: ‘false’

        :param timeout (str, int) custom timeout to limit the processing time in seconds; default: dependent on server
        settings, retrievable via the /metadata request

        :param filter2: (str) Combines several attributive filters. Only for ratio queries.

        :param groupByKey: (str) OSM key, no default value (only one groupByKey can be defined),
        non matching objects (if any) will be summarised in a ‘remainder’ category. Only for groupByKey queries.

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

    def _handle_request(self):
        """
        Handles request to ohsome API
        :return:
        """
        error = None
        try:
            response = requests.post(url=self._url, data=self._parameters)
            response.raise_for_status()
            response.json()
        except requests.exceptions.HTTPError as e:
            error = OhsomeException(
                message=e.response.json()["message"],
                url=self._url,
                params=self._parameters,
                error_code=e.response.status_code,
            )
        except requests.exceptions.ConnectionError:
            error = OhsomeException(
                message="Connection Error: Query could not be sent. Make sure there are no network "
                f"problems and that the ohsome API URL {self._url} is valid.",
                url=self._url,
                params=self._parameters,
            )
        except requests.exceptions.RequestException as e:
            error = OhsomeException(
                message=str(e), url=self._url, params=self._parameters
            )
        except KeyboardInterrupt:
            error = OhsomeException(
                message="Keyboard Interrupt: Query was interrupted by the user.",
                url=self._url,
                params=self._parameters,
                error_code=440,
            )
        except ValueError:
            error_code, message = extract_error_message_from_invalid_json(response)
            error = OhsomeException(
                message=message,
                url=self._url,
                error_code=error_code,
                params=self._parameters,
            )
        finally:
            # If there has been an error and logging is enabled, write it to file
            if error:
                if self.log:
                    error.to_json(self.log_dir)
                raise error
            else:
                return OhsomeResponse(response, url=self._url, params=self._parameters)

    def _format_parameters(self, params):
        """
        Check and format parameters of the query
        :param params: Parameters for request
        :return:
        """
        self._parameters = params.copy()
        try:
            format_boundary(self._parameters)
        except OhsomeException as e:
            raise OhsomeException(
                message=str(e),
                error_code=300,
                params=self._parameters,
                url=self._url,
            )
        format_time(self._parameters)

    def _construct_resource_url(self, endpoint=None):
        """
        Constructs the full url of the ohsome request
        :param endpoint: Endpoint of ohsome API
        :return:
        """
        if endpoint:
            self._url = self._base_api_url + "/" + endpoint.strip("/")
        else:
            self._url = self._base_api_url + "/".join(self._cache)


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


class _OhsomeClientElements:
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initialize _OhsomeClientElements object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL
        self.log = log
        self.log_dir = log_dir

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


class _OhsomeClientElementsFullHistory:
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initialize _OhsomeClientElementsFullHistory object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL
        self.log = log
        self.log_dir = log_dir

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


class _OhsomeClientContributions:
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initiazlize _OhsomeClientContributions object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL
        self.log = log
        self.log_dir = log_dir

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


class _OhsomeClientUsers:
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    def __init__(
        self, base_api_url=None, log=DEFAULT_LOG, log_dir=DEFAULT_LOG_DIR, cache=None
    ):
        """
        Initialize _OhsomeClientUsers object
        :param base_api_url: URL of ohsome API instance
        :param log: Log failed queries, default:True
        :param log_dir: Directory for log files, default: ./ohsome_log
        :param cache: Cache for endpoint components
        """
        self._cache = cache or []
        if base_api_url is not None:
            self._base_api_url = base_api_url.strip("/") + "/"
        else:
            self._base_api_url = OHSOME_BASE_API_URL
        self.log = log
        self.log_dir = log_dir

    @property
    def count(self):
        return _OhsomeClientUsersAggregated(
            self._base_api_url, self.log, self.log_dir, self._cache + ["count"]
        )


class _OhsomeClientUsersAggregated(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def density(self):
        return _OhsomeClientUsersDensity(
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


class _OhsomeClientUsersDensity(_OhsomePostClient):
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


class _OhsomeClientContributionsLatest(_OhsomePostClient):
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


class _OhsomeClientElementsAggregated(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def density(self):
        return _OhsomeClientDensity(
            self._base_api_url, self.log, self.log_dir, self._cache + ["density"]
        )

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsGroupByBoundary(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )

    @property
    def ratio(self):
        return _OhsomeClientElementsRatio(
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


class _OhsomeClientDensity(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByBoundary(self):
        return _OhsomeClientElementsGroupByBoundary(
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


class _OhsomeClientElementsGroupByBoundary(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByTag(self):
        return _OhsomePostClient(
            self._base_api_url, self.log, self.log_dir, self._cache + ["groupBy", "tag"]
        )


class _OhsomeClientElementsRatio(_OhsomePostClient):
    """Subclass of _OhsomePostClient to define endpoints of ohsome API"""

    @property
    def groupByBoundary(self):
        return _OhsomePostClient(
            self._base_api_url,
            self.log,
            self.log_dir,
            self._cache + ["groupBy", "boundary"],
        )
