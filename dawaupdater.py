#!/usr/bin/python
# -*- coding: utf-8 -*-

"""DAWA updater

Usage:
  dawaupdater.py freshimport
  dawaupdater.py update
  dawaupdater.py list-obsolete-parish
  dawaupdater.py import-new-parish
  dawaupdater.py list-new-parish

Options:
  -h --help             Show this screen.
  update-parish         Update database with the new parishes
  list-obsolete-parish  List obsolete parish
  list-new-parish       List new parish 
  freshimport           Used to establish a fresh local copy of the data
  update                Is used for updating the data
"""

from docopt import docopt

import json
import concurrent.futures
import csv
from pprint import pprint

from models import *
import os
import peewee
import re
import requests
import pyproj
from services.VejstykkerService import VejstykkerService
from services.AddressService import AddressService
import config
import shutil
import tempdata
import pymysql.err

wgs84 = pyproj.Proj(init='epsg:4326')
etrs89 = pyproj.Proj(init='epsg:25832')

vejstykker_service = None
address_service = None

SERVER_URL = 'http://dawa.aws.dk/'


def import_commune_information():
    print('importing commune information...')

    def get_communes():
        response = requests.get(SERVER_URL + 'kommuner')
        data = response.json()

        for e in data:
            yield {'id': e['kode'], 'name': e['navn']}

    SamKommune.insert_many(get_communes()).execute()

    print('done.')

#Updates parishes. Takes an Array of parishes in the form SOGNXXXX where XXXX is the parish code
def update_parishes(dawa_parish_json, parishes = []):
    print("Updating parishes with new parish data")
    parishmap = {}
    updatelist = []

    for i in range(0, len(dawa_parish_json)):
        parishmap[int(dawa_parish_json[i]['kode'])] = dawa_parish_json[i]


    for parish in parishes:        
        pString = int(parish[4:8])
        url = SERVER_URL + 'adgangsadresser'
        parameters = {'sognekode': pString, 'side': 1, 'per_side': 1}
        response = requests.get(url, params=parameters)
        if response.json():
            kommune_id = response.json()[0]['kommune']['kode']

        new_parish = {
            'areacode': pString, 
            'areaname': parishmap[pString]['navn'],
            'areatypeid': 'SOGN',
            'kommuneid': int(kommune_id),
            'areaid': "{0}{1}".format('SOGN', pString)
        }
        print("Added %s" % new_parish)
        updatelist.append(new_parish)

    with database.atomic():
        SamArea.insert_many(updatelist).execute()

def get_parishes():
    response = requests.get(SERVER_URL + 'sogne')
    data = response.json()

    for e in data:
        url = SERVER_URL + 'adgangsadresser'
        parameters = {'sognekode': e['kode'], 'side': 1, 'per_side': 1}
        response = requests.get(url, params=parameters)
        if response.json():
            kommune_id = response.json()[0]['kommune']['kode']

        yield {
        'areacode': int(e['kode']), 
        'areaname': e['navn'],
        'areatypeid': 'SOGN', 
        'kommuneid': int(kommune_id),
        'areaid': "{0}{1}".format('SOGN', int(e['kode']))
        }

    print('done importing parishes')


#Calculates the parishes in that are on the webservice but NOT in the database. 
#This is new parishes we can safely insert
def get_new_parish_from_dawa(dawa_parish_json = []):
    print("Finding new parishes")
    added = []
    for e in dawa_parish_json:
        if e['kode']:
            try:
                found = SamArea.get(SamArea.areaid == 'SOGN'+e['kode'])
            except DoesNotExist as dne:
                print("WARNING: Found new area not imported %s" % ("SOGN"+e['kode']))
                added.append('SOGN'+e['kode'])
    return added

#Calculates the parises in that are in the database but not on the dawa api
#These need to be individually evaluted. We can basically just print them to console
def get_obsolete_parish():
    print("Finding obsolete parishes")
    renamed = []
    response = requests.get(SERVER_URL + 'sogne')
    data = response.json()
    database_rows = SamArea.select().where(SamArea.areaid.contains("SOGN")).execute()
    for dbr in database_rows:
        found  = False
        for dawadata in data:        
            if(dawadata['kode'] in dbr.areaid):
                found = True                
                break
        if not found:
            print("WARNING: Found obsolete area %s - %s" % (dbr.areaid,dbr.areaname))                
            renamed.append(dbr.areaid)
    return renamed


def import_area_information():
    print('importing area information...')

    def get_communes():
        response = requests.get(SERVER_URL + 'kommuner')
        data = response.json()

        for e in data:
            yield {'areacode': int(e['kode']), 'areaname': e['navn'],
                   'areatypeid': 'KOM', 'kommuneid': int(e['kode']),
                   'areaid': "{0}{1}".format('KOM', int(e['kode']))}

        print('done importing communes')

    def get_postal_districts():
        response = requests.get(SERVER_URL + 'postnumre')
        data = response.json()

        postnr_kommunekode_map = {}
        for e in data:
            if len(e['kommuner']) == 0:
                continue
            postnr_kommunekode_map[e['nr']] = int(e['kommuner'][0]['kode'])

        response = requests.get(SERVER_URL + 'replikering/postnumre')
        data = response.json()

        for e in data:
            if e['stormodtager']:
                continue

            yield {'areacode': int(e['nr']), 'areaname': e['navn'],
                   'areatypeid': 'POST', 'kommuneid': postnr_kommunekode_map[e['nr']],
                   'areaid': "{0}{1}".format('POST', int(e['nr']))}

        print('done importing postal districts')


    def get_electoral_districts():
        response = requests.get(SERVER_URL + 'opstillingskredse')
        data = response.json()

        for e in data:
            yield {'areacode': int(e['kode']), 'areaname': e['navn'],
                   'areatypeid': 'VALG', 'kommuneid': 9999,
                   'areaid': "{0}{1}".format('VALG', int(e['kode']))}

        print('done importing electoral districts')

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(SamArea.insert_many(get_communes()).execute())
        executor.submit(SamArea.insert_many(get_postal_districts()).execute())
        executor.submit(SamArea.insert_many(get_parishes()).execute())
        executor.submit(SamArea.insert_many(get_electoral_districts()).execute())


def create_houseunit(data):
    houseunit = {}

    houseunit['adgangsadresse_uuid'] = data['id']
    houseunit['kommuneid'] = data['kommunekode']

    houseunit['roadid'] = data['vejkode']
    houseunit['roadname'] = vejstykker_service.get_road_name_from_road_id_and_commune_id(data['vejkode'], data['kommunekode'])

    house_id = data['husnr']
    houseunit['houseid'] = house_id

    house_number = re.findall(r'\d+', house_id)[0]
    if int(house_number) % 2 == 0:
        houseunit['equalno'] = 1
    else:
        houseunit['equalno'] = 0

    x = data['etrs89koordinat_øst']
    y = data['etrs89koordinat_nord']

    wgs84_coordinates = pyproj.transform(etrs89, wgs84, x, y)
    houseunit['x'] = wgs84_coordinates[0]
    houseunit['y'] = wgs84_coordinates[1]

    houseunit['doorcount'] = address_service.get_door_count_from_adgangsadresseid(data['id'])
    houseunit['zip'] = data['postnr']

    parish = address_service.get_parish_from_adgangsadresseid(data['id'])
    houseunit['sognenr'] = parish['kode']
    houseunit['sognenavn'] = parish['navn']

    valgkredskode = address_service.get_political_district_id_from_adgangsadresseid(data['id'])
    houseunit['valgkreds'] = valgkredskode

    return houseunit


def freshimport():
    print('importing address info')

    with open(config.ADDRESS_ACCESS_DATA, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        next(reader)  # skip header

        for index, row in enumerate(reader):
            if index % 50000 == 0:
                print('records read: {0}'.format(index))

            valid_address = True

            address = {'id': row[0], 'kommunekode': row[2], 'vejkode': row[3], 'husnr': row[4], 'postnr': row[6],
                       'etrs89koordinat_øst': row[13], 'etrs89koordinat_nord': row[14]}

            for v in address.values():
                if not v:
                    valid_address = False
                    break

            if valid_address:
                houseunit = create_houseunit(address)
                SamHouseunits.create(**houseunit)

    print('done importing address info')


def update_address_information():
    print('updating address info')

    def handle_insert_event(event):
        print('inserting new record {0}'.format(event['data']['id']))

        data = event['data']
        houseunit = create_houseunit(data)

        try:
            SamHouseunits.create(**houseunit)
        except IntegrityError:
            return

    def handle_update_event(event):
        print('updating record {0}'.format(event['data']['id']))

        data = event['data']
        houseunit = create_houseunit(data)

        try:
            record = SamHouseunits.get(SamHouseunits.adgangsadresse_uuid == houseunit['adgangsadresse_uuid'])
            record.delete_instance()
        except DoesNotExist:
            print('record is not found for updates so it will be created')
        except peewee.IntegrityError:
            print("peewee integrity error")
            return
        except pymysql.err.IntegrityError:
            print("pymysql integrity error")
            return
        finally:
            try:
                SamHouseunits.create(**houseunit)
            except peewee.IntegrityError:
                print("peewee integrity error")
                return
            except pymysql.err.IntegrityError:
                print("pymysql integrity error")
                return

    def handle_delete_event(event):
        print('deleting record {0}'.format(event['data']['id']))

        try:
            record = SamHouseunits.get(SamHouseunits.adgangsadresse_uuid == event['data']['id'])
            record.delete_instance()
        except DoesNotExist:
            return

    with open(config.ADDRESS_ACCESS_DATA_UPDATES, encoding='utf-8') as jsonfile:
        address_updates = json.loads(jsonfile.read())

        for event in address_updates:
            print('event number: {0}'.format(event['sekvensnummer']))

            valid = True

            needed_keys = ['id', 'kommunekode', 'vejkode', 'husnr', 'postnr', 'etrs89koordinat_øst',
                           'etrs89koordinat_nord']
            data = {key: event['data'][key] for key in event['data'] if key in needed_keys}

            for v in data.values():
                if v is None:
                    valid = False

            if not valid:
                print('skipped record {0}'.format(data['id']))
                continue

            event_switcher = {
                'insert': handle_insert_event,
                'update': handle_update_event,
                'delete': handle_delete_event
            }

            event_handler = event_switcher.get(event['operation'])
            event_handler(event)

    print('done updating')


def initialize(is_update):
    def get_current_update():
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
        update = get_current_update()
        tempdata.append_or_save({'update_to_register': update})

        sekvensnummertil = update['sekvensnummer']

        update = Updates.select().order_by(Updates.tidspunkt.desc()).limit(1).get()
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
        update = get_current_update()

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
    pprint(data_files)

    download_data_files(data_files)

    print('done.')

    print('starting services...')
    global vejstykker_service
    vejstykker_service = VejstykkerService()

    global address_service
    address_service = AddressService()
    print('done')


def register_update():
    print('registering an update...')

    tdata = tempdata.load()
    update = tdata['update_to_register']
    update.pop('tidspunkt') # The database will set `tidspunkt` to CURRENT_TIMESTAMP on edit
    print(update)

    Updates.create(**update)

    print('done')


def updates_available():
    print('checking for updates...')

    response = requests.get('{0}replikering/senestesekvensnummer'.format(SERVER_URL))
    update = response.json()

    sekvensnummertil = update['sekvensnummer']

    update = Updates.select().order_by(Updates.tidspunkt.desc()).limit(1).get()
    sekvensnummerfra = int(update.sekvensnummer)

    print('sekvensnummerfra: {0}; sekvensnummertil: {1}'.format(sekvensnummerfra, sekvensnummertil))

    output = True

    if sekvensnummerfra == sekvensnummertil:
        print('no updates found')
        output = False
    else:
        print('found {0} update events'.format(sekvensnummertil - sekvensnummerfra))

    return output


def main(arguments):

    is_obsolete_parish = arguments['list-obsolete-parish']
    is_list_new_parish = arguments['list-new-parish']
    is_import_new_parish = arguments['import-new-parish']
    is_update = arguments['update']
    is_freshimport = arguments['freshimport']

    if is_obsolete_parish:
        get_obsolete_parish()            

    if is_list_new_parish:
        #Get full list of parish from 
        response = requests.get(SERVER_URL + 'sogne')
        data = response.json()          
        get_new_parish_from_dawa(data)

    if is_import_new_parish:      
        parish_updates = get_new_parish_from_dawa(data)
        update_parishes(data, parish_updates)

    if is_update and updates_available():
        initialize(is_update)
        update_address_information()
        register_update()

    if is_freshimport:
        initialize(is_update)
        import_commune_information()
        import_area_information()
        freshimport()
        register_update()

    print('Done using updater')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
