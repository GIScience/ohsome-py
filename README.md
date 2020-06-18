# Ohsome for Python 

This repository contains a Python client for the Ohsome API. It is implemented as a fluent interface [(see this blog post)](https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/). Using a fluent interface, API calls are created dynamically without the need to predefine all endpoints. 

## Installation 

1. Set up the python environment and activate it.

``` 
conda create -n ohsome python=3 geopandas requests aiohttp geojson utm 
conda activate ohsome
```

2. Clone the repo, change into the ohsome-py folder and install the ohsome-py package by running:

```
pip install git+https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/libs/ohsome-py
```

## Usage 


To build an Ohsome query, you create an `OhsomeClient` object and append the parts of the endpoint URL as method calls to the client (similar to regular method chaining in Python). In the end, you call the `post()` method with all necessary parameters to send off your query.  

__Example:__ A POST request to the "/elements/area" endpoint may look like this:

```
from ohsome import OhsomeClient

bboxes = "8.67066,49.41423,8.68177,49.4204"
time = "2010-01-01/2011-01-01/P1Y"
keys = ["building"]
values = [""]

client = OhsomeClient()
response = client.elements.area.post(bboxes=bboxes, time=time, keys=keys, values=values)
del client
```

The response can be converted to a *Pandas* `DataFrame`... 

```
response_df = response.as_dataframe()
```

... or a *GeoPandas* `GeoDataFrame`, if the request contains geometries.

```
client = OhsomeClient()
response = client.elements.geometry.post(bboxes=bboxes, time=time, keys=keys, values=values)
response_gdf = response.as_geodataframe()
```
