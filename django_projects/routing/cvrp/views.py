import pandas as pd
from django.shortcuts import render
from django.views import generic

from .base.services import Geocoding
from .models import Driver, Route, Location, Address
from .base import common
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


def home(request):
    """
    View function for driver page of site.
    :return:
    """

    # Get drivers in database
    num_drivers = Driver.objects.all().count()
    num_routes = Route.objects.all().count()
    num_locations = Location.objects.all().count()

    context = {
        'num_drivers': num_drivers,
        'num_locations': num_locations,
        'num_routes': num_routes
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


class DriverDetailView(generic.DetailView):
    model = Driver
