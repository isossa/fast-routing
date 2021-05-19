from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('drivers/', views.DriverListView.as_view(), name='drivers'),
    path('driver/<int:pk>', views.DriverListView.as_view(), name='driver-detail'),
    path('addresses/', views.AddressListView.as_view(), name='addresses'),
    path('addresses/<int:pk>', views.AddressListView.as_view(), name='address-detail'),
]