# ohsome-py: A Python client for the ohsome API

[![status: active](https://github.com/GIScience/badges/raw/master/status/active.svg)](https://github.com/GIScience/badges#active)

The *ohsome-py* package helps you extract and analyse OpenStreetMap history data using the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/) and Python. It handles queries to the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/) and converts its responses to [Pandas](https://pandas.pydata.org/) and [GeoPandas](https://geopandas.org/) data frames to facilitate easy data handling and analysis.

The ohsome API provides various endpoints for [data aggregation](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation), [data extraction](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=dataExtraction) and [contributions](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Contributions) to analyse the history of OSM data. Take a look at the [documentation of the ohsome API](https://docs.ohsome.org/ohsome-api/stable) or go through the [Tutorial](https://github.com/GIScience/ohsome-py/blob/master/notebooks/Tutorial.ipynb) to get started on how to use *ohsome-py*.

## Installation

### Using pip

You can install *ohsome-py* using pip, which will also install all dependencies.

```
$ pip install ohsome
```

### Using Anaconda

*ohsome-py* is not available through Conda. So if you are using Conda, create a new conda environment and install your required dependencies as well as those from *ohsome-py* (see [pyproject.toml](pyproject.toml)) before installing *ohsome-py* using pip. Please note that there might be issues when [using pip within anaconda](https://www.anaconda.com/blog/using-pip-in-a-conda-environment). To avoid issues we advise to install everything in a new conda environment.

### Dependencies for Jupyter Notebooks

If you want to run the Jupyter Notebook [Tutorial](https://github.com/GIScience/ohsome-py/blob/master/notebooks/Tutorial.ipynb) you also need to install `jupyter` and `matplotlib` e.g.

```
$ pip install jupyter matplotlib
```

## Usage

All queries are handled by an `OhsomeClient` object, which also provides information about the current ohsome API instance, e.g. `start_timestamp` and `end_timestamp` indicate the earliest and the latest possible dates for a query.

``` python
from ohsome import OhsomeClient
client = OhsomeClient()
client.start_timestamp # --> '2007-10-08T00:00:00Z'
client.end_timestamp # --> '2021-01-23T03:00Z'
```

### 1. Data Aggregation

**Example:** The area of OSM elements tagged as _landuse=farmland_ using the [/elements/area](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Aggregation#/Elements%20Area/area_1) endpoint:

``` python
response = client.elements.area.post(bboxes=[8.625,49.3711,8.7334,49.4397],
				      time="2014-01-01",
				      filter="landuse=farmland and geometry:polygon")
```

The single components of the endpoint URL are appended as method calls to the `OhsomeClient` object. Use automatic code completion to find valid endpoints. Alternatively, you can define the endpoint as argument in the `.post()` method.

``` python
response = client.post(endpoint="elements/area",
		       bboxes=[8.625,49.3711,8.7334,49.4397],
		       time="2020-01-01",
		       filter="landuse=farmland and geometry:polygon")
```

Responses from the data aggregation endpoints can be converted to a `pandas.DataFrame` object using the `OhsomeResponse.as_dataframe()` method.

```
response_df = response.as_dataframe()
```

### 2. Data Extraction

**Example:** OSM elements tagged as _landuse=farmland_ including their geometry and tags using the [/elements/geometry](https://api.ohsome.org/v1/swagger-ui.html?urls.primaryName=Data%20Extraction#/Data%20Extraction/elementsGeometry_1) endpoint:

``` python
client = OhsomeClient()
response = client.elements.geometry.post(bboxes=[8.625,49.3711,8.7334,49.4397],
					 time="2020-01-01",
					 filter="landuse=farmland and geometry:polygon",
					 properties="tags")
response_gdf = response.as_dataframe()
```

Responses from the data extraction endpoint can be converted to a `geopandas.GeoDataFrame`  using the `OhsomeResponse.as_dataframe()` method, since the data contains geometries.

### Query Parameters

All query parameters are described in the [ohsome API documentation](https://docs.ohsome.org/ohsome-api/stable) and can be passed as `string` objects to the `post()` method. Other Python data types are accepted as well.

#### Boundary

The [boundary](https://docs.ohsome.org/ohsome-api/stable/boundaries.html) of the query can be defined using the `bpolys`, `bboxes` and `bcircles` parameters. The coordinates have to be given in WGS 84 (EPSG:4326).

##### bpolys

The `bpolys` parameter can be passed as a `geopandas.GeoDataFrame` containing the polygon features.

``` python
bpolys = gpd.read_file("./data/polygons.geojson")
client.elements.count.groupByBoundary.post(bpolys=bpolys, filter="amenity=restaurant")
```

##### bboxes

The `bboxes` parameter contains the coordinates of one or several bounding boxes.

``` python
bboxes = [8.7137,49.4096,8.717,49.4119] # one bounding box
bboxes = [[8.7137,49.4096,8.717,49.4119], [8.7137,49.4096,8.717,49.4119]]
bboxes = {"A": [8.67066, 49.41423, 8.68177, 49.4204],
	  "B": [8.67066, 49.41423, 8.68177, 49.4204]}
```

##### bcircles

The `bcircles` parameter contains one or several circles defined through the coordinates of the centroids and the radius in meters.

```python
bcircles = [8.7137,49.4096, 100]
bcircles = [[8.7137,49.4096, 100], [8.7137,49.4096, 300]]
bcircles = {"Circle1": [8.695, 49.41, 200],
	    "Circle2": [8.696, 49.41, 200]}
```

#### Time

The [time](https://docs.ohsome.org/ohsome-api/stable/time.html) parameter must be ISO-8601 conform can be passed in several ways

```python
time = '2018-01-01/2018-03-01/P1M'
time = ['2018-01-01', '2018-02-01', '2018-03-01']
time = datetime.datetime(year=2018, month=3, day=1)
time = pandas.date_range("2018-01-01", periods=3, freq="M")
```
## Citation

When using [ohsome-py](https://github.com/GIScience/ohsome-py) e.g. for a publication or elsewhere, please cite the ohsome-api as described in their [citation recommendation](https://github.com/GIScience/ohsome-api/blob/master/README.md#how-to-cite) for example like

> M. Raifer, R. Troilo, F.-B. Mocnikand M. Schott, ‘OSHDB - OpenStreetMap History Data Analysis version 1.2.1 accessed via the ohsome-py library version 0.3.0’. Zenodo, Sep. 29, 2023. doi: 10.5281/zenodo.8391737.


```bibtex
@software{raifer_2023_7713347,
  author       = {Raifer, Martin and
                  Troilo, Rafael and
                  Mocnik, Franz-Benjamin and
                  Schott, Moritz},
  title        = {OSHDB - OpenStreetMap History Data Analysis version 1.2.1 accessed via the ohsome-py library version 0.3.0},
  month        = sep,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {1.2.1},
  doi          = {10.5281/zenodo.8391737},
  url          = {https://doi.org/10.5281/zenodo.8391737}
}
```

## Contribution Guidelines

The easiest way to contribute is to file a comprehensive [issue](https://github.com/GIScience/ohsome-py/issues) with a reproducible example. Pull requests are always welcome, so if you want to contribute to this project, please fork the repository or create a new branch containing your changes. Follow the steps below to make sure that your contributed code follows the code style and does not break any functionality. Create a **pull request to the main/master** branch once it is ready to be merged.

### Install Package

This package uses [poetry](https://python-poetry.org/) for dependency management. To install all packages necessary for testing and development run

`poetry install`

### Install Pre-Commit Hooks

**Install the pre-commit hooks** in our local git repo before committing to ensure homogenous code style.

`poetry run pre-commit install`

### Run Tests

**Before pushing your commits**, run the python unit tests

`poetry run pytest`

#### VCR

ohsome-py records responses using [VCR](https://vcrpy.readthedocs.io/en/latest/) via [pytest-recording](https://github.com/kiwicom/pytest-recording) to prevent unnecessary network traffic and computing during testing. If you implement a test or change an existing one, make sure to update the recorded cassettes. In addition, you should delete all cassettes after a certain time (e.g. every 6m or on each new ohsome release) and re-record them. To do that run

`poetry run pytest --record-mode=all`

## References

The design of this package was inspired by the blog post [Using Python to Implement a Fluent Interface to Any REST API](https://sendgrid.com/blog/using-python-to-implement-a-fluent-interface-to-any-rest-api/) by Elmer Thomas.
