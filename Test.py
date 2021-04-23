from IPython.core.display import display

from Address import *
from Geocoding import *
from DistanceMatrix import *
import pandas as pd
import os

from dataframeutils import standardize_dataframe_columns

# Load addresses
address_location = '..\\ISC Project\\ISC Project Code\\RandomAddresses.xlsx'
data = pd.read_excel(address_location)

# Clean data
temp_df = data.select_dtypes(include='object')
data[temp_df.columns] = temp_df.apply(lambda x: x.str.strip())
data.drop_duplicates(inplace=True, ignore_index=True)
standardize_dataframe_columns(data)
print(f'Reading {len(data)} addresses.')

# Get geocodes
addresses = Address.build_addresses(data)
all_geocodes, log = Geocoding.get_geocodes(addresses)
print(f'Number of geocode retrieves: {len(all_geocodes)}')
print(f'Number of failed geocoding: {len(log)}')
geocodes_map = {geocode : index for index, geocode in enumerate(all_geocodes)}

# Request distance and duration matrices
api_key = os.environ['BING_MAPS_API_KEY']
distance_map, duration_map, response = DistanceMatrix.request_matrix(list(geocodes_map.keys()), api_key, 'driving', size=10)

print(f'API call status: {response.request}')

# Get Display matrices
distance_matrix = DistanceMatrix.get_matrix(distance_map, geocodes_map)
duration_matrix = DistanceMatrix.get_matrix(duration_map, geocodes_map)

print("\nDistance Matrix")
display(pd.DataFrame(distance_matrix))

print("\nDuration Matrix")
display(pd.DataFrame(duration_matrix))