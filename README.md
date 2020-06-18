# Ohsome for Python 

This repository contains a Python client for the Ohsome API. It is implemented as a fluent interface [(see this blog post)](https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/). Using a fluent interface, API calls are created dynamically without the need to predefine all endpoints. 

__Important Note:__ This project is still __under development__. So please, handle with care. :)

## Installation 

1. Set up the python environment and activate it. If you are using Anaconda, run:

``` 
conda create -n ohsome python=3
conda activate ohsome
conda install --file requirements
```

2.  If you want to use the juypter notebooks, additionally install:

```
conda install jupyter matplotlib descartes 
```

3. Install ohsome-py from GitHub:

```
pip install git+https://github.com/GIScience/ohsome-py
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
