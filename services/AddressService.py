import csv
from collections import Counter
import config

class AddressService:
    def __init__(self):
        self._ADDRESS_DATA = []
        with open(config.ADDRESS_DATA) as address_data:
            reader = csv.reader(address_data)
            next(reader)  # skip header

            doors = []
            for row in reader:
                doors.append(row[7])

            self._ADDRESS_DATA = Counter(doors)

        self._PARISH_DATA = {}
        with open(config.PARISH_ADDRESS_DATA, encoding='utf-8') as parish_address, open(
                config.PARISH_DATA, encoding='utf-8') as parish:
            reader = csv.reader(parish)
            next(reader)  # skip header

            parish_id_name_map = {}
            for row in reader:
                parish_id_name_map[row[1]] = row[2]

            reader = csv.reader(parish_address)
            next(reader)  # skip header

            for row in reader:
                self._PARISH_DATA[row[0]] = {'kode': row[1], 'navn': parish_id_name_map[row[1]]}

        self._POLITICAL_DATA = {}
        with open(config.POLITICAL_ADDRESS_DATA) as political_address:
            reader = csv.reader(political_address)
            next(reader)  # skip header

            for row in reader:
                self._POLITICAL_DATA[row[0]] = row[1]

    def get_parish_from_adgangsadresseid(self, adgangsadresseid):
        if adgangsadresseid in self._PARISH_DATA:
            return self._PARISH_DATA[adgangsadresseid]
        else:
            return {'kode': 9999, 'navn': 'Ukendt (Sogn) Sogn'}

    def get_political_district_id_from_adgangsadresseid(self, adgangsadresseid):
        if adgangsadresseid in self._POLITICAL_DATA:
            return self._POLITICAL_DATA[adgangsadresseid]
        else:
            return 9999

    def get_door_count_from_adgangsadresseid(self, adgangsadresseid):
        if adgangsadresseid in self._ADDRESS_DATA:
            return self._ADDRESS_DATA[adgangsadresseid]
        else:
            return 1
