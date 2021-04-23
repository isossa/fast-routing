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
standardize_dataframe_columns(data)

subset_data = data[:5]

# Get geocodes
addresses = Address.build_addresses(subset_data)
geocodes = [add.coordinates_as_string() for add in addresses]

for i, add in enumerate(addresses):
    display(add, geocodes[i])

# get distance matrix
api_key = os.environ['BING_MAPS_API_KEY']
response = DistanceMatrix.request_matrix(geocodes, api_key, 'driving')

print(type(response))

print()

print(response)

