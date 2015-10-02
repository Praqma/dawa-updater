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
from builtins import print
from models import *
from docopt import docopt
import logging.config
import os
import time
import re
import requests
import concurrent.futures
import threading
import csv
import pyproj
from queue import Queue
from services.VejstykkerService import VejstykkerService
from services.AddressService import AddressService
import config
import shutil
import pprint
import tempdata

SERVER_URL = 'http://dawa.aws.dk/'

_LOGGING_CONFIG = os.path.join(os.path.dirname(__file__), "logging.ini")
logging.config.fileConfig(_LOGGING_CONFIG)


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


def import_address_information():
    print('importing address info')
    CHUNK_SIZE = 20000

    process_queue = Queue()
    write_queue = Queue()

    print('starting services...')
    vejstykker_service = VejstykkerService()
    address_service = AddressService()
    print('done')

    def read_address_data():
        print('reading address data...')

        last_index = 0

        with open(config.ADDRESS_ACCESS_DATA, encoding='utf-8') as csvfile:
            output = []
            reader = csv.reader(csvfile)

            next(reader)  # skip header

            for index, row in enumerate(reader):
                valid_address = True

                last_index = index

                if index != 0 and index % CHUNK_SIZE == 0:
                    process_queue.put(output)
                    print('process queue: item added; size: {0}'.format(process_queue.qsize()))
                    output = []
                    while process_queue.qsize() >= 10:
                        print('Process queue full')
                        time.sleep(30)

                address = {'id': row[0], 'kommunekode': row[2], 'vejkode': row[3], 'husnr': row[4], 'postnr': row[6],
                           'etrs89koordinat_øst': row[13], 'etrs89koordinat_nord': row[14]}

                for v in address.values():
                    if not v:
                        valid_address = False
                        break

                if valid_address:
                    output.append(address)

        print('ending address reading. Last index {0}'.format(last_index))
        return 'reading address data done.'

    def process_address_data():
        print('processing address data block...')

        stop = False
        wgs84 = pyproj.Proj(init='epsg:4326')
        etrs89 = pyproj.Proj(init='epsg:25832')
        output = []

        while not stop:
            addresses = process_queue.get()

            for index, address in enumerate(addresses):
                if index != 0 and (index+1) % CHUNK_SIZE == 0:
                    write_queue.put(output)
                    output = []

                    print('write queue: item added; size: {0}'.format(write_queue.qsize()))

                    while write_queue.qsize() >= 10:
                        print('Write queue full')
                        time.sleep(30)

                houseunit = {}

                houseunit['adgangsadresse_uuid'] = address['id']
                houseunit['kommuneid'] = address['kommunekode']

                houseunit['roadid'] = address['vejkode']
                houseunit['roadname'] = vejstykker_service.get_road_name_from_road_id_and_commune_id(address['vejkode'],
                                                                                                     address[
                                                                                                         'kommunekode'])

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
                houseunit['x'] = wgs84_coordinates[0]
                houseunit['y'] = wgs84_coordinates[1]

                houseunit['doorcount'] = address_service.get_door_count_from_adgangsadresseid(address['id'])
                houseunit['zip'] = address['postnr']

                parish = address_service.get_parish_from_adgangsadresseid(address['id'])
                houseunit['sognenr'] = parish['kode']
                houseunit['sognenavn'] = parish['navn']

                valgkredskode = address_service.get_political_district_id_from_adgangsadresseid(address['id'])
                houseunit['valgkreds'] = valgkredskode

                output.append(houseunit)

            print('processing address data, queue size {0}'.format(process_queue.qsize()))
            if process_queue.qsize() == 0:
                print('process queue empty processor shutting off')
                stop = True

        return 'processing address data block done.'

    def write_houseunits_to_database():
        print('writing houseunits to database...')

        stop = False
        records_written = 0

        while not stop:
            houseunits = write_queue.get()

            for houseunit in houseunits:
                SamHouseunits.create(**houseunit)

                records_written += 1

                if records_written % 10000 == 0:
                    print('{0} records written'.format(records_written))

            print('writing address data, queue size {0}'.format(write_queue.qsize()))
            if write_queue.empty():
                print('write queue empty writer shutting off')
                stop = True

        return 'writing houseunits to database done.'

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        f = executor.submit(read_address_data)
        time.sleep(5)

        futures = [
            f,

            executor.submit(process_address_data),
            executor.submit(process_address_data),
            executor.submit(write_houseunits_to_database),
            executor.submit(write_houseunits_to_database),
            executor.submit(write_houseunits_to_database)
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                print(future.result())
            except Exception as e:
                template = 'exception of type {0} occurred. \narguments:\n{1} \nmessage: {2}'
                message = template.format(type(e).__name__, e.args, e)
                print(message)


def initialize(is_update):
    def get_current_sequence_number():
        response = requests.get('http://dawa.aws.dk/replikering/senestesekvensnummer')
        return response.json()

    def download_data_files(data_files):
        def download_file(file):
            with open(file['filename'], 'wb') as handle:
                headers = {'Accept-Encoding': 'gzip, deflate'}
                response = requests.get(file['url'], headers=headers, stream=True)

                if not response.ok:
                    print('file: "{0}"; url: {1}\n {2}'.format(file['filename'], file['url'], response.reason))

                for block in response.iter_content(1024):
                    handle.write(block)

            return "file [{0}] has finished downloading".format(file['filename'])

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(data_files)) as executor:
            futures = []
            for df in data_files:
                futures.append(executor.submit(download_file, df))

            for future in concurrent.futures.as_completed(futures):
                try:
                    print(future.result())
                except Exception as e:
                    template = 'exception of type {0} occurred. \narguments:\n{1} \nmessage: {2}'
                    message = template.format(type(e).__name__, e.args, e)
                    print(message)

    def prepare_update_data_files():
        update = get_current_sequence_number()
        tempdata.append_or_save({'update_to_register': update})

        sekvensnummertil = update['sekvensnummer']

        update = Updates.select().order_by(Updates.tidspunkt.desc()).limit(1).excecute()
        sekvensnummerfra = update.sekvensnummer

        return [
            {'filename': config.STREET_DATA,
             'url': 'http://dawa.aws.dk/replikering/vejstykker?sekvensnummer={0}&format=csv'.format(sekvensnummertil)},

            {'filename': config.ADDRESS_ACCESS_DATA_UPDATES,
             'url': 'http://dawa.aws.dk/replikering/adgangsadresser/haendelser?sekvensnummerfra={0}&sekvensnummertil={1}'.format(
                 sekvensnummerfra, sekvensnummertil)},

            {'filename': config.ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/adresser?sekvensnummer={0}&format=csv'.format(sekvensnummertil)},

            {'filename': config.PARISH_ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/sognetilknytninger?sekvensnummer={0}&format=csv'.format(
                 sekvensnummertil)},

            {'filename': config.PARISH_DATA, 'url': 'http://dawa.aws.dk/sogne?format=csv'},

            {'filename': config.POLITICAL_ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/opstillingskredstilknytninger?sekvensnummer={0}&format=csv'.format(
                 sekvensnummertil)}
        ]

    def prepare_data_files_for_initial_import():
        update = get_current_sequence_number()
        # update['sekvensnummer'] = 1420000
        tempdata.append_or_save({'update_to_register': update})

        sekvensnummer = update['sekvensnummer']

        return [
            {'filename': config.STREET_DATA,
             'url': 'http://dawa.aws.dk/replikering/vejstykker?sekvensnummer={0}&format=csv'.format(sekvensnummer)},

            {'filename': config.ADDRESS_ACCESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/adgangsadresser?sekvensnummer={0}&format=csv'.format(
                 sekvensnummer)},

            {'filename': config.ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/adresser?sekvensnummer={0}&format=csv'.format(sekvensnummer)},

            {'filename': config.PARISH_ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/sognetilknytninger?sekvensnummer={0}&format=csv'.format(
                 sekvensnummer)},

            {'filename': config.PARISH_DATA, 'url': 'http://dawa.aws.dk/sogne?format=csv'},

            {'filename': config.POLITICAL_ADDRESS_DATA,
             'url': 'http://dawa.aws.dk/replikering/opstillingskredstilknytninger?sekvensnummer={0}&format=csv'.format(
                 sekvensnummer)}
        ]

    try:
        os.remove(config.TEMP_DATA_FILE)
    except OSError:
        pass

    shutil.rmtree(config.DATA_FILE_FOLDER, ignore_errors=True)
    os.makedirs(config.DATA_FILE_FOLDER)

    if is_update:
        print('preparing for an update')
        data_files = prepare_update_data_files()
    else:
        print('preparing for an initial import')
        data_files = prepare_data_files_for_initial_import()

    print('downloading data files...')
    pprint.pprint(data_files)

    download_data_files(data_files)

    print('done.')

def register_update():
    print('registering an update...')

    tdata = tempdata.load()
    update = tdata['update_to_register']
    print(update)

    Updates.create(**update)

    print('done')


def main():
    initialize(is_update=False)

    # import_commune_information()
    # import_area_information()

    import_address_information()
    register_update()

    print('donedone')

# database.close()

if __name__ == '__main__':
    # arguments = docopt(__doc__)
    main()
