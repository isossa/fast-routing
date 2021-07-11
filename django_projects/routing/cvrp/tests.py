# from django.test import TestCase
#
# from django_projects.routing.cvrp.base.common import Role
# from django_projects.routing.cvrp.forms import DriverForm
# from django_projects.routing.cvrp.models import Driver
#
#
# class RouteSubmissionForm(TestCase):
#     def setUp(self) -> None:
#         Driver.objects.create(first_name='Joe', last_name='Doe', role=Role.PERMANENT.value)
#
#     def driver_data(self, first_name, last_name, role):
#         return DriverForm(data={'driver_field': first_name + ' ' + last_name + ' ' + role})
#
#     def test_valid_data(self):
#         form = self.driver_data('Joe', 'Doe', 'Permanent')
#         self.assertTrue(form.is_valid())
