# ohsome-py: A Python client for the ohsome API

The *ohsome* package provides a Python client to query the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/), which can be used for analysing OpenStreetMap history data. It provides various endpoints for [data aggregation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation), [data extraction](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction) and [contributions](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Contributions).


## Installation 

The *ohsome* package can be installed using pip: 

```
pip install ohsome
```

If you want to run the [tutorial](./notebooks/Tutorial.ipynb) in this repository, you also need to install:

```
pip install jupyter matplotlib descartes 
```


## Usage 

The ohsome API provides various endpoints for [data aggregation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation), [data extraction](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction) and [contributions](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Contributions). The endpoints and parameters such as [boundaries](https://docs.ohsome.org/ohsome-api/stable/boundaries.html), [grouping](https://docs.ohsome.org/ohsome-api/stable/group-by.html), [time](https://docs.ohsome.org/ohsome-api/stable/time.html) and [filter](https://docs.ohsome.org/ohsome-api/stable/filter.html) are documented in the [ohsome API Documentation](https://docs.ohsome.org/ohsome-api/stable/index.html).


### Data Aggregation

**Example:** Query the number of OSM objects mapped as ways with the tag _landuse=farmland_ using the [/elements/count](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation#/Count/count_1) endpoint:


``` python
from ohsome import OhsomeClient
client = OhsomeClient()
response = client.elements.count.post(bboxes=[8.625,49.3711,8.7334,49.4397], 
									  time="2014-01-01", 
									  filter="landuse=farmland and type:way")
response_df = response.as_dataframe()

```

The single components of the endpoint URL are appended as method calls to the `OhsomeClient` object. The request is sent off by calling the ```post()``` method containing the query parameters. Responses from the data aggregation or contributions endpoints can be converted to a `pandas.DataFrame` using the `OhsomeResponse.as_dataframe()` method. 


### Data Extraction and Contributions


**Example:** Query all OSM objects mapped as ways with the tag _landuse=farmland_ including their geometry using the [/elements/geometry](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Extraction#/Data%20Extraction/elementsGeometry_1) endpoint:

``` python
client = OhsomeClient()
response = client.elements.geometry.post(bboxes=[8.625,49.3711,8.7334,49.4397], 
 												 time="2014-01-01", 
 												 filter="landuse=farmland and type:way")
response_gdf = response.as_geodataframe()
```
Responses from the data extraction endpoint can be converted to a `geopandas.GeoDataFrame`, since the data contains geometries:

### Metadata

The metadata of the ohsome API are returned using the `OhsomeClient().metadata` property. The `start_timestamp` and `end_timestamp` properties return the earliest and the latest possible dates for the [time](https://docs.ohsome.org/ohsome-api/stable/time.html) parameter of the query. 

``` python
OhsomeClient().metadata # --> returns metadata
OhsomeClient().start_timestamp # --> '2007-10-08T00:00:00Z'
OhsomeClient().end_timestamp # --> '2021-01-23T03:00Z'

```

### Parameters

All query parameters can be passed as strings as described in the documentation. 


##### Boundary 

In addition, the `bpolys` parameter can be passed as a `geopandas.GeoDataFrame` and the [boundary](https://docs.ohsome.org/ohsome-api/stable/boundaries.html) parameters `bboxes` and `bcircles` can be provided as a list containing the coordinates of one bounding box 

``` python 
bboxes = [8.7137,49.4096,8.717,49.4119]
```

a list containing several bounding boxes

```python 
bboxes = [[8.7137,49.4096,8.717,49.4119], [8.7137,49.4096,8.717,49.4119]]
```

or a dictionary: 

``` python
bboxes = {
	"A": [8.67066, 49.41423, 8.68177, 49.4204],
	"B": [8.67066, 49.41423, 8.68177, 49.4204],
}
```

##### Time

The [time](https://docs.ohsome.org/ohsome-api/stable/time.html) parameter can be passed as a `pandas.DateRange`:

```
time = pd.date_range("2018-01-01", periods=3, freq="D")
```

or as a list of dates. 

```
time = ['2018-01-01', '2018-01-02', '2018-01-03']
```

#### References: 

The design of this package was inspired by the blog post [Using Python to Implement a Fluent Interface to Any REST API]
(https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/) by Elmer Thomas.
