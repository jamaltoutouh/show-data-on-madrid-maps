# Shapes are shown using geopandas
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
import descartes
import contextily as ctx

# Adds the sensors information to de GeoDataFrame
def add_sensors_to_districts(districts, sensors):
    districts_sensors_list = list()
    for index, row in districts.iterrows():
        sensors_list = list()
        for i in range(sensors.shape[0]):
            if row.geometry.contains(sensors.iloc[i].geometry): sensors_list.append(i)
        districts_sensors_list.append(sensors_list)
    districts['sensors'] = districts_sensors_list
    return districts


# Adds values to de GeoDataFrame from a given metric to be used to get the colours
def add_sensors_and_values_to_districts(districts, sensors, metric='GAP'):
    districts_sensors_list = list()
    districts_values_list = list()
    for index, row in districts.iterrows():
        sensors_list = list()
        values_list = list()
        for index_sensors, row_sensors in sensors.iterrows():
            if row.geometry.contains(row_sensors.geometry):
                sensors_list.append(index_sensors)
                values_list.append(row_sensors[metric])

        districts_sensors_list.append(sensors_list)

        value=sum(values_list)/len(values_list) if len(values_list)>0 else None
        districts_values_list.append(value)

    districts['sensors'] = districts_sensors_list
    districts['values'] = districts_values_list
    return districts

# Create DataFrames with required data
air_quality_sensors_df = pd.read_csv('../data/stations-information.csv', index_col=None, sep=',',  encoding = 'ISO-8859-1')
# Create geometry objects to create GeoDataFrames
geometry_aq_sensors = [Point(xy) for xy in zip(air_quality_sensors_df.Longitud, air_quality_sensors_df.Latitud)]
# Add geometries to the DataFrames
air_quality_sensors_df['geometry'] = geometry_aq_sensors
# Create GeoDataFrames with the locations (Points) to show
crs = {'init': 'epsg:4326'}
aq_sensor_locs = gpd.GeoDataFrame(air_quality_sensors_df, crs=crs, geometry=geometry_aq_sensors)
aq_sensor_locs= aq_sensor_locs.to_crs(epsg=3857)

crs_epsg = ccrs.epsg('3857')

# ax = plt.axes(projection=ccrs.Orthographic(11, 42))
fig, ax = plt.subplots(subplot_kw={'projection': crs_epsg}, figsize=(10, 10))

# Zoom in Madrid
ax.set_extent([-3.838983, -3.528423, 40.319002, 40.629588], crs=ccrs.PlateCarree()) #Set zoom in Spain

# Read shape files
madrid_dist_shape_file = '../data/distritos-madrid-shape/Distritos.shp'
madrid_dist_shapes = list(shpreader.Reader(madrid_dist_shape_file).geometries())

districts_data = gpd.read_file(madrid_dist_shape_file)
districts_data = districts_data.to_crs(epsg=3857)

districts_data = add_sensors_and_values_to_districts(districts_data, aq_sensor_locs, 'GAP')

districts_data.plot(ax=ax, column='values',  cmap='summer', legend=True, linewidth=1, edgecolor='k')
# Plot the sensors location
aq_sensor_locs.plot(ax=ax, markersize=60, alpha=0.5, color='blue', edgecolor='k',)

# Add background base map
ax.set_axis_off() # remove the axis ticks
plt.tight_layout() # adjust the padding between figure edges

plt.savefig('../images/mc-results-in-districts.png')
plt.savefig('../images/mc-results-in-districts.eps')
plt.show()


