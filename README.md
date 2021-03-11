# ohsome-py: A Python client for the ohsome API

ohsome-py is a package for quering the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/) using Python. Take a look at the [tutorial](https://github.com/GIScience/ohsome-py/blob/master/notebooks/Tutorial.ipynb) to learn how it works. 

__Important Note:__ This project is still __under development__. So please, handle with care. :)

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

All requests to the ohsome API are sent using an `OhsomeClient` object.

```
from ohsome import OhsomeClient
client = OhsomeClient()
```

To send a request to one of the [ohsome API endpoints](https://docs.ohsome.org/ohsome-api/stable/endpoints.html) append the single components of the endpoint URL as method calls to the client (similar to regular method chaining in Python). In the end, call the ```post()``` method with all necessary parameters to send off the query as a POST request.

&rarr; For information on all available endpoints refer to the [ohsome swagger documentation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction)

&rarr; For more information on the parameters refer to the [ohsome API Sphinx documentation](https://docs.ohsome.org/ohsome-api/stable/index.html), e.g. [filters](https://docs.ohsome.org/ohsome-api/stable/filter.html), [boundaries](https://docs.ohsome.org/ohsome-api/stable/boundaries.html), [time](https://docs.ohsome.org/ohsome-api/stable/time.html) and [grouping](https://docs.ohsome.org/ohsome-api/stable/group-by.html).

__Example:__ Query the number of OSM features containing the tag _building=*_ using the [/elements/area](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation#/Count/count_1)

```
bboxes = "8.67066,49.41423,8.68177,49.4204"
time = "2010-01-01/2011-01-01/P1Y"
filter = "building=*"

client = OhsomeClient()
response = client.elements.area.post(bboxes=bboxes, time=time, keys=keys, values=values)

del client
```

The ohsome API response can be converted to a *Pandas* `DataFrame`... 

```
response_df = response.as_dataframe()
```

... or a *GeoPandas* `GeoDataFrame`, if the request contains geometries.

```
time = "2010-01-01"
client = OhsomeClient()
response = client.elements.geometry.post(bboxes=bboxes, time=time, filter=filter)
response_gdf = response.as_geodataframe()
```

#### References: 

This package is implemented as a [fluent interface](https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/) using which API calls are created dynamically without the need to predefine all endpoints.
