#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"


from dataclasses import dataclass
from typing import List, Union, Dict, Optional


@dataclass
class OhsomeFilter:
    """Contains filter parameters"""

    tags: Optional[Dict[str, Union[List[str], str]]] = None
    geoms: Optional[List[str]] = None
    types: Optional[List[str]] = None

    def validate(self):
        """Validates geoms and tags parameters"""
        if isinstance(self.geoms, str):
            self.geoms = [self.geoms]
        elif self.geoms is None:
            self.geoms = []
        if isinstance(self.types, str):
            self.types = [self.types]
        elif self.types is None:
            self.types = []

    def __post_init__(self):
        """Post init"""
        self.validate()
