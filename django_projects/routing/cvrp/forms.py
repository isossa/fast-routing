import os.path

from django import forms

from .models import Address, Driver


class BuildRouteForm(forms.Form):

    # def init(self, args, **kwargs):
    #     super(BuildRouteForm, self).init(args, **kwargs)
    #     # self.helper = FormHelper()
    #     # self.helper.form_method = 'post'
    #     self.helper.layout = Layout(
    #         Row(
    #             Column('dhcp_member', css_class='form-group col-md-6 mb-0'),
    #             Column('router', css_class='form-group col-md-6 mb-0'),
    #             css_class='form-row'
    #         )

    address_choices = list()
    addresses = Address.objects.all().order_by('country', 'state', 'city',  'zipcode', 'street')
    print(len(addresses))

    for address in addresses:
        address_choices.append((address.__str__(), address.__str__()))

    departure_field = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                                        choices=address_choices, label="Departure")

    drivers = Driver.objects.all().order_by('first_name', 'last_name')

    driver_choices = list()
    for driver in drivers:
        driver_choices.append((driver.__str__(), driver.__str__()))

    drivers_field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
                                              choices=driver_choices, label="Drivers")

    vehicle_capacity = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                          min_value=1)

    BASE_DIR = os.environ['USERPROFILE']
    # path_documents = os.path.join(BASE_DIR, 'Documents')
    # drivers_availability = forms.FilePathField(path=path_documents)
    # locations = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
    #                                       choices=address_choices)
    demand = forms.DecimalField(required=False,
                                min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))



# class DriverForm(forms.Form):
#     drivers = Driver.objects.all().order_by('first_name', 'last_name')
#
#     driver_choices = list()
#     for driver in drivers:
#         driver_choices.append((driver.__str__(), driver.__str__()))
#
#     # drivers_field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
#     #                                           choices=driver_choices, label="Drivers")
