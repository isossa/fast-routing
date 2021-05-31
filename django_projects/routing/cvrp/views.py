import pandas as pd
from django.forms import modelformset_factory, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .base import common
from .forms import BuildRouteForm, DriverForm, BaseDriverFormSet, LocationForm, BaseLocationFormSet
from .models import Driver, Route, Location, Address
from .utils import dataframeutils


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


def update_address_db():
    data = load_addresses_from_csv('./data/RandomAddresses.xlsx')
    update_address_db_helper(data)


def load_addresses_from_csv(filename):
    # Load addresses
    data = pd.read_excel(filename)

    # Clean data
    temp_df = data.select_dtypes(include='object')
    data[temp_df.columns] = temp_df.apply(lambda x: x.str.strip())
    data.drop_duplicates(inplace=True, ignore_index=True)
    dataframeutils.standardize_dataframe_columns(data)
    print(f'Reading {len(data)} addresses.')
    return data


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


def add_route(request):
    number_drivers = Driver.objects.count()
    DriverFormSet = formset_factory(DriverForm, formset=BaseDriverFormSet, extra=1, max_num=number_drivers)
    driver_form = DriverFormSet()  # queryset=Driver.objects.none()

    number_addresses = Address.objects.count()
    LocationFormSet = formset_factory(LocationForm, formset=BaseLocationFormSet, extra=1, max_num=number_addresses)
    location_form = LocationFormSet()

    if request.method == "POST":
        # address = get_object_or_404(Address)
        form = BuildRouteForm(request.POST)

        if form.is_valid():
            # Process data
            # Do some processing
            pass

            # Redirect to a new URL:
            return HttpResponseRedirect(reverse('create_routes'))

    context = {
        'route_form': BuildRouteForm(),
        'driver_form': driver_form,
        'location_form': location_form,
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
