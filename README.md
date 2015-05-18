# dawa-updater
pulls address data from DAWA and pushes it to the RUT database

## how to regenerate the database models
The process is described here http://peewee.readthedocs.org/en/latest/peewee/playhouse.html#pwiz

The command I ran is this

## running the script
install python 3

install pip if it's not installed

install virtualenv using pip running $ pip install virtualenv

create a virtual environment

execute $ virtualenv dawa-updater

if you have multiple python interpreters installed $ virtualenv -p /usr/bin/python3.4 dawa-updater

now clone the the project from github into the environment

it should look like this after you are done

C:\projects\dawa-updater>ls
Include  Lib  README.md  Scripts  __pycache__  dawaupdater.py  models.py  pip-selfcheck.json  requirements.txt

use the environment by running

on linux
$ source bin/activate

windows
$ Scripts/activate

to stop using virtualenv run $ deactivate

after activating the virtualenv in the root of the project install the dependencies using pip

$ pip install -r requirements.txt

if you change the dependencies update the file with

$ pip freeze > requirements.txt

if the model has changed update it.

# notes

https://docs.python.org/3.4/library/concurrent.futures.html#threadpoolexecutor

http://dawa.aws.dk/replikering/adresser/haendelser?id=0a3f50b3-7253-32b8-e044-0003ba298018
http://dawa.aws.dk/adgangsadresser?id=0a3f5084-5dd8-32b8-e044-0003ba298018
http://dawa.aws.dk/replikering/adgangsadresser/haendelser?id=0a3f5084-5dd8-32b8-e044-0003ba298018
http://dawa.aws.dk/replikering/postnumre/haendelser
http://dawa.aws.dk/replikering/adresser/haendelser?sekvensnummerfra=15000&sekvensnummertil=20000
http://dawa.aws.dk/replikering/adgangsadresser/haendelser?sekvensnummerfra=15000&sekvensnummertil=20000
http://dawa.aws.dk/replikeringdok