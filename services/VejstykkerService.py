import csv
import config

class VejstykkerService:
    def __init__(self):
        self._STREET_DATA = []

        with open(config.STREET_DATA, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header

            for row in reader:
                self._STREET_DATA.append({'kode': row[0],
                                         'kommunekode': row[1],
                                         'navn': row[2],
                                         'adresseringsnavn': row[3]})

    def get_road_name_from_road_id_and_commune_id(self, road_id, commune_id):
        for street in self._STREET_DATA:
            if street['kode'] == road_id and street['kommunekode'] == commune_id:
                return street['navn']

        return 'none'
