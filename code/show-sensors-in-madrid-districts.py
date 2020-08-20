"""
Author: Jamal Toutouh (toutouh@mit.edu) - www.jamal.es
"""

# Shapes are shown using cartpy

import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
import descartes

import contextily as ctx


# Create DataFrames with required data
madrid_central_df = pd.read_csv('../data/Camaras_MCDic_2018.csv', index_col=None, sep=';',  encoding = 'ISO-8859-1')
air_quality_sensors_df = pd.read_csv('../data/stations-information.csv', index_col=None, sep=',',  encoding = 'ISO-8859-1')

# Create geometry objects to create GeoDataFrames
geometry_mc = [Point(xy) for xy in zip(madrid_central_df.Longitud, madrid_central_df.Latitud)]
geometry_aq_sensors = [Point(xy) for xy in zip(air_quality_sensors_df.Longitud, air_quality_sensors_df.Latitud)]

# Add geometries to the DataFrames
madrid_central_df['geometry'] = geometry_mc
air_quality_sensors_df['geometry'] = geometry_aq_sensors

# Create GeoDataFrames with the locations (Points) to show
crs = {'init': 'epsg:4326'}
aq_sensor_locs = gpd.GeoDataFrame(air_quality_sensors_df, crs=crs, geometry=geometry_aq_sensors)
aq_sensor_locs= aq_sensor_locs.to_crs(epsg=3857)

# Create GeoDataFrame to plot the shaded area of Madrid Central with madrid_central_df data
geometry_xy = [(x, y) for x, y in zip(madrid_central_df.Longitud, madrid_central_df.Latitud)]
mc_polygon = Polygon(geometry_xy)
mc_area = gpd.GeoSeries(mc_polygon, crs=crs)
mc_area = mc_area.to_crs(epsg=3857)

# Read shape files
shapefile = '../data/distritos-madrid-shape/Distritos.shp'
madrid_dist_shapes = list(shpreader.Reader(shapefile).geometries())


# Create figure and projection
crs_epsg = ccrs.epsg('3857')
fig, ax = plt.subplots(subplot_kw={'projection': crs_epsg}, figsize=(10, 10))

# Zoom in Madrid
ax.set_extent([-3.838983, -3.528423, 40.319002, 40.629588], crs=ccrs.PlateCarree()) #Set zoom in Spain

# Create projection for the shapes. The shapes in Spain require the following projection (which can be found in *.proj files):
# PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-3.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]
proj = ccrs.TransverseMercator(central_longitude=-3.0,central_latitude=0.0,
                           false_easting=500000.0,false_northing=0.0,
                           scale_factor=0.9996)
ax.add_geometries(madrid_dist_shapes, crs=proj, edgecolor='black', facecolor='none', alpha=0.5)

# Plot the shaded area
mc_area.plot(ax=ax, alpha=0.5, edgecolor='k', lw=4)

# Plot the sensors location
aq_sensor_locs.plot(ax=ax, markersize=10, alpha=0.5, color='blue', edgecolor='k')

# Create labels for the sensors and plot them
bbox_props = dict(boxstyle="circle,pad=0.2", fc="white", ec="k", lw=2)
for x, y, label in zip(aq_sensor_locs.geometry.x, aq_sensor_locs.geometry.y, aq_sensor_locs.Id):
    ax.annotate('{:02d}'.format(label), xy=(x, y), xytext=(0, 0), size=15, bbox=bbox_props, textcoords="offset points")


# Add background base map
add_background_map = False
if add_background_map:
    ctx.add_basemap(ax)
ax.set_axis_off() # remove the axis ticks
plt.tight_layout() # adjust the padding between figure edges

plt.savefig('../images/mc-sensors-in-districts.png')
plt.savefig('../images/mc-sensors-in-districts.eps')
plt.show()


