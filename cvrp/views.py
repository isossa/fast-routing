import concurrent.futures.thread
import os
import threading
import timeit

import django_rq
import pandas as pd
import timerit
from background_task import background
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db import ProgrammingError
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from multiprocessing import Pool

from django_rq import job

from . import common, services
from .common import Route, Location
from .database import DistanceMatrixDB, DurationMatrixDB
from .forms import DriverForm, BaseDriverFormSet, LocationForm, BaseLocationFormSet, DefaultForm, DriverFormSetHelper, \
    UploadAddressForm, UploadDriverForm
from .models import Driver, Address
from .utils import dataframeutils


def reset_databases():
    try:
        Driver.objects.all().delete()
        Address.objects.all().delete()
        cache.clear()
        print('RUNNING DATABASE RESET')
    except ProgrammingError:
        pass


def read_xls_data(filepath):
    """
    A generic method to read xls and xlsx files

    Args:
        filepath:

    Returns:

    """
    try:
        data = pd.read_excel(filepath)

        # Clean data
        temp_df = data.select_dtypes(include='object')
        data[temp_df.columns] = temp_df.apply(lambda x: x.str.strip())
        data.drop_duplicates(inplace=True, ignore_index=True)
        dataframeutils.standardize_dataframe_columns(data)
    except FileNotFoundError:
        return []

    return data


def save_address(address: common.Address):
    if address:
        if address.latitude and address.longitude:
            address_db = Address(street=address.street, city=address.city, state=address.state, country=address.country,
                                 zipcode=address.zipcode, latitude=address.latitude, longitude=address.longitude,
                                 coordinates=address.coordinates, info=address.info)
        else:
            address.coordinates
        address_db.save()


def save_driver(driver: common.Driver):
    if driver:
        driver_db = Driver(first_name=driver.first_name, last_name=driver.last_name, role=driver.role)
        driver_db.save()


def update_address_db_helper(data):
    addresses = common.Address.build_addresses(data)

    with concurrent.futures.thread.ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
        executor.map(save_address, addresses)


def update_driver_db_helper(data):
    drivers = common.Driver.get_drivers(data)
    with concurrent.futures.thread.ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
        executor.map(save_driver, drivers)


def update_driver_db(filepath):
    data = read_xls_data(filepath)
    update_driver_db_helper(data)


def update_address_db(filepath):
    data = read_xls_data(filepath)
    update_address_db_helper(data)


# update_driver_db('./data/Drivers.xlsx')

# def refresh():
#     """Ensure that every address is geocoded"""
#     for address in Address.objects.filter(longitude__exact=''):
#         address_copy = common.Address(street=address.street, city=address.city, state=address.state,
#                                       country=address.country, zipcode=address.zipcode)
#         address.latitude = address_copy.latitude
#         address.longitude = address_copy.longitude
#         address.coordinates = address_copy.coordinates
#         address.info = address_copy.info
#         address.save()


def get_matrices():
    address_list = []
    for address in Address.objects.all():
        address_obj = common.Address(street=address.street, city=address.city, state=address.state,
                                     country=address.country, zipcode=address.zipcode)
        address_list.append(address_obj)

    DistanceMatrixDB.distance_matrix, DurationMatrixDB.duration_matrix, response = services.DistanceMatrix.request_matrix(
        address_list, os.environ['BING_MAPS_API_KEY'], 'driving', 1)

    DistanceMatrixDB.save('./cache/test_distance_matrix')
    DurationMatrixDB.save('./cache/test_duration_matrix')


def setup():
    DistanceMatrixDB.load('./cache/test_distance_matrix')
    DurationMatrixDB.load('./cache/test_duration_matrix')


def get_matrix(geocodes: list, matrix: dict):
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
    context = {
        'routes_assigned': request.session.get('routes_assigned').items(),
        'all_routes': request.session.get('all_routes'),
        'location_assigned': request.session.get('location_assigned'),
        'all_assigned': request.session.get('all_assigned')
    }
    return render(request, 'new_route.html', context=context)


def export(request):
    routes = None  # Location.objects.all()
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


# print("\n")
# print(DistanceMatrixDB.distance_matrix)

# add1 = common.Address(street="5545 Center St", city="Omaha", state="Nebraska", country="United States", zipcode=68106)
# add2 = common.Address(street="9029 Burt St", city="Omaha", state="Nebraska", country="United States", zipcode=68114)

# print("\n")

# print(DistanceMatrixDB.distance_between(add1, add2))
# print(DurationMatrixDB.duration_between(add1, add2))

# print(SavingsDB.compute_saving_matrix(DistanceMatrixDB.distance_matrix, add1))

# def get_drivers(driver_formset):
#     driver_set = []
#     for driver_data in driver_formset.cleaned_data:
#         if driver_data:
#             driver_obj = str2driver(driver_data['driver_field'])
#             result_set = Driver.objects.filter(first_name__exact=driver_obj.first_name,
#                                                last_name__exact=driver_obj.last_name, role__exact=driver_obj.role)
#             driver_set.append(result_set[0])
#     return driver_set


# def get_locations(location_formset, geocodes):
#     if not geocodes:
#         geocodes = []
#     location_set = []
#     for location_data in location_formset.cleaned_data:
#         if location_data:
#             location_address = location_data['location_field']
#             address_obj = str2address(location_address)
#             result_set = Address.objects.filter(street__exact=address_obj.street, city__exact=address_obj.city,
#                                                 state__exact=address_obj.state, zipcode__exact=address_obj.zipcode)
#
#             add = result_set[0]
#             geocodes.append(get_geocode(add))
#             location_db = Location(address=add, demand=location_data['demand_field'])
#             location_set.append(location_db)
#     return location_set, geocodes


# def get_driver_availability(driver_set: list, location_set: list) -> dict:
#     availability_map = {}
#     for driver in driver_set:
#         temp = {}
#         for location in location_set:
#             if driver.language.all().intersection(location.address.language.all()):
#                 temp[get_geocode(location.address)] = 1
#             else:
#                 temp[get_geocode(location.address)] = 0
#         availability_map[driver.first_name + ' ' + driver.last_name + ' ' + driver.role] = temp
#     return availability_map

#
# def run_solver(default_formset, driver_formset, location_formset):
#     home_depot_obj = str2address(default_formset.cleaned_data[0]['departure_field'])
#     vehicle_capacity = int(default_formset.cleaned_data[0]['vehicle_capacity_field'])
#     geocodes = []
#
#     result_set = Address.objects.filter(street__exact=home_depot_obj.street, city__exact=home_depot_obj.city,
#                                         state__exact=home_depot_obj.state, zipcode__exact=home_depot_obj.zipcode)
#
#     add = result_set[0]
#     print(add.coordinates)
#     geocodes.append(get_geocode(add))
#
#     print("\n\n")
#
#     driver_set = get_drivers(driver_formset)
#
#     print("\n\n")
#
#     location_set, geocodes = get_locations(location_formset, geocodes)
#
#     print(geocodes, end="\n\n\n")
#
#     # Prepare data for cvrp algorithm
#     distance_matrix = get_matrix(geocodes, matrix=DistanceMatrixDB.distance_matrix)
#
#     print("\n\n")
#
#     duration_matrix = get_matrix(geocodes, matrix=DurationMatrixDB.duration_matrix)
#
#     savings_matrix = SavingsDB.compute_saving_matrix(distance_matrix, home_depot_obj)
#
#     print(savings_matrix)
#
#     SavingsDB.get_sorted_savings_matrix()
#
#     print("\n\n")
#
#     print(SavingsDB.sorted_savings_map)
#
#     # Compute availability matrix
#     print("\n\n")
#     availability_map = get_driver_availability(driver_set, location_set)
#
#     print("\n\n")
#
#     print(availability_map)
#
#     # Get availability scores
#     availability_scores = algorithms.get_availability_score(availability_map)
#
#     print("\n\n\n")
#
#     print("Availability scores: ", availability_scores)
#
#     print("\n\n")
#
#     # Ranking drivers by availability scores
#     sorted_availability_map = {}
#     for driver in availability_scores.keys():
#         sorted_availability_map[driver] = availability_map[driver]
#
#     print("Sorted availability map: ", sorted_availability_map)
#
#     print("\n\n\n")
#
#     # Display locations to be assigned
#     for location in location_set:
#         print(location.address, location.assigned)
#
#     # Get demand by location
#     customers_demand = {}
#     for location in location_set:
#         customers_demand[get_geocode(location.address)] = location.demand
#
#     print("Customers demand: ", customers_demand)
#
#     # Marginal capacity not defined - Default to zero
#     marginal_capacity = 1
#
#     # Run CVRP Solver
#     print('Starting solver...', end="\n")
#
#     location_assigned = {get_geocode(location.address): not location.assigned for location in location_set}
#     print("Location assigned ", location_assigned)
#     routes_assigned, all_routes, location_assigned, all_assigned = algorithms.assign_routes(
#         sorted_savings=SavingsDB.sorted_savings_map, capacity=vehicle_capacity, \
#         demand=customers_demand, customers=location_assigned, availability_map=sorted_availability_map,
#         duration_matrix=duration_matrix, marginal_capacity=marginal_capacity)
#
#     print('\n\n\n')
#
#     print("Solver output", end="\n\n")
#
#     print("Routes Assigned", routes_assigned, "\n")
#     print("All Routes", all_routes, end="\n")
#     print("All Assigned", all_assigned, end="\n")
#     print("Location assigned ", location_assigned)
#
#     # Post-processing
#     location_map = {}
#
#     for location in location_set:
#         location_map[get_geocode(location.address)] = location
#
#     print('\n\n\n')
#     routes_assigned_copy = []
#     for driver, route in routes_assigned.items():
#         if route:
#             temp = []
#             route_id = uuid.uuid4()
#             print("DRIVER ASSIGNED ", driver)
#             driver_fields = driver.split('_')
#             driver_index = driver_fields[1]
#             driver_fields = driver_fields[0].split(' ')
#             driver_obj = common.Driver(first_name=driver_fields[0], last_name=driver_fields[1], role=driver_fields[2])
#             result_set = Driver.objects.filter(first_name__exact=driver_obj.first_name,
#                                                last_name__exact=driver_obj.last_name, role__exact=driver_obj.role)
#             driver_obj = result_set[0]
#             for geocode in route:
#                 location = location_map[geocode]
#                 print(geocode, location)
#                 location.route_id = route_id
#                 location.assigned_to = driver_obj
#                 location.assigned = True
#                 location.save()
#                 temp.append(location)
#             routes_assigned_copy.append(driver_obj)
#             routes_assigned_copy.extend(temp)
#
#     routes_result = {}
#     for driver in routes_assigned.keys():
#         if routes_assigned[driver]:
#             driver_fields = driver.split('_')
#             driver_index = driver_fields[1]
#             driver_fields = driver_fields[0].split(' ')
#             driver_name = driver_fields[0] + ' ' + driver_fields[1]
#             print(driver_name)
#             temp = [str(home_depot_obj)]
#             for geocode in routes_assigned[driver]:
#                 coordinates = '(' + geocode + ')'
#                 result_set = Address.objects.filter(coordinates__exact=coordinates)
#                 print('\t', result_set[0])
#                 temp.append(str(result_set[0]))
#             print('\n')
#             temp.append(str(home_depot_obj))
#             routes_result[driver_name] = temp
#
#     print('\n\n\n')
#     for location in location_set:
#         print(location)
#
#     print("\n\n\n")
#
#     return routes_result, all_routes, location_assigned, all_assigned


def create_routes(request):
    # refresh()
    number_drivers = 1 if Driver.objects.count() == 0 else 1
    number_addresses = 1 if Address.objects.count() == 0 else 1
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

            routes_assigned, all_routes, location_assigned, all_assigned = None, None, None, None  # run_solver(default_formset, driver_formset,
            # location_formset)
            request.session['routes_assigned'] = routes_assigned
            request.session['all_routes'] = all_routes
            request.session['location_assigned'] = location_assigned
            request.session['all_assigned'] = all_assigned

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

    return render(request, 'create_routes.html', context=context)


def handle_file_upload(file):
    file_storage = FileSystemStorage()
    filename = file_storage.save(file.name, file)
    filepath = file_storage.path(filename)
    print(filename, filepath)

    data = pd.read_excel(filepath)

    update_address_db(filepath)


@job
def load_files(files):
    timer = timerit.Timerit(verbose=2)
    for time in timer:
        with concurrent.futures.thread.ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
            executor.map(handle_file_upload, files)


def settings(request):
    if request.method == 'POST':
        reset_databases()
        form = UploadAddressForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES:
                filenames = list(request.FILES.keys())
                print('FILENAMES', filenames)
                print(os.fork())
                files = [request.FILES[filenames[index]] for index in range(len(filenames))]
                queue = django_rq.get_queue(name='high', autocommit=True, is_async=True)
                queue.enqueue(load_files, files=files)
                # load_files(files)

            return HttpResponseRedirect(reverse('create_routes'))

    context = {
        'address_file_form': UploadAddressForm(),
        'driver_file_form': UploadDriverForm()
    }

    return render(request, 'settings.html', context=context)


# def home(request):
#     """
#     View function for driver page of site.
#     :return:
#     """
#
#     try:
#         # Get drivers in database
#         num_drivers = Driver.objects.all().count()
#         num_routes = Route.objects.all().count()
#         num_locations = Location.objects.all().count()
#         num_addresses = Address.objects.all().count()
#     except ProgrammingError:
#         num_drivers = 0
#         num_locations = 0
#         num_routes = 0
#         num_addresses = 0
#
#     context = {
#         'num_drivers': num_drivers,
#         'num_locations': num_locations,
#         'num_routes': num_routes,
#         'num_addresses': num_addresses
#     }
#
#     return render(request, 'home.html', context=None)


class DriverListView(generic.ListView):
    # model = Driver
    #
    # refresh()
    #
    # def get_context_data(self, *, object_list=None, **kwargs):
    #     # Call the base implementation first to get the context data
    #     # This code is used as an example of how to modify variables.
    #     context = super(DriverListView, self).get_context_data(**kwargs)
    #     return context
    #
    # def get_queryset(self):
    #     return Driver.objects.order_by('role', 'first_name', 'last_name')
    pass


class AddressListView(generic.ListView):
    # model = Address
    #
    # def get_queryset(self):
    #     return Address.objects.order_by('country', 'state', 'city', 'street', 'zipcode')
    pass


class DriverDetailView(generic.DetailView):
    # model = Driver
    pass
