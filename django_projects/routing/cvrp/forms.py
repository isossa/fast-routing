from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.forms import BaseFormSet

from .models import Address, Driver


def get_addresses():
    address_choices = list()
    addresses = Address.objects.all().order_by('zipcode', 'country', 'state', 'city', 'street')
    print(len(addresses))

    for address in addresses:
        address_choices.append((address.__str__(), address.__str__()))

    return address_choices


class DriverForm(forms.Form):
    drivers = Driver.objects.all().order_by('role', 'first_name', 'last_name')

    driver_choices = list()
    for driver in drivers:
        driver_choices.append((driver.__str__(), driver.__str__()))

    driver_choices = [('', 'Select Driver')] + driver_choices

    driver_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=driver_choices, label="")


# class DriverModelForm(forms.ModelForm):
#     class Meta:
#         model = models.Driver
#         fields = ['first_name', 'last_name']

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
                    raise forms.ValidationError('Drivers must be selected at most once.')
                else:
                    drivers.append(driver)


class LocationForm(forms.Form):
    address_choices = get_addresses()
    address_choices = [('', 'Select Address')] + address_choices
    location_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control selectpciker',
                                   'data-live-search': 'true',
                                   'searchable': 'Search here...'}),
        choices=address_choices, label='Address')
    demand_field = forms.DecimalField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control',
                                        'placeholder': 'Enter demand'}))

    # def __init__(self, *args, **kwargs):
    #     super(LocationForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.layout = Layout(
    #         Row(
    #             Column('location_field', css_class='form-group col-md-6 mb-2'),
    #             Column('demand_field', css_class='form-group col-md-6 mb-0'),
    #             css_class='form-row'
    #         ),
    #     )


class BaseLocationFormSet(BaseFormSet):
    pass


class BuildRouteForm(forms.Form):
    address_choices = get_addresses()
    departure_choices = [('', 'Select Starting Location')]
    departure_choices.extend(address_choices)
    departure_field = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=departure_choices, label="Departure")

    vehicle_capacity_field = forms.DecimalField(
        label="Vehicle Capacity",
        widget=forms.NumberInput(attrs={'class': 'form-control',
                                        'placeholder': 'Enter Vehicle Capacity'}),
        min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_id = 'id-buildRouteForm'
        self.helper.form_method = 'post'
        # self.helper.form_class = 'blueForms'
        # self.helper.form_action = 'new_route'  # 'routing_request'
        # self.helper.add_input(Submit('Create Routes', 'Submit'))
        self.helper.layout = Layout(
            Row(
                Column('departure_field', css_class='form-group col-md-6 mb-0'),
                Column('vehicle_capacity_field', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
        )
