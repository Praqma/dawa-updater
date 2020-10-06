#!/usr/bin/env python

"""DAWA updater

Handle the missing addresses that don't have a sognenr.
"""
import csv
from typing import Dict

from models import SamHouseunits


class Updater:
    def __init__(self):
        # a mapping for adgangsadresse_uuid -> sogne kode
        self.parish_uuid_map = {}  # type: Dict[str, str]
        # a mapping between kode -> navn
        self.parish_name_map = {}  # type: Dict[str, str]

    def update_houses(self):
        houses = SamHouseunits.filter(SamHouseunits.sognenr == '9999')
        for house in houses:  # type: SamHouseunits
            try:
                sognenr = self.parish_uuid_map[house.adgangsadresse_uuid]
                house.sognenr = sognenr
                house.sognenavn = self.parish_name_map[self.parish_uuid_map[house.adgangsadresse_uuid]]
                house.save()
            except KeyError:
                pass

    def read_parish_uuid_data(self):
        with open('dawadata/parish_address_data.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.parish_uuid_map[row["adgangsadresseid"]] = row["sognekode"]

    def read_parish_names(self):
        with open('dawadata/parish_data.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                self.parish_name_map[row["kode"]] = row["navn"]


if __name__ == '__main__':
    updater = Updater()
    updater.read_parish_uuid_data()
    updater.read_parish_names()
    updater.update_houses()
