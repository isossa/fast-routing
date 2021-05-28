from django.db import models
from django.urls import reverse

from .base.common import Role


class Address(models.Model):
    """This class provides the mechanism for working building stand U.S. addresses.

    It provides methods for geocoding standard U.S. addresses. Standard U.S. addresses
    are defined to have the following formats:

        street, state, country, zipcode.

    Attributes:
    """

    street = models.CharField(max_length=200, help_text="Street address")
    city = models.CharField(max_length=200, help_text="City")
    state = models.CharField(max_length=200, help_text="State")
    country = models.CharField(max_length=200, help_text="Country", default="United States")
    zipcode = models.CharField(max_length=5)

    latitude = models.CharField(max_length=200, editable=False, default="")
    longitude = models.CharField(max_length=200, editable=False, default="")
    coordinates = models.CharField(max_length=200, editable=False, default="")
    info = models.TextField(default="", editable=False)

    created_on = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def get_absolute_url(self):
        return reverse('address-detail', args=[str(self.id)])

    def __str__(self) -> str:
        """Retrieves a string representation of this address.

        Returns:
            String representing this address. The string is formatted as follows:
            "STREET, CITY, STATE, COUNTRY, ZIPCODE"
        """
        return f'{self.street}, {self.city}, {self.state}, {self.country}, {self.zipcode}'

    def __eq__(self, other):
        return (
                self.__class__ == other.__class__ and self.street == other.street and self.city == other.city
                and self.state == other.state and self.country == other.country and self.zipcode == other.zipcode
        )

    def __hash__(self):
        return hash(self.coordinates)


class Language(models.Model):
    language = models.CharField(max_length=20, help_text='Select a language')

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return f'{self.language}'

    def get_absolute_url(self):
        return reverse('language-detail', args=[str(self.id)])


class Location(models.Model):
    address = models.OneToOneField(Address, on_delete=models.PROTECT)
    demand = models.PositiveIntegerField(default=0)
    assigned = models.BooleanField(editable=False, null=True, default=False)
    route = models.ForeignKey('Route', on_delete=models.PROTECT, editable=False, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    language = models.ManyToManyField(Language, help_text='Select a language')

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f'{self.address}; {self.demand}'

    def get_absolute_url(self):
        return reverse('location-detail', args=[str(self.id)])


class Route(models.Model):
    demand = models.PositiveIntegerField(default=0, editable=False)
    distance = models.PositiveIntegerField(default=0, editable=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    assigned_to = models.ForeignKey('Driver', on_delete=models.PROTECT, null=True, editable=False)

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        return f'{self.address}; {self.demand}; {self.assigned_to}'

    def get_absolute_url(self):
        return reverse('route-detail', args=[str(self.id)])


class Driver(models.Model):
    ROLE = (
        (Role.PERMANENT.name, Role.PERMANENT.value),
        (Role.VOLUNTEER.name, Role.VOLUNTEER.value),
        (Role.NONE.name, Role.NONE.value)
    )
    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    role = models.CharField(max_length=20, choices=ROLE, default="None")
    created_on = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    availability_score = models.PositiveIntegerField(editable=False, default=0)
    language = models.ManyToManyField(Language, help_text='Select a language')

    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.role}'

    def get_absolute_url(self):
        return reverse('driver-detail', args=[str(self.id)])
