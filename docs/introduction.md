# Introduction

## Overview

`h3xplorer` is intended to help jump-start spatial analysis by using the Uber-created `h3` hexagon layer which covers the earth at 19 different resolutions. This enables comparable analysis to be carried out internationally at whatever scale is required.

## Without `h3xplorer`

If you wanted to take a dataset and plot it spatially as hexagons, it is expected that you'd need to do something like the below to do this without `h3xplorer`:

1. Bring your dataset into Python using `geopandas` (`read_file` or equivalent).
1. Use `h3-py` to find all of the relevant hexagons to your datasets spatial extent.
1. Assign the original data to hexagon references. This might be quite involved if you are using polygon data, using area assignment or similar, and requires knowledge of the sizing of the hexagons against your dataset.
1. Get the hexagon extents from `h3-py` and convert them into polygons using `shapely` then group these into a `GeoDataFrame`.
1. Join the hexagon polygons to the dataset.
1. Plot the hexagons.

This process is full of pitfalls / gotchas, and can be poorly optimised if you don't understand how `h3-py` works on the backend.

## With `h3xplorer`

`h3xplorer` is designed to carry out this pipeline, auto-size the hexagons to your data, and provide tools to automate the comparison of datasets once they're hexagons.

In the simplest form you can just do:

``` shell
h3x --file my_file.parquet --x "x" --y "y" --epsg 27700 --field "population" --output "C:/projects"
```

which will generate a local html file `C:/projects/my_file_population.html` using the population field for the colour scale. `h3xplorer` will guess at what resolution of hexagons you are likely to want, based on the bounding box of the dataset being used.

While if you want to specify arguments, you can control the process at a finer level:

``` shell
h3x --file my_file.parquet --x "x" --y "y" --epsg 27700 --field "population" --field "households" --cmap "rainbow" --size 8 --output "C:/projects"
```

which will generate a local html file `C:/projects/my_file_population_vs_households.html` as a comparison between the population and households fields.
