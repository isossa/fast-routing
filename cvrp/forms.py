from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, Button, Div
from django import forms
from django.db import ProgrammingError
from django.forms import BaseFormSet

from .models import Address, Driver


def get_addresses(home_depot=False):
    address_choices = list()
    try:
        flag = 1 if home_depot else 0
        addresses = Address.objects.filter(is_home_depot__exact=flag).order_by('zipcode', 'country', 'state', 'city',
                                                                               'street')
        for address in addresses:
            address_choices.append((address.__str__(), address.__str__()))
    except ProgrammingError:
        pass
    return address_choices


def get_drivers():
    driver_choices = list()

    try:
        drivers = Driver.objects.all().order_by('role', 'first_name', 'last_name')

        for driver in drivers:
            driver_choices.append((driver.__str__(), driver.__str__()))
    except ProgrammingError:
        pass

    return driver_choices


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
                if location in locations:
                    raise forms.ValidationError('A location must be selected at most once.')
                else:
                    locations.append(location)


class DefaultForm(forms.Form):
    departure_choices = [('', 'Select Starting Location')] + get_addresses(home_depot=True)
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

    def __init__(self, *args, **kwargs):
        departure_choices = [('', 'Select Starting Location')] + get_addresses(home_depot=True)
        super(DefaultForm, self).__init__(*args, **kwargs)
        self.fields['departure_field'].choices = departure_choices


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
                if driver in drivers:
                    raise forms.ValidationError('A driver must be selected at most once.', code='duplicates_drivers')
                else:
                    drivers.append(driver)


class DriverForm(forms.Form):
    driver_choices = [('', 'Select Driver')] + get_drivers()

    driver_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control',
                                   'required': 'required'}),
        choices=driver_choices, label="")

    def __init__(self, *args, **kwargs):
        super(DriverForm, self).__init__(*args, **kwargs)
        driver_choices = [('', 'Select Driver')] + get_drivers()
        self.fields['driver_field'].choices = driver_choices


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
    address_choices = [('', 'Select Address')] + get_addresses(home_depot=False)
    location_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control selectpicker',
                                   'data-live-search': 'true',
                                   'searchable': 'Search here...',
                                   'required': 'required'}),
        choices=address_choices, label='Address')
    demand_field = forms.DecimalField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control',
                                        'placeholder': 'Enter demand',
                                        'required': 'required'}))

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        address_choices = [('', 'Select Address')] + get_addresses(home_depot=False)
        self.fields['location_field'].choices = address_choices


class UploadAddressForm(forms.Form):
    address_file_location = forms.FileField(
        label='',
        required=False
    )


class UploadDriverForm(forms.Form):
    driver_file_location = forms.FileField(
        label='',
        required=False
    )
