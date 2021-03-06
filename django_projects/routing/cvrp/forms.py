from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Button, Div
from django import forms
from django.forms import BaseFormSet

from .models import Address, Driver


def get_addresses():
    address_choices = list()
    addresses = Address.objects.filter(is_home_depot__exact=0).order_by('zipcode', 'country', 'state', 'city', 'street')

    for address in addresses:
        address_choices.append((address.__str__(), address.__str__()))

    return address_choices


def get_home_depot():
    address_choices = list()
    addresses = Address.objects.filter(is_home_depot__exact=1).order_by('zipcode', 'country', 'state', 'city', 'street')

    for address in addresses:
        address_choices.append((address.__str__(), address.__str__()))

    return address_choices


# class DriverModelForm(forms.ModelForm):
#     class Meta:
#         model = models.Driver
#         fields = ['first_name', 'last_name']


class BaseLocationFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that a location is selected at most once.
        """
        if any(self.errors):
            return
        locations = []
        for form in self.forms:
            if form.cleaned_data:
                location = form.cleaned_data['location_field']
                # print(location)
                if location in locations:
                    raise forms.ValidationError('A location must be selected at most once.')
                else:
                    locations.append(location)


class DefaultForm(forms.Form):
    address_choices = get_home_depot()
    departure_choices = [('', 'Select Starting Location')]
    departure_choices.extend(address_choices)
    departure_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control',
                                   'required': 'required'}),
        choices=departure_choices, label="Departure")

    vehicle_capacity_field = forms.DecimalField(
        label="Vehicle Capacity",
        widget=forms.NumberInput(attrs={'class': 'form-control',
                                        'placeholder': 'Enter Vehicle Capacity',
                                        'required': 'required'}),
        min_value=1)


class BaseDriverFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that a driver is selected at most once.
        """
        if any(self.errors):
            return
        drivers = []
        for form in self.forms:
            if form.cleaned_data:
                driver = form.cleaned_data['driver_field']
                print(driver)
                if driver in drivers:
                    raise forms.ValidationError('A driver must be selected at most once.', code='duplicates_drivers')
                else:
                    drivers.append(driver)


class DriverForm(forms.Form):
    drivers = Driver.objects.all().order_by('role', 'first_name', 'last_name')

    driver_choices = list()
    for driver in drivers:
        driver_choices.append((driver.__str__(), driver.__str__()))

    driver_choices = [('', 'Select Driver')] + driver_choices

    driver_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control',
                                   'required': 'required'}),
        choices=driver_choices, label="")


class DriverFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = Layout(
            Fieldset('Drivers',
                     Div(
                         Row(
                             Column('driver_field', css_class='form-group col-md-8 mt-2'),
                             Button('remove-driver-btn', 'Remove', css_class='form-group col-md-2 btn '
                                                                             'btn-outline-danger btn-sm '
                                                                             'remove-driver-btn'),
                             Button('add-driver-btn', 'Add', css_class='form-group col-md-2 btn '
                                                                       'btn-no-outline-danger btn-sm '
                                                                       'add-driver-btn'),
                             css_class='form-row driver-container'
                         ),
                         css_class='form-group'
                     )
                     )
        )
        self.form_tag = False


class LocationForm(forms.Form):
    address_choices = get_addresses()
    address_choices = [('', 'Select Address')] + address_choices
    location_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control selectpciker',
                                   'data-live-search': 'true',
                                   'searchable': 'Search here...',
                                   'required': 'required'}),
        choices=address_choices, label='Address')
    demand_field = forms.DecimalField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control',
                                        'placeholder': 'Enter demand',
                                        'required': 'required'}))
