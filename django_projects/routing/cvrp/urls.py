from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('routes/', views.route, name='route_home'),
    path('routes/new/', views.add_route, name='create_routes'),
    path('routes/new_route', views.new_route, name='new_route'),
    path('drivers/', views.DriverListView.as_view(), name='drivers'),
    path('driver/<int:pk>', views.DriverListView.as_view(), name='driver-detail'),
    path('addresses/', views.AddressListView.as_view(), name='addresses'),
    path('addresses/<int:pk>', views.AddressListView.as_view(), name='address-detail'),
    path('export/', views.export, name='export_home'),
]
