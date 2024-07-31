# Changelog

## Unreleased

### Fixed

- Ordering of exception handling to correctly parse a broken response
- Assert that the expected columns are also present if the result is empty

## 0.3.2

### Fixed

- GeoSeries supplied as `bpolys` input raising exception ([#155](https://github.com/GIScience/ohsome-py/issues/155))

### Changed

- if tags are supplied for explosion in `response.as_dataframe`, the respective column will always be present in the resulting Geodataframe, even if the tags were not part of the result. In that case the column will be all-None ([#149](https://github.com/GIScience/ohsome-py/issues/149)).


## 0.3.1

### Fixed

 - prevent an exception if the `log_dir` for the `OhsomeClient` was set to `None`
 - removed time-dependency of unit tests that would cause them to fail at any time after the cassettes were recorded

### Changed

 - relaxed dependency requirement for `urllib3` to >=2.0.2 to prevent ohsome-py from becoming a 'diamond-dependency'
 - improved and sped up testing (first steps towards [#139](https://github.com/GIScience/ohsome-py/issues/139))
 - move metadata property from singleton to `cached_property`

## 0.3.0

### Added

 - support for python 3.12
 - custom [retry](https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.Retry) configuration
 - start and end timestamp meta information of the client are now datetime objects
 - accept shapely Polygon and MultiPolygon for `bpolys` input parameter
 - if a request fails a bash script containing the respective `curl` command is logged (if possible). This allows for easier debugging and sharing of failed requests.
 - timestamps are converted without timezone information. Deviates from Ohsome API [(Issue #318)](https://github.com/GIScience/ohsome-api/issues/318)

### Changed

 - breaking: geodataframes now contain a `@other_tags` colum containing all OSM tags. This behaviour can be adapted using the `explode_tags` parameter that allows to specify tags that should be in a separate column or to disable the feature completely. The latter will result in a potentially wide but sparse data frame.

### Removed

 - support for python < 3.10
 - support for geopandas < 0.14
 - support for pandas < 2.1
 - support for urllib3 < 2.1

## 0.2.0

### Added

 - support for python 3.11
 - support for geopandas up to v0.12.0

### Removed

 - support for python 3.7

### Fixed

 - wrong formatting of list parameters for ohsome requests if not given as string
