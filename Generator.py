import pandas as pd
from IPython.core.display import display

from Address import Address
from DistanceMatrix import DistanceMatrix

# Build a list of Addresses
from Geocoding import Geocoding

add0 = Address(street='305 Elm St', city='Weston', state='NE', zipcode='68070')
add1 = Address(street='2073 23rd St', city='Wahoo', state='NE', zipcode='68066')
add2 = Address(street='16th St & Locust St', city='Wahoo', state='NE', zipcode='68066')
add3 = Address(street='2237 N Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add4 = Address(street='1799 N Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add5 = Address(street='1661 N Chestnut St', city='Wahoo', state='NE', zipcode='68066')
add6 = Address(street='16th St & Chestnut St', city='Wahoo', state='NE', zipcode='68066')
add7 = Address(street='2212 N Maple St', city='Wahoo', state='NE', zipcode='68066')
add8 = Address(street='2025 N Maple St', city='Wahoo', state='NE', zipcode='68066')
add9 = Address(street='1744 N Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add10 = Address(street='1699 N Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add11 = Address(street='18th St & Oak St', city='Wahoo', state='NE', zipcode='68066')
add12 = Address(street='W 15th St & Oak St', city='Wahoo', state='NE', zipcode='68066')
add13 = Address(street='16th St & Locust St', city='Wahoo', state='NE', zipcode='68066')
add14 = Address(street='16th St & Sycamore', city='Wahoo', state='NE', zipcode='68066')
add15 = Address(street='1702 N Walnut St', city='Wahoo', state='NE', zipcode='68066')
add16 = Address(street='16th St & Walnut St', city='Wahoo', state='NE', zipcode='68066')
add17 = Address(street='16th St & Oak St', city='Wahoo', state='NE', zipcode='68066')
add18 = Address(street='839 W 16th St', city='Wahoo', state='NE', zipcode='68066')
add19 = Address(street='15th St & Locust St', city='Wahoo', state='NE', zipcode='68066')
add20 = Address(street='16th St & Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add21 = Address(street='15th St & Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add22 = Address(street='15th St & Hickory St', city='Wahoo', state='NE', zipcode='68066')
add23 = Address(street='820 W 15th St', city='Wahoo', state='NE', zipcode='68066')
add24 = Address(street='15th St & Hackberry Ct', city='Wahoo', state='NE', zipcode='68066')
add25 = Address(street='12th St & Hickory St', city='Wahoo', state='NE', zipcode='68066')
add26 = Address(street='14th St & Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add27 = Address(street='15th St & Chestnut St', city='Wahoo', state='NE', zipcode='68066')
add28 = Address(street='15th St & Broadway', city='Wahoo', state='NE', zipcode='68066')
add29 = Address(street='14th St & Hickory St', city='Wahoo', state='NE', zipcode='68066')
add30 = Address(street='12th St & Birch St', city='Wahoo', state='NE', zipcode='68066')
add31 = Address(street='13th St & Sycamore St', city='Wahoo', state='NE', zipcode='68066')
add32 = Address(street='14th St & Walnut St', city='Wahoo', state='NE', zipcode='68066')
add33 = Address(street='14th St & Chestnut St', city='Wahoo', state='NE', zipcode='68066')
# addn = Address(street ='', city='', state='', zipcode='')
adds = [add2,  add3,  add4,  add5,  add6,  add7,  add8,  add9,  add10, add11, add12,
        add13, add14, add15, add16, add17, add18, add19, add20, add21, add22, add23,
        add24, add25, add26, add27, add28, add29, add30, add31, add32, add33]

adds_used = []
for add in adds:
    if add not in adds_used:
        adds_used.append(add)

# print(geocodes)

# for i in log:
# print(i)


# data = pd.read_csv() # use excel data

# adds = []
# for address in data:
# add = Address(street = "")
# adds.append(add)

## Read individual rows, use field to convert row to Address object

key = 'AhW6XA1uWQ5iKrnO_BTIsEWUrVOKHI-5k6jm12ICzsTVrIIR55BtSRSnS9xeiTWj'

# distance value in km, time in minutes
all_geocodes, log = Geocoding.get_geocodes(adds_used)
print(f'Number of geocode retrieves: {len(all_geocodes)}')
print(f'Number of failed geocoding: {len(log)}')
geocodes_map = {geocode: index for index, geocode in enumerate(all_geocodes)}

# Request distance and duration matrices
distance_map, duration_map, response = DistanceMatrix.request_matrix(list(geocodes_map.keys()), key, 'driving', size=10)

print(f'API call status: {response.status_code}')

# Get Display matrices
distance_matrix = DistanceMatrix.get_matrix(distance_map, geocodes_map)
duration_matrix = DistanceMatrix.get_matrix(duration_map, geocodes_map)

print("\nDistance Matrix")
display(pd.DataFrame(distance_matrix))

print("\nDuration Matrix")
display(pd.DataFrame(duration_matrix))
