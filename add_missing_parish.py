#!/usr/bin/env python

"""DAWA updater

Handle the missing addresses that don't have a sognenr.
"""
import logging

import peewee
import requests

from models import SamArea

SERVER_URL = 'https://dawa.aws.dk/'

# Calculates the parishes in that are on the webservice but NOT in the database.
# This is new parishes we can safely insert
def get_new_parish_from_dawa():
    # Get full list of parish from
    response = requests.get(SERVER_URL + 'sogne')
    dawa_parish_json = response.json()

    logging.info("Finding new parishes")
    added = []
    for e in dawa_parish_json:
        if e['kode']:
            try:
                found = SamArea.get(SamArea.areaid == 'SOGN' + e['kode'])
                print(found)
            except peewee.DoesNotExist:
                print("Found new area not imported %s" % ("SOGN" + e['kode']))
                added.append('SOGN' + e['kode'])

    return added

#
# # Updates parishes. Takes an Array of parishes in the form SOGNXXXX where XXXX is the parish code
# def update_parishes(dawa_parish_json, parishes=None):
#     if parishes is None:
#         parishes = []
#     logging.info("Updating parishes with new parish data")
#     parishmap = {}
#     updatelist = []
#
#     for i in range(0, len(dawa_parish_json)):
#         parishmap[int(dawa_parish_json[i]['kode'])] = dawa_parish_json[i]
#
#     for parish in parishes:
#         pString = int(parish[4:8])
#         url = SERVER_URL + 'adgangsadresser'
#         parameters = {'sognekode': pString, 'side': 1, 'per_side': 1}
#         response = requests.get(url, params=parameters)
#         if response.json():
#             kommune_id = response.json()[0]['kommune']['kode']
#
#         new_parish = {
#             'areacode': pString,
#             'areaname': parishmap[pString]['navn'],
#             'areatypeid': 'SOGN',
#             'kommuneid': int(kommune_id),
#             'areaid': "{0}{1}".format('SOGN', pString)
#         }
#         logging.info("Added %s" % new_parish)
#         updatelist.append(new_parish)
#
#     with database.atomic():
#         for idx in range(0, len(updatelist), 100):
#             # Insert 100 rows at a time.
#             rows = updatelist[idx:idx + 100]
#             SamArea.insert_many(rows).execute()




if __name__ == '__main__':
    get_new_parish_from_dawa()
