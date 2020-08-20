import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
import descartes

import contextily as ctx

# Create DataFrames with required data
madrid_central_df = pd.read_csv('../data/Camaras_MCDic_2018.csv', index_col=None, sep=';',  encoding = 'ISO-8859-1')
air_quality_sensors_df = pd.read_csv('../data/stations-information.csv', index_col=None, sep=',',  encoding = 'ISO-8859-1')
lemur_df = pd.read_csv('../data/lemur-station.csv', index_col=None, sep=',',  encoding = 'ISO-8859-1')

# Create geometry objects to create GeoDataFrames
geometry_mc = [Point(xy) for xy in zip(madrid_central_df.Longitud, madrid_central_df.Latitud)]
geometry_aq_sensors = [Point(xy) for xy in zip(air_quality_sensors_df.Longitud, air_quality_sensors_df.Latitud)]
geom = [Point(xy) for xy in zip(lemur_df.Longitud, lemur_df.Latitud)]

# Add geometries to the DataFrames
madrid_central_df['geometry'] = geometry_mc
air_quality_sensors_df['geometry'] = geometry_aq_sensors
lemur_df['geometry'] = geom

# Create GeoDataFrames with the locations (Points) to show
crs = {'init': 'epsg:4326'}
aq_sensor_locs = gpd.GeoDataFrame(air_quality_sensors_df, crs=crs, geometry=geometry_aq_sensors)
aq_sensor_locs= aq_sensor_locs.to_crs(epsg=3857)
lemur_locs = gpd.GeoDataFrame(lemur_df, crs=crs, geometry=geom)
lemur_locs= lemur_locs.to_crs(epsg=3857)

# Create GeoDataFrame to plot the shaded area of Madrid Central with madrid_central_df data
geometry_xy = [(x, y) for x, y in zip(madrid_central_df.Longitud, madrid_central_df.Latitud)]
mc_polygon = Polygon(geometry_xy)
mc_area = gpd.GeoSeries(mc_polygon, crs=crs)
mc_area = mc_area.to_crs(epsg=3857)

# Show the data
fig, ax = plt.subplots(figsize=(10,10))

# Plot the sensors location
aq_sensor_locs.plot(ax=ax, markersize=10, alpha=0.5, color='blue', edgecolor='k')

# Create labels for the sensors and plot them
bbox_props = dict(boxstyle="circle,pad=0.2", fc="white", ec="k", lw=2)
for x, y, label in zip(aq_sensor_locs.geometry.x, aq_sensor_locs.geometry.y, aq_sensor_locs.Id):
    ax.annotate('{:02d}'.format(label), xy=(x, y), xytext=(-10, -3), size=15, bbox=bbox_props, textcoords="offset points")

# Plot the shaded area
mc_area.plot(ax=ax, alpha=0.5, edgecolor='k', lw=4)

# Add background base map
ctx.add_basemap(ax)
ax.set_axis_off() # remove the axis ticks
plt.tight_layout() # adjust the padding between figure edges

plt.savefig('../images/mc-sensors-location.png')
plt.savefig('../images/mc-sensors-location.eps')
plt.show()
