# ohsome-py: A Python client for the ohsome API

[![status: experimental](https://github.com/GIScience/badges/raw/master/status/experimental.svg)](https://github.com/GIScience/badges#experimental)


`ohsome` helps you query the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/) to extract and analyse OpenStreetMap history data in Python. The ohsome API provides various endpoints for [data aggregation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation), [data extraction](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction) and [contributions](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Contributions). Take a look at the [documentation](https://docs.ohsome.org/ohsome-api/stable) to learn more or go through the [tutorial](./notebooks/Tutorial.ipynb) to get started.

## Installation 

### Using Anaconda

All required packages are contained in _requirements.txt_. Download or clone the repository and start a new environment inside the repository folder.

1. Set up the python environment and activate it:

``` 
conda create -n ohsome python=3
conda activate ohsome
conda install --file requirements
```

2.  If you want to run the Juypter notebook tutorial install:

```
conda install jupyter matplotlib descartes 
```

### Using PIP

PIP has the ability to install directly from github:

```
pip install git+https://github.com/GIScience/ohsome-py
```

Of course you can also install using pip in Anaconda.


## Usage

The ohsome API provides various endpoints for [data aggregation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation), [data extraction](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction) and [contributions](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Contributions). The endpoints and parameters such as [boundaries](https://docs.ohsome.org/ohsome-api/stable/boundaries.html), [grouping](https://docs.ohsome.org/ohsome-api/stable/group-by.html), [time](https://docs.ohsome.org/ohsome-api/stable/time.html) and [filter](https://docs.ohsome.org/ohsome-api/stable/filter.html) are described in the [ohsome API documentation](https://docs.ohsome.org/ohsome-api/stable/index.html).

### Data Aggregation

**Example:** Query the number of OSM objects mapped as ways with the tag _landuse=farmland_ using the [/elements/count](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation#/Count/count_1) endpoint:


``` python
from ohsome import OhsomeClient
client = OhsomeClient()
response = client.elements.count.post(bboxes=[8.625,49.3711,8.7334,49.4397], time="2014-01-01",  filter="landuse=farmland and type:way")
response_df = response.as_dataframe()

```

The single components of the endpoint URL are appended as method calls to the `OhsomeClient` object. The request is sent off by calling the ```post()``` method containing the query parameters. Responses from the data aggregation or contributions endpoints can be converted to a `pandas.DataFrame` using the `OhsomeResponse.as_dataframe()` method.

Alternatively, you can define the endpoint using the `endpoint` argument of the `OhsomeClient.post()`:

``` python
response = client.post(endpoint="elements/count", bboxes=[8.625,49.3711,8.7334,49.4397], time="2014-01-01",  filter="landuse=farmland and type:way")
```

### Data Extraction and Contributions


**Example:** Query all OSM objects mapped as ways with the tag _landuse=farmland_ including their geometry using the [/elements/geometry](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Extraction#/Data%20Extraction/elementsGeometry_1) endpoint:

``` python
client = OhsomeClient()
response = client.elements.geometry.post(bboxes=[8.625,49.3711,8.7334,49.4397], time="2014-01-01", filter="landuse=farmland and type:way")
response_gdf = response.as_geodataframe()
```
Responses from the data extraction endpoint can be converted to a `geopandas.GeoDataFrame`  using the `OhsomeResponse.as_geodataframe()` method, since the data contains geometries.

### Metadata

The metadata of the ohsome API are returned using the `OhsomeClient().metadata` property. The `start_timestamp` and `end_timestamp` properties return the earliest and the latest possible dates for the [time](https://docs.ohsome.org/ohsome-api/stable/time.html) parameter of the query.

``` python
OhsomeClient().metadata # --> returns metadata
OhsomeClient().start_timestamp # --> '2007-10-08T00:00:00Z'
OhsomeClient().end_timestamp # --> '2021-01-23T03:00Z'

```

### Parameters

All query parameters such as [boundary](https://docs.ohsome.org/ohsome-api/stable/boundaries.html), [grouping](https://docs.ohsome.org/ohsome-api/stable/group-by.html), [time](https://docs.ohsome.org/ohsome-api/stable/time.html) and [filter](https://docs.ohsome.org/ohsome-api/stable/filter.html) can be passed as strings as described in the [ohsome API documentation](https://docs.ohsome.org/ohsome-api/stable).


##### Boundary

The [boundary](https://docs.ohsome.org/ohsome-api/stable/boundaries.html) of the query can be defined using the `bpolys`, `bboxes` and `bcircles` parameters. The `bpolys` parameter can be passed as a `geopandas.GeoDataFrame`, while `bboxes` and `bcircles` can be provided as ...

a list containing the coordinates of the bounding box or circle

``` python
bboxes = [8.7137,49.4096,8.717,49.4119]
bcircles = [8.7137,49.4096, 100]
```

a list containing several bounding boxes or circles

```python
bboxes = [[8.7137,49.4096,8.717,49.4119], [8.7137,49.4096,8.717,49.4119]]
bcircles = [[8.7137,49.4096, 100], [8.7137,49.4096, 300]]
```

or a dictionary containing several bounding boxes or circles including user defined IDs.

``` python
bboxes = {"A": [8.67066, 49.41423, 8.68177, 49.4204], "B": [8.67066, 49.41423, 8.68177, 49.4204]}
bcircles = {"C1": [8.695, 49.41, 200], "C2": [8.696, 49.41, 200]}
```

##### Time

The [time](https://docs.ohsome.org/ohsome-api/stable/time.html) parameter can be passed as a ...

* ISO-8601 conform `string` e.g. `time = '2018-01-01/2018-03-01/P1M'`
* list of ISO-8601 conform dates e.g. `time = ['2018-01-01', '2018-02-01', '2018-03-01']`
* `datetime.datetime`: `dt.datetime(year=2018, month=3, day=1)`
* `pandas.DateRange` e.g. `time = pd.date_range("2018-01-01", periods=3, freq="M")`

#### References:

The design of this package was inspired by the blog post [Using Python to Implement a Fluent Interface to Any REST API]
(https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/) by Elmer Thomas.
