---
maintainer: MadsNielsen
---

## dawa-updater

pulls address data from DAWA and pushes it to the RUT database

### Setting up the environment

1. start by installing Python 3. On Linux using apt-get and for windows download an installer from their website. It has to version 3 otherwise the application wont run. Add it to the PATH.

2. Install PIP. `https://pip.readthedocs.org/en/stable/installing/`

3. Using PIP install `virtualenv` instructions here `https://virtualenv.readthedocs.org/en/latest/installation.html`.

4. Set up a virtual environment for the project. To create ab virtualenv run `$ virtualenv dawa-updater`. If there multiple versions of python installed on the system then you need to make sure to use the python 3 interpreter. Older versions of Ubuntu come with python 2.7 installed. Run this command `virtualenv --python=/usr/bin/python3.5 dawa-updater`.

5. Clone the project from GitHub into the virtual environment.

6. Activate the environment by running `$ source bin/activate` after you are done using it run `deactivate` to stop using it. After running the activate script, deactivate will be in the PATH.

7. After activating the environment use PIP to install the dependencies by running `$ pip install -r requirements.txt`. If the dependencies have been changed update the requirements file by running `$ pip freeze > requirements.txt`

8. For the application to run it needs information about the database. There are 3 environmental variables that it will look for. `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`.

##### How to regenerate the database models
In case the database schema has changed, the model class needs to be regenerated. 
The process is described in on this website.

`http://peewee.readthedocs.org/en/latest/peewee/playhouse.html#pwiz`

###	Executing the application 



The application can be ran in two different modes. 

The first one is a fresh import. This mode should be used when there is no data from DAWA present in the database. 

the second mode is update it should be ran when some state of the dawa dataset is persisted to the local database.

So the usage of the application will be to have a database ready with the sammy schema created. The SAM_AREA, SAM_KOMMUNE and SAM_HOUSEUNITS tables should be empty. Start by running `$ python dawaupdater.py freshimport` this will import the DAWA data into the database and persist the first update sequence number. It will be used when updating the data in the future.

After the initial import is done, you can run `$ python dawaupdater.py update`, it will get the update sequence number saved in the database and update the data to the latest state. After it is done, it will register the update. 

Running the fresh import command is only necessary the first time you import the data.

