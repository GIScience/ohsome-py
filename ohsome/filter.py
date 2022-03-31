#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"


from dataclasses import dataclass
from typing import List, Union, Dict, Optional
import pydantic
from pydantic import BaseModel


class OhsomeFilter(BaseModel):
    """Contains filter parameters"""

    tags: Optional[Dict[str, Union[List[str], str]]]
    geoms: Optional[List[str]]
    types: Optional[List[str]]

    @pydantic.validator("geoms", "types", pre=True)
    @classmethod
    def validate_geoms_tags(cls, value) -> List[str]:
        """Validates geoms and tags parameters"""
        if isinstance(value, str):
            return [value]
        return value

    class Config:
        """Config"""

        extra = "forbid"
