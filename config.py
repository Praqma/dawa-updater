import sys
import os

if "DATABASE_HOST" in os.environ:
    DATABASE_HOST = os.environ['DATABASE_HOST']
else:
    print('environment variable [DATABASE_HOST] not found')
    sys.exit(1)

if "DATABASE_NAME" in os.environ:
    DATABASE_NAME = os.environ['DATABASE_NAME']
else:
    print('environment variable [DATABASE_NAME] not found')
    sys.exit(1)

if "DATABASE_USER" in os.environ:
    DATABASE_USER = os.environ['DATABASE_USER']
else:
    print('environment variable [DATABASE_USER] not found')
    sys.exit(1)

if "DATABASE_PASSWORD" in os.environ:
    DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']    
else:
    print('environment variable [DATABASE_PASSWORD] not found')
    sys.exit(1)

TEMP_DATA_FILE = 'tempdata.json'

DATA_FILE_FOLDER = 'dawadata'

STREET_DATA = '{0}/street_data.csv'.format(DATA_FILE_FOLDER)
ADDRESS_ACCESS_DATA = '{0}/address_access_data.csv'.format(DATA_FILE_FOLDER)
ADDRESS_DATA = '{0}/address_data.csv'.format(DATA_FILE_FOLDER)
PARISH_ADDRESS_DATA = '{0}/parish_address_data.csv'.format(DATA_FILE_FOLDER)
PARISH_DATA = '{0}/parish_data.csv'.format(DATA_FILE_FOLDER)
POLITICAL_ADDRESS_DATA = '{0}/political_address_data.csv'.format(DATA_FILE_FOLDER)

ADDRESS_ACCESS_DATA_UPDATES = '{0}/address_access_data_updates.json'.format(DATA_FILE_FOLDER)
