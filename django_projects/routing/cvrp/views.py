from pickle import load
from .database import DistanceMatrixDB, DurationMatrixDB
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory, forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from . import common, services, algorithms
from .forms import DriverForm, BaseDriverFormSet, LocationForm, BaseLocationFormSet, DefaultForm, DriverFormSetHelper
from .models import Driver, Route, Location, Address
from .utils import dataframeutils
from .utils.savingsutils import SavingsDB

import os


def load_addresses_from_xls(filename):
    # Load addresses
    data = pd.read_excel(filename)

    # Clean data
    temp_df = data.select_dtypes(include='object')
    data[temp_df.columns] = temp_df.apply(lambda x: x.str.strip())
    data.drop_duplicates(inplace=True, ignore_index=True)
    dataframeutils.standardize_dataframe_columns(data)
    print(f'Reading {len(data)} addresses.')
    return data


def update_address_db():
    data = load_addresses_from_xls('./data/RandomAddresses.xlsx')
    update_address_db_helper(data)


def update_address_db_helper(data):
    # Get geocodes
    addresses = common.Address.build_addresses(data)

    for address in addresses:
        # Geocode addresses
        address.coordinates
        if address.latitude and address.longitude:
            address_db = Address(street=address.street, city=address.city, state=address.state, country=address.country,
                                 zipcode=address.zipcode, latitude=address.latitude, longitude=address.longitude,
                                 coordinates=address.coordinates, info=address.info)
            address_db.save()


def refresh():
    """Ensure that every address is geocoded"""
    for address in Address.objects.filter(longitude__exact=''):
        address_copy = common.Address(street=address.street, city=address.city, state=address.state,
                                      country=address.country, zipcode=address.zipcode)
        address.latitude = address_copy.latitude
        address.longitude = address_copy.longitude
        address.coordinates = address_copy.coordinates
        address.info = address_copy.info
        address.save()


def get_distance_matrix():
    address_list = []
    for address in Address.objects.all():
        print(address, address.coordinates)
        address_obj = common.Address(street=address.street, city=address.city, state=address.state, country=address.country, zipcode=address.zipcode)
        address_list.append(address_obj)

    DistanceMatrixDB.distance_matrix, DurationMatrixDB.duration_matrix, response = services.DistanceMatrix.request_matrix(address_list[:5], os.environ['BING_MAPS_API_KEY'], 'driving', 1)

    print(response)

    print(DistanceMatrixDB.distance_matrix)

    DistanceMatrixDB.save('./cache/test_distance_matrix')
    DurationMatrixDB.save('./cache/test_duration_matrix')


def setup():
    DistanceMatrixDB.load('./cache/test_distance_matrix')
    DurationMatrixDB.load('./cache/test_duration_matrix')



def get_matrix(geocodes: list, matrix:dict):
    matrix_out = {}
    
    for origin in geocodes:
        if origin in matrix:
            temp = {}
            for destination in geocodes:
                if destination in matrix:
                    if origin != destination:
                        temp.update({destination: matrix[origin][destination]})
        matrix_out[origin] = temp
    return matrix_out


def route(request):
    return render(request, 'route_home.html', context=None)


def new_route(request):
    return render(request, 'new_route.html', context=None)


def export(request):
    routes = Route.objects.all()
    context = {
        'routes': routes
    }
    return render(request, 'export_home.html', context=context)


def build_routes(request):
    return render(request, 'create_routes.html', context=None)


def str2address(address: str) -> common.Address:
    fields = [x.strip() for x in address.split(',')]
    address = common.Address(street=fields[0], city=fields[1], state=fields[2], country=fields[3], zipcode=fields[4])
    return address


def str2driver(driver: str) -> common.Driver:
    fields = [x.strip() for x in driver.split(',')]
    role = fields[1]
    fields = [x.strip() for x in fields[0].split(' ')]
    driver = common.Driver(first_name=fields[0], last_name=fields[1], role=role)
    return driver


def get_geocode(address: Address) -> str:
    coordinates = address.coordinates
    return coordinates[1:len(coordinates) - 1]

# get_distance_matrix()
setup()
# print("\n")
# print(DistanceMatrixDB.distance_matrix)

# add1 = common.Address(street="5545 Center St", city="Omaha", state="Nebraska", country="United States", zipcode=68106)
# add2 = common.Address(street="9029 Burt St", city="Omaha", state="Nebraska", country="United States", zipcode=68114)

# print("\n")

# print(DistanceMatrixDB.distance_between(add1, add2))
# print(DurationMatrixDB.duration_between(add1, add2))

# print(SavingsDB.compute_saving_matrix(DistanceMatrixDB.distance_matrix, add1))



def create_routes(request):
    number_drivers = Driver.objects.count()
    number_addresses = Address.objects.count()
    DriverFormSet = formset_factory(DriverForm, formset=BaseDriverFormSet, max_num=number_drivers)
    LocationFormSet = formset_factory(LocationForm, formset=BaseLocationFormSet, max_num=number_addresses)
    DefaultFormset = formset_factory(DefaultForm)

    # print("CREATE ROUTES")
    # print(request.POST)
    # print(request.get_full_path())
    if request.method == "POST":
        driver_formset = DriverFormSet(request.POST, prefix='drivers')  # queryset=Driver.objects.none()
        location_formset = LocationFormSet(request.POST, prefix='locations')
        default_formset = DefaultFormset(request.POST, prefix='default')
        # print(default_formset.is_valid())
        # print(driver_formset.is_valid())
        # print(location_formset.is_valid())

        if default_formset.is_valid() and driver_formset.is_valid() and location_formset.is_valid():
            # Process data
            print("BEGINNING PROCESSING")
            print(default_formset.cleaned_data)
            print(driver_formset.cleaned_data)
            print(location_formset.cleaned_data)

            home_depot_obj = str2address(default_formset.cleaned_data[0]['departure_field'])
            vehicle_capacity = int(default_formset.cleaned_data[0]['vehicle_capacity_field'])
            geocodes = []

            result_set = Address.objects.filter(street__exact = home_depot_obj.street, city__exact = home_depot_obj.city, state__exact = home_depot_obj.state, zipcode__exact = home_depot_obj.zipcode)

            add = result_set[0]
            print(add.coordinates)
            geocodes.append(get_geocode(add))

            print("\n\n")

            driver_set = []
            for driver_data in driver_formset.cleaned_data:
                if driver_data:
                    driver_obj = str2driver(driver_data['driver_field'])
                    result_set = Driver.objects.filter(first_name__exact=driver_obj.first_name, last_name__exact=driver_obj.last_name, role__exact=driver_obj.role)
                    driver_set.append(result_set[0])

            print("\n\n")

            location_set = []
            # Process locations
            for location_data in location_formset.cleaned_data:
                if location_data:
                    location_address = location_data['location_field']
                    address_obj = str2address(location_address)
                    result_set = Address.objects.filter(street__exact = address_obj.street, city__exact = address_obj.city, state__exact = address_obj.state, zipcode__exact = address_obj.zipcode)
                    
                    add = result_set[0]
                    geocodes.append(get_geocode(add))
                    location_db = Location(address=add, demand=location_data['demand_field'])
                    location_set.append(location_db)

            print(geocodes, end="\n\n\n")

            # Prepare data for cvrp algorithm
            distance_matrix = get_matrix(geocodes, matrix=DistanceMatrixDB.distance_matrix)

            print("\n\n")

            duration_matrix = get_matrix(geocodes, matrix=DurationMatrixDB.duration_matrix)

            savings_matrix = SavingsDB.compute_saving_matrix(distance_matrix, home_depot_obj)

            print(savings_matrix)

            SavingsDB.get_sorted_savings_matrix()

            print("\n\n")

            print(SavingsDB.sorted_savings_map)

            # Compute availability matrix
            print("\n\n")
            availability_map = {}
            for driver in driver_set:
                temp = {}
                for location in location_set:
                    if driver.language.all().intersection(location.address.language.all()):
                        temp[get_geocode(location.address)] = 1
                    else:
                        temp[get_geocode(location.address)] = 0
                availability_map[driver.first_name + ' ' + driver.last_name + ' ' + driver.role] = temp
                    
                print("\n\n")

            print(availability_map)

            # Get availability scores
            availability_scores = algorithms.get_availability_score(availability_map)

            print("\n\n\n")

            print("Availability scores: ", availability_scores)

            print("\n\n")

            # Ranking drivers by availability scores
            sorted_availability_map = {}
            for driver in availability_scores.keys():
                sorted_availability_map[driver] = availability_map[driver]

            print("Sorted availability map: ", sorted_availability_map)

            print("\n\n\n")

            # Display locations to be assigned
            for location in location_set:
                print(location.address, location.assigned)

            # Get demand by location
            customers_demand = {}
            for location in location_set:
                customers_demand[get_geocode(location.address)] = location.demand

            print("Customers demand: ", customers_demand)

            # Marginal capacity not defined - Default to zero

            # Run CVRP Solver
            print('Starting solver...', end="\n")

            location_assigned = {get_geocode(location.address) : not location.assigned for location in location_set}
            print("Location assigned ", location_assigned)
            routes_assigned, all_routes, location_assigned, all_assigned = algorithms.assign_routes(sorted_savings=SavingsDB.sorted_savings_map, 
            capacity=vehicle_capacity, demand=customers_demand, customers=location_assigned, availability_map=sorted_availability_map)

            print('\n\n\n')

            print("Solver output", end="\n\n")

            print("Routes Assigned", routes_assigned, "\n")
            print("All Routes", all_routes, end="\n")
            print("All Assigned", all_assigned, end="\n")
            for address in location_assigned:
                print(address)


            print("\n\n\n")

            # Redirect to a new URL:
            return HttpResponseRedirect(reverse('new_route'))
    else:
        driver_formset = DriverFormSet(request.GET or None, prefix='drivers')
        location_formset = LocationFormSet(request.GET or None, prefix='locations')
        default_formset = DefaultFormset(request.GET or None, prefix='default')

    context = {
        'default_formset': default_formset,
        'driver_formset': driver_formset,
        'driver_formset_helper': DriverFormSetHelper(),
        'location_formset': location_formset,
    }

    return render(request, 'create_routes.html', context)


def home(request):
    """
    View function for driver page of site.
    :return:
    """

    # Get drivers in database
    num_drivers = Driver.objects.all().count()
    num_routes = Route.objects.all().count()
    num_locations = Location.objects.all().count()
    num_addresses = Address.objects.all().count()

    context = {
        'num_drivers': num_drivers,
        'num_locations': num_locations,
        'num_routes': num_routes,
        'num_addresses': num_addresses
    }

    # Render the HTML template driver_list.html with the data in the context variable
    return render(request, 'home.html', context=context)


class DriverListView(generic.ListView):
    model = Driver

    refresh()

    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get the context data
        # This code is used as an example of how to modify variables.
        context = super(DriverListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Driver.objects.order_by('role', 'first_name', 'last_name')


class AddressListView(generic.ListView):
    model = Address

    def get_queryset(self):
        return Address.objects.order_by('country', 'state', 'city', 'street', 'zipcode')


class DriverDetailView(generic.DetailView):
    model = Driver

