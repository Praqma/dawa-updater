import csv
import logging
from collections import Counter

import config

log = logging.getLogger("dawa")


class AddressService:
    def __init__(self):
        self._ADDRESS_DATA = []
        with open(config.ADDRESS_DATA) as address_data:
            reader = csv.reader(address_data)  # type: List
            next(reader)  # skip header

            # adgangsaddressid
            doors = []  # type: List[str]
            for row in reader:  # type: List[str]
                try:
                    doors.append(row[5])
                except IndexError:
                    doors.append('')

            self._ADDRESS_DATA = Counter(doors)

        self._PARISH_DATA = {}
        parish_id_name_map = {}

        # UUID for sogne skal med
        with open(config.PARISH_ADDRESS_DATA, encoding='utf-8') as parish_address, open(
                config.PARISH_DATA, encoding='utf-8') as parish:
            # csv format
            # dagi_id,kode,navn,ændret,geo_ændret,geo_version,bbox_xmin,bbox_ymin,bbox_xmax,bbox_ymax,visueltcenter_x,visueltcenter_y
            reader = csv.reader(parish)
            next(reader)  # skip header

            for row in reader:
                parish_id_name_map[row[1]] = row[2]

            # csv format
            # adgangsadresseid (uuid),sognekode
            reader = csv.reader(parish_address)
            next(reader)  # skip header

            for row in reader:
                try:
                    # row[0] = uuid
                    self._PARISH_DATA[row[1]] = {'kode': row[1], 'navn': parish_id_name_map[row[1]]}
                except KeyError:
                    log.warning(f"Sogn {row[1]} does not exist")

        # THIS DOES NOT CHANGE, SO COMMENTED OUT ...
        # MISSING DATA: VALGKREDSNAVN

        # self._POLITICAL_DATA = {}
        # with open(config.POLITICAL_ADDRESS_DATA) as political_address:
        #     reader = csv.reader(political_address)
        #     next(reader)  # skip header
        #
        #     # csv format
        #     # adgangsadresseid (uuid),opstillingskredskode
        #     for row in reader:
        #         try:
        #             self._POLITICAL_DATA[row[0]] = row[1]
        #             log.info(f"Now updating political {row[1]} and {parish_id_name_map[row[1]]}")
        #         except KeyError:
        #             log.warning(f"Valgkreds {row[1]} was problematic")

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
