from geo.Address import Address
from driver.Driver import Driver


class Location:
    def __init__(self, address: Address, demand: int, served_by: Driver, identifier: str):
        self._address: Address = address
        self._demand: int = demand
        self._served_by: Driver = served_by
        self._identifier = identifier

    @property
    def address(self):
        return self._address

    @property
    def demand(self):
        return self._demand

    @property
    def served_by(self):
        return self._served_by

    @property
    def identifier(self):
        return self._identifier

    def __str__(self):
        info = f'Address: {self._address}\n' \
               f'Demand: {self._demand}\n' \
               f'Served By: \n\n{self._served_by}'
        return info
