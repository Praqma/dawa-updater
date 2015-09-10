#!/usr/bin/python
# -*- coding: utf-8 -*-
"""DAWA updater

Usage:
  dawaupdater.py freshimport
  dawaupdater.py update

Options:
  -h --help     Show this screen.
  freshimport   used to establish a fresh local copy of the data
  update        is used for updating the data
"""
from models import *
from docopt import docopt
import logging.config
import os.path
import re
import requests
import concurrent.futures
import json
import csv
import pyproj
from queue import Queue
from services.VejstykkerService import VejstykkerService
from services.AddressService import AddressService

SERVER_URL = 'http://dawa.aws.dk/'

_LOGGING_CONFIG = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.config.fileConfig(_LOGGING_CONFIG)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def import_commune_information():
    def get_communes():
        response = requests.get(SERVER_URL + 'kommuner')
        data = response.json()

        for e in data:
            yield {'id': e['kode'], 'name': e['navn']}

    SamKommune.insert_many(get_communes()).execute()


def import_area_information():
    def get_communes():
        response = requests.get(SERVER_URL + 'kommuner')
        data = response.json()

        for e in data:
            yield {'areacode': int(e['kode']), 'areaname': e['navn'],
                   'areatypeid': 'KOM', 'kommuneid': int(e['kode']),
                   'areaid': "{0}{1}".format('KOM', int(e['kode']))}

    def get_postal_districts():
        response = requests.get(SERVER_URL + 'postnumre')
        data = response.json()

        postnr_kommunekode_map = {}
        for e in data:
            postnr_kommunekode_map[e['nr']] = int(e['kommuner'][0]['kode'])

        response = requests.get(SERVER_URL + 'replikering/postnumre')
        data = response.json()

        for e in data:
            if e['stormodtager']:
                continue

            yield {'areacode': int(e['nr']), 'areaname': e['navn'],
                   'areatypeid': 'POST', 'kommuneid': postnr_kommunekode_map[e['nr']],
                   'areaid': "{0}{1}".format('POST', int(e['nr']))}

    def get_parishes():
        response = requests.get(SERVER_URL + 'sogne')
        data = response.json()

        for e in data:
            url = SERVER_URL + 'adgangsadresser'
            parameters = {'sognekode': e['kode'], 'side': 1, 'per_side': 1}
            response = requests.get(url, params=parameters)
            if response.json():
                kommune_id = response.json()[0]['kommune']['kode']

            yield {'areacode': int(e['kode']), 'areaname': e['navn'],
                   'areatypeid': 'SOGN', 'kommuneid': int(kommune_id),
                   'areaid': "{0}{1}".format('SOGN', int(e['kode']))}

    def get_electoral_districts():
        response = requests.get(SERVER_URL + 'opstillingskredse')
        data = response.json()

        for e in data:
            yield {'areacode': int(e['kode']), 'areaname': e['navn'],
                   'areatypeid': 'VALG', 'kommuneid': 9999,
                   'areaid': "{0}{1}".format('VALG', int(e['kode']))}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(SamArea.insert_many(get_communes()).execute())
        executor.submit(SamArea.insert_many(get_postal_districts()).execute())
        executor.submit(SamArea.insert_many(get_parishes()).execute())
        executor.submit(SamArea.insert_many(get_electoral_districts()).execute())

def get_address_chunks_from_commune(commune, page_number, chunk_size):
    url = 'http://dawa.aws.dk/replikering/adgangsadresser'
    parameters = {'kommunekode': commune.id, 'side': page_number, 'per_side': chunk_size}
    headers = {'Accept-Encoding': 'gzip, deflate'}

    response = requests.get(url, params=parameters, headers=headers)

    return response.json()


def import_address_information():
    process_queue = Queue()
    writeQueue = Queue()
    vejstykker_service = VejstykkerService()
    address_service = AddressService()

    def read_address_data():
        CHUNK_SIZE = 20000
        with open('C:/projects/dawa-updater/sample_data/address_data.csv') as csvfile:
            output = []
            reader = csv.reader(csvfile)

            next(reader)  # skip header

            for index, row in enumerate(reader):
                if index % CHUNK_SIZE == 0:
                    process_queue.put(output)
                    output = []

                address = {}
                address['id'] = row[0]
                address['status'] = row[1]
                address['kommunekode'] = row[2]
                address['vejkode'] = row[3]
                address['husnr'] = row[4]
                address['supplerendebynavn'] = row[5]
                address['postnr'] = row[6]
                address['oprettet'] = row[7]
                address['ændret'] = row[8]
                address['ikrafttrædelsesdato'] = row[9]
                address['ejerlavkode'] = row[10]
                address['matrikelnr'] = row[11]
                address['esrejendomsnr'] = row[12]
                address['etrs89koordinat_øst'] = row[13]
                address['etrs89koordinat_nord'] = row[14]
                address['nøjagtighed'] = row[15]
                address['kilde'] = row[16]
                address['husnummerkilde'] = row[17]
                address['tekniskstandard'] = row[18]
                address['tekstretning'] = row[19]
                address['esdhreference'] = row[20]
                address['journalnummer'] = row[21]
                address['adressepunktændringsdato'] = row[22]

                output.append(address)

    def process_address_data(data):
        wgs84 = pyproj.Proj(init='epsg:4326')
        etrs89 = pyproj.Proj(init='epsg:25832')

        while True:
            addresses = process_queue.get()

            for address in addresses:
                houseunit = {}

            # x = DecimalField(db_column='X', null=True)
            # y = DecimalField(db_column='Y', null=True)

                # address['status'] = row[1]
                # address['supplerendebynavn'] = row[5]
                # address['oprettet'] = row[7]
                # address['ændret'] = row[8]
                # address['ikrafttrædelsesdato'] = row[9]
                # address['ejerlavkode'] = row[10]
                # address['matrikelnr'] = row[11]
                # address['esrejendomsnr'] = row[12]
                # address['etrs89koordinat_øst'] = row[13]
                # address['etrs89koordinat_nord'] = row[14]
                # address['nøjagtighed'] = row[15]
                # address['kilde'] = row[16]
                # address['husnummerkilde'] = row[17]
                # address['tekniskstandard'] = row[18]
                # address['tekstretning'] = row[19]
                # address['esdhreference'] = row[20]
                # address['journalnummer'] = row[21]
                # address['adressepunktændringsdato'] = row[22]

                houseunit['adgangsadresse_uuid'] = address['id']
                houseunit['kommuneid'] = address['kommunekode']

                houseunit['roadid'] = address['vejkode']
                houseunit.roadName = vejstykker_service.get_road_name_from_road_id_and_commune_id(address['vejkode'], address['kommunekode'])

                house_id = address['husnr']
                houseunit['houseid'] = house_id

                house_number = re.findall(r'\d+', house_id)[0]
                if int(house_number) % 2 == 0:
                    houseunit['equalno'] = 1
                else:
                    houseunit['equalno'] = 0

                x = address['etrs89koordinat_øst']
                y = address['etrs89koordinat_nord']
                wgs84_coordinates = pyproj.transform(etrs89, wgs84, x, y)

                c = accessAddress['adgangspunkt']['koordinater']
                if c:
                    houseunit.X, houseunit.Y = c[0], c[1]
                else:
                    houseunit.X, houseunit.Y = None, None


                houseunit['doorcount'] = 1
                houseunit['zip'] = address['postnr']

                parish = address_service.get_parish_from_address_id(address['id'])
                if parish:
                    houseunit['sognenr'] = parish['kode']
                    houseunit['sognenavn'] = parish['navn']
                else:
                    houseunit['sognenr'] = 9999
                    houseunit['sognenavn'] = 'Ukendt (Sogn) Sogn'

                valgkredskode = address_service.get_political_district_id_from_address_id(address['id'])
                if valgkredskode:
                    houseunit['valgkreds'] = valgkredskode
                else:
                    houseunit['valgkreds'] = 9999

    def write_houseunits_to_database():
        pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(read_address_data())
        # executor.submit(write_houseunits_to_database())

        # executor.submit(process_address_data())

    #     for future in concurrent.futures.as_completed(futures):
    #         print(future.result())
    #
    #         # are all threads done?
    #         # are the queues empty?

def main():

    x = 585153.17
    y = 6138676.75

    wgs84 = pyproj.Proj(init='epsg:4326')
    etrs89 = pyproj.Proj(init='epsg:25832')

    pyproj.transform(etrs89, wgs84, x, y)

if __name__ == '__main__':
    # arguments = docopt(__doc__)
    main()
