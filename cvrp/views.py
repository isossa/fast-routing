import concurrent.futures.thread
import os
import uuid

import pandas as pd
import timerit
from django.core.files.storage import FileSystemStorage
from django.db import ProgrammingError
from django.forms import formset_factory
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from django.views.generic import TemplateView
from fpdf import FPDF

from . import common, services, algorithms
from .database import DistanceMatrixDB, DurationMatrixDB
from .forms import DriverForm, BaseDriverFormSet, LocationForm, BaseLocationFormSet, DefaultForm, DriverFormSetHelper, \
    UploadAddressForm, UploadDriverForm, UpdateMatrixCheckBox
from .models import Driver, Address, Location
from .utils import dataframeutils
from .utils.savingsutils import SavingsDB


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


def get_address_to_model(address: common.Address):
    return Address(street=address.street, city=address.city, state=address.state, country=address.country,
                   zipcode=address.zipcode, latitude=address.latitude, longitude=address.longitude,
                   coordinates=address.coordinates, info=address.info, is_home_depot=address.is_home_base)


def save_address(address: common.Address):
    if address:
        if address.latitude and address.longitude:
            address_db = get_address_to_model(address)
        else:
            address.coordinates
            address_db = get_address_to_model(address)
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


def get_matrices():
    try:
        address_list = []
        for address in Address.objects.all():
            address_obj = common.Address(street=address.street, city=address.city, state=address.state,
                                         country=address.country, zipcode=address.zipcode)
            address_list.append(address_obj)

        DistanceMatrixDB.distance_matrix, DurationMatrixDB.duration_matrix, response = services.DistanceMatrix. \
            request_matrix(address_list, os.environ['BING_MAPS_API_KEY'], 'driving', size=25)

        DistanceMatrixDB.save('./cache/distance_matrix')
        DurationMatrixDB.save('./cache/duration_matrix')
    except ProgrammingError:
        # INTENTIONALLY LEFT BLANK
        pass


def load_matrices():
    try:
        DistanceMatrixDB.load('./cache/distance_matrix')
        DurationMatrixDB.load('./cache/duration_matrix')
    except FileNotFoundError:
        get_matrices()


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


def geocode_to_address(geocode: str) -> Address:
    coordinates = '(' + geocode + ')'
    result_set = Address.objects.filter(coordinates__exact=coordinates)
    return result_set[0] if result_set else None


def get_drivers(driver_formset):
    driver_set = []
    for driver_data in driver_formset.cleaned_data:
        if driver_data:
            driver_obj = str2driver(driver_data['driver_field'])
            result_set = Driver.objects.filter(first_name__exact=driver_obj.first_name,
                                               last_name__exact=driver_obj.last_name, role__exact=driver_obj.role)
            driver_set.append(result_set[0])
    return driver_set


def get_locations(location_formset, geocodes):
    if not geocodes:
        geocodes = []
    location_set = []
    for location_data in location_formset.cleaned_data:
        if location_data:
            location_address = location_data['location_field']
            address_obj = str2address(location_address)
            result_set = Address.objects.filter(street__exact=address_obj.street, city__exact=address_obj.city,
                                                state__exact=address_obj.state, zipcode__exact=address_obj.zipcode)

            add = result_set[0]
            geocodes.append(get_geocode(add))
            location_db = Location(address=add, demand=location_data['demand_field'])
            location_set.append(location_db)
    return location_set, geocodes


def get_driver_availability(driver_set: list, location_set: list) -> dict:
    availability_map = {}
    for driver in driver_set:
        temp = {}
        for location in location_set:
            if driver.language.all().intersection(location.address.language.all()):
                temp[get_geocode(location.address)] = 1
            else:
                temp[get_geocode(location.address)] = 1  # IGNORE LANGUAGE REQUIREMENT
        availability_map[driver.first_name + ' ' + driver.last_name + ' ' + driver.role] = temp
    return availability_map


def run_solver(default_formset, driver_formset, location_formset):
    load_matrices()

    home_depot_obj = str2address(default_formset.cleaned_data[0]['departure_field'])
    vehicle_capacity = int(default_formset.cleaned_data[0]['vehicle_capacity_field'])
    geocodes = []

    result_set = Address.objects.filter(street__exact=home_depot_obj.street, city__exact=home_depot_obj.city,
                                        state__exact=home_depot_obj.state, zipcode__exact=home_depot_obj.zipcode)

    add = result_set[0]
    print('\nHome Depot', add.coordinates, end="\n\n")
    geocodes.append(get_geocode(add))

    driver_set = get_drivers(driver_formset)

    print("Drivers: ", driver_set)

    location_set, geocodes = get_locations(location_formset, geocodes)

    print('Geocodes: ', geocodes, end="\n\n")

    # Prepare data for cvrp algorithm
    distance_matrix = get_matrix(geocodes, matrix=DistanceMatrixDB.distance_matrix)

    print("Distance Matrix: ", distance_matrix, end="\n\n")

    duration_matrix = get_matrix(geocodes, matrix=DurationMatrixDB.duration_matrix)

    savings_matrix = SavingsDB.compute_saving_matrix(distance_matrix, home_depot_obj)

    print('Saving Matrix', savings_matrix, end="\n\n")

    SavingsDB.get_sorted_savings_matrix()

    print('Sorted Savings Matrix: ', SavingsDB.sorted_savings_map, end="\n\n")

    # Compute availability matrix
    availability_map = get_driver_availability(driver_set, location_set)

    print('Availability Map: ', availability_map, end="\n\n")

    # Get availability scores
    availability_scores = algorithms.get_availability_score(availability_map)

    print("Availability scores: ", availability_scores, end="\n\n")

    # Ranking drivers by availability scores
    sorted_availability_map = {}
    for driver in availability_scores.keys():
        sorted_availability_map[driver] = availability_map[driver]

    print("Sorted availability map: ", sorted_availability_map, end="\n\n")

    # Display locations to be assigned
    for location in location_set:
        print(location.address, 'is assigned', location.assigned)

    # Get demand by location
    customers_demand = {}
    for location in location_set:
        customers_demand[get_geocode(location.address)] = location.demand

    print("Customers demand: ", customers_demand, end="\n\n")

    # Run CVRP Solver
    print('Starting solver...', end="\n\n")

    active_locations = {get_geocode(location.address): not location.assigned for location in location_set}
    print("Location not assigned(active) ", active_locations)
    routes_assigned, all_routes, active_locations, all_assigned = algorithms.assign_routes(
        sorted_savings=SavingsDB.sorted_savings_map, capacity=vehicle_capacity,
        demand=customers_demand, customers=active_locations, availability_map=sorted_availability_map,
        duration_matrix=duration_matrix, marginal_capacity=0)

    active_locations = {location: status for location, status in active_locations.items() if status}

    print("Solver output", end="\n\n")

    print("Routes Assigned", routes_assigned, end="\n")
    print("All Routes", all_routes, end="\n")
    print("All Assigned", all_assigned, end="\n")
    print("Location Active ", active_locations, end="\n")

    # Post-processing
    location_map = {}

    for location in location_set:
        location_map[get_geocode(location.address)] = location

    print('Location Map', location_map, end='\n\n')

    routes_assigned_copy = []
    for driver, route_generated in routes_assigned.items():
        if route_generated:
            temp = []
            route_id = uuid.uuid4()
            print("DRIVER ASSIGNED ", driver)
            driver_fields = driver.split('_')
            driver_index = driver_fields[1]
            driver_fields = driver_fields[0].split(' ')
            driver_obj = common.Driver(first_name=driver_fields[0], last_name=driver_fields[1], role=driver_fields[2])
            result_set = Driver.objects.filter(first_name__exact=driver_obj.first_name,
                                               last_name__exact=driver_obj.last_name, role__exact=driver_obj.role)
            driver_obj = result_set[0]
            for geocode in route_generated:
                location = location_map[geocode]
                location.route_id = route_id
                location.assigned_to = driver_obj
                location.assigned = True
                location.save()
                temp.append(location)
            routes_assigned_copy.append(driver_obj)
            routes_assigned_copy.extend(temp)

    routes_result = {}
    for driver in routes_assigned.keys():
        if routes_assigned[driver]:
            driver_fields = driver.split('_')
            driver_index = driver_fields[1]
            driver_fields = driver_fields[0].split(' ')
            driver_name = driver_fields[0] + ' ' + driver_fields[1]
            temp = [str(home_depot_obj)]
            temp += [str(geocode_to_address(geocode)) for geocode in routes_assigned[driver]]
            temp.append(str(home_depot_obj))
            routes_result[driver_name] = temp

    locations_not_assigned = [str(geocode_to_address(location)) for location in active_locations.keys()]

    return routes_result, all_routes, locations_not_assigned, all_assigned


def create_routes(request):
    try:
        number_drivers = 1 if Driver.objects.count() == 0 else 1
    except ProgrammingError:
        number_drivers = 1

    try:
        number_addresses = 1 if Address.objects.count() == 0 else 1
    except ProgrammingError:
        number_addresses = 1

    DriverFormSet = formset_factory(DriverForm, formset=BaseDriverFormSet, max_num=number_drivers)
    LocationFormSet = formset_factory(LocationForm, formset=BaseLocationFormSet, max_num=number_addresses)
    DefaultFormset = formset_factory(DefaultForm)

    if request.method == "POST":
        driver_formset = DriverFormSet(request.POST, prefix='drivers')  # queryset=Driver.objects.none()
        location_formset = LocationFormSet(request.POST, prefix='locations')
        default_formset = DefaultFormset(request.POST, prefix='default')

        if default_formset.is_valid() and driver_formset.is_valid() and location_formset.is_valid():
            # Process data
            print("BEGINNING PROCESSING")
            print(default_formset.cleaned_data)
            print(driver_formset.cleaned_data)
            print(location_formset.cleaned_data)

            routes_assigned, all_routes, locations_not_assigned, all_assigned = run_solver(default_formset,
                                                                                           driver_formset,
                                                                                           location_formset)
            request.session['routes_assigned'] = routes_assigned
            request.session['all_routes'] = all_routes
            request.session['location_not_assigned'] = locations_not_assigned
            request.session['all_assigned'] = all_assigned

            print('FROM CREATE ROUTE')
            print('ROUTES ASSIGNED', request.session['routes_assigned'])
            print('ALL ROUTES', request.session['all_routes'])
            print('LOCATIONS ACTIVE', request.session['location_not_assigned'])
            print('ALL ROUTES ASSIGNED', request.session['all_assigned'])
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


def new_route(request):
    context = {
        'routes_assigned': request.session.get('routes_assigned').items(),
        'all_routes': request.session.get('all_routes'),
        'location_not_assigned': request.session.get('location_not_assigned'),
        'all_assigned': request.session.get('all_assigned')
    }
    return render(request, 'new_route.html', context=context)


def download_routes(request):
    pdf_file = 'routes.pdf'
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font(family='courier', style='B', size=18)
    pdf.cell(w=40, h=10, txt='Routes Assigned', border=0, ln=1)
    pdf.cell(w=40, h=10, txt='', border=0, ln=1)
    pdf.set_font('courier', '', 12)

    routes_assigned = request.session.get('routes_assigned').items()
    location_not_assigned = request.session.get('location_not_assigned')
    all_assigned = request.session.get('all_assigned')

    for driver, path in routes_assigned:
        pdf.set_font(family='courier', style='B', size=14)
        pdf.cell(200, 8, driver, 0, 1)
        pdf.set_font('courier', '', 12)
        for location in path:
            pdf.cell(200, 8, f'    {location}', 0, 1)
        pdf.cell(w=40, h=10, txt='', border=0, ln=1)

    if not all_assigned:
        pdf.set_font(family='courier', style='B', size=14)
        pdf.cell(w=40, h=10, txt='The following address(es) could not be assigned:', border=0, ln=1)
        pdf.set_font('courier', '', 12)

        for location in location_not_assigned:
            pdf.cell(200, 8, f'    {location}', 0, 1)
        pdf.cell(w=40, h=10, txt='', border=0, ln=1)

    pdf.output(pdf_file, 'F')

    return FileResponse(open(pdf_file, 'rb'), as_attachment=False, content_type='application/pdf')


def handle_file_upload(file):
    file_storage = FileSystemStorage()
    filename = file_storage.save(file.name, file)
    filepath = file_storage.path(filename)
    print(filename, filepath)
    try:
        if filename.lower().find('driver') != -1:
            while Driver.objects.all().exists():
                Driver.objects.all().delete()
    except ProgrammingError:
        pass

    try:
        if filename.lower().find('address') != -1:
            while Address.objects.all().exists():
                Address.objects.all().delete()
            print('DELETED ADDRESSES')
    except ProgrammingError:
        pass


def load_files(files):
    for file in files:
        timer = timerit.Timerit(verbose=2)
        handle_file_upload(file)


def settings(request):
    if request.method == 'POST':
        form = UploadAddressForm(request.POST, request.FILES)
        update_matrix = UpdateMatrixCheckBox(request.POST, None)
        if form.is_valid():
            if request.FILES:
                filenames = list(request.FILES.keys())
                print(request.FILES.keys(), request.FILES.values())
                files = [request.FILES[file] for file in filenames]
                load_files(files)
                print("Added files to storage system", files)
                try:
                    context = {'update_distance_matrix_field': request.POST['update_distance_matrix_field']}
                except MultiValueDictKeyError:
                    context = None

                return render(request, 'settings_loader.html', context=context)
            else:
                return HttpResponseRedirect(reverse('create_routes'))

    context = {
        'address_file_form': UploadAddressForm(),
        'driver_file_form': UploadDriverForm(),
        'update_matrix_checkbox': UpdateMatrixCheckBox()
    }

    return render(request, 'settings.html', context=context)


# def settings_load(request):
#     reset_databases()
#     # loop = asyncio.get_event_loop()
#     # async_function = sync_to_async(reset_databases)
#     # loop.create_task(async_function())
#     while True:
#         pass
#
#     return HttpResponseRedirect(reverse('create_routes'))


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

class IndexView(TemplateView):
    template_name = "index.html"


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
