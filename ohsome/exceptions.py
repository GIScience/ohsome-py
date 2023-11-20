#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class to handle error codes of ohsome API"""

import datetime as dt
import json
from pathlib import Path

from curlify2 import Curlify


class OhsomeException(Exception):
    """Exception to handle ohsome API errors"""

    def __init__(
        self, message=None, url=None, params=None, error_code=None, response=None
    ):
        """Initialize OhsomeException object"""
        super(Exception, self).__init__(message)
        self.message = message
        self.url = url
        if params:
            self.parameters = {k: v for k, v in params.items() if v is not None}
        self.error_code = error_code
        self.response = response
        self.timestamp = dt.datetime.now().isoformat()

    def log(self, log_dir: Path):
        """
        Logs OhsomeException
        :return:
        """
        log_file_name = f"ohsome_{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}"
        self.log_bpolys(log_dir, log_file_name)
        self.log_parameter(log_dir, log_file_name)
        if self.response is not None:
            self.log_curl(log_dir, log_file_name)
            self.log_response(log_dir, log_file_name)

    def log_curl(self, log_dir: Path, log_file_name: str) -> None:
        """Log the respective curl command for the request for easy debugging and sharing."""
        log_file = log_dir / f"{log_file_name}_curl.sh"
        curl = Curlify(self.response.request)
        curl_command = curl.to_curl()
        with log_file.open(mode="w") as dst:
            dst.write(curl_command)

    def log_response(self, log_dir: Path, log_file_name: str):
        """
        Log raw response. This may duplicate much data but is helpful for debugging to know the exact raw answer by the
        ohsome-api.
        """
        log_file = log_dir / f"{log_file_name}_raw.txt"
        with log_file.open(mode="w") as dst:
            dst.write(self.response.text)

    def log_parameter(self, log_dir: Path, log_file_name: str) -> None:
        """
        Log query parameters to file
        :param log_dir:
        :param log_file_name:
        :return:
        """
        log_file = log_dir / f"{log_file_name}.json"

        log = {
            "timestamp": self.timestamp,
            "status": self.error_code,
            "message": self.message,
            "requestUrl": self.url,
            "parameters": self.parameters,
        }
        with log_file.open(mode="w") as dst:
            json.dump(obj=log, fp=dst, indent=4)

    def log_bpolys(self, log_dir: Path, log_file_name: str) -> None:
        """
        Log bpolys parameter to geojson file if it is included in the query
        :params log_file: Path to geojson file which should contain bpolys parameter
        :return:
        """
        if "bpolys" in self.parameters:
            log_file_bpolys = log_dir / f"{log_file_name}_bpolys.geojson"
            bpolys = self.parameters.pop("bpolys")
            with log_file_bpolys.open(mode="w") as dst:
                json.dump(obj=json.loads(bpolys), fp=dst, indent=4)

    def __str__(self):
        return f"OhsomeException ({self.error_code}): {self.message}"
