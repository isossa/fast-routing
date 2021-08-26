from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_routes, name='create_routes'),
    path('routes/', views.route, name='route_home'),
    path('routes/create_routes/', views.create_routes, name='create_routes'),
    path('routes/new_route/', views.new_route, name='new_route'),
    path('settings/', views.settings, name='settings'),
    path('settings/load', views.settings_load, name='settings_load'),
    # path('drivers/', views.DriverListView.as_view(), name='drivers'),
    # path('driver/<int:pk>', views.DriverListView.as_view(), name='driver-detail'),
    # path('addresses/', views.AddressListView.as_view(), name='addresses'),
    # path('addresses/<int:pk>', views.AddressListView.as_view(), name='address-detail'),
    path('export/', views.export, name='export_home'),
]

websocket = path

