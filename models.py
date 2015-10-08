from peewee import *

database = MySQLDatabase('sammy_updated', **{'user': 'root', 'password': 'root'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class SamArea(BaseModel):
    areacode = CharField(db_column='AREACODE')
    areaid = CharField(db_column='AREAID', primary_key=True)
    areaname = CharField(db_column='AREANAME')
    areatypeid = CharField(db_column='AREATYPEID')
    coordinates = TextField(db_column='COORDINATES', null=True)
    kommuneid = IntegerField(db_column='KOMMUNEID')

    class Meta:
        db_table = 'sam_area'

class SamAreaadmin(BaseModel):
    areacomment = CharField(db_column='AREACOMMENT', null=True)
    areaid = CharField(db_column='AREAID')
    lastupdated = DateTimeField(db_column='LASTUPDATED', null=True)
    organisationid = CharField(db_column='ORGANISATIONID')
    passwd = CharField(db_column='PASSWD', null=True)

    class Meta:
        db_table = 'sam_areaadmin'
        primary_key = CompositeKey('areaid', 'organisationid')

class SamAreatype(BaseModel):
    areatypeid = CharField(db_column='AREATYPEID', primary_key=True)
    areatypename = CharField(db_column='AREATYPENAME')

    class Meta:
        db_table = 'sam_areatype'

class SamDistrict(BaseModel):
    areaid = CharField(db_column='AREAID')
    coordinates = TextField(db_column='COORDINATES', null=True)
    customizedid = DecimalField(db_column='CUSTOMIZEDID', null=True)
    districtcomment = TextField(db_column='DISTRICTCOMMENT', null=True)
    districtno = DecimalField(db_column='DISTRICTNO')
    exportallowed = DecimalField(db_column='EXPORTALLOWED', null=True)
    footer = TextField(db_column='FOOTER', null=True)
    header = TextField(db_column='HEADER', null=True)
    lastupdated = DateTimeField(db_column='LASTUPDATED', null=True)
    name = CharField(db_column='NAME', null=True)
    organisationid = CharField(db_column='ORGANISATIONID')
    passwd = CharField(db_column='PASSWD', null=True)

    class Meta:
        db_table = 'sam_district'
        primary_key = CompositeKey('areaid', 'districtno', 'organisationid')

class SamHouseunits(BaseModel):
    adgangsadresse_uuid = CharField(db_column='ADGANGSADRESSE_UUID', unique=True)
    doorcount = DecimalField(db_column='DOORCOUNT', null=True, default=1)
    equalno = DecimalField(db_column='EQUALNO', null=True)
    houseid = CharField(db_column='HOUSEID')
    kommuneid = DecimalField(db_column='KOMMUNEID')
    roadid = DecimalField(db_column='ROADID')
    sognenavn = CharField(db_column='SOGNENAVN')
    sognenr = DecimalField(db_column='SOGNENR')
    x = DecimalField(db_column='X', null=True)
    y = DecimalField(db_column='Y', null=True)
    zip = DecimalField(db_column='ZIP')
    roadname = CharField(db_column='roadName', index=True, null=True)
    valgkreds = IntegerField(null=True)

    class Meta:
        db_table = 'sam_houseunits'
        primary_key = CompositeKey('houseid', 'kommuneid', 'roadid')

class SamHouseunitsindistrict(BaseModel):
    areaid = CharField(db_column='AREAID')
    districtid = IntegerField(db_column='DISTRICTID')
    houseid = CharField(db_column='HOUSEID')
    kommuneid = IntegerField(db_column='KOMMUNEID')
    organisationid = CharField(db_column='ORGANISATIONID')
    roadid = IntegerField(db_column='ROADID')

    class Meta:
        db_table = 'sam_houseunitsindistrict'
        primary_key = CompositeKey('areaid', 'districtid', 'houseid', 'organisationid', 'roadid')

class SamKommune(BaseModel):
    name = CharField(null=True)

    class Meta:
        db_table = 'sam_kommune'

class SamOrganisation(BaseModel):
    contactinfo = TextField(db_column='CONTACTINFO', null=True)
    defaultexportallowed = DecimalField(db_column='DEFAULTEXPORTALLOWED', null=True)
    exportallowed = DecimalField(db_column='EXPORTALLOWED', null=True)
    lastupdated = DateTimeField(db_column='LASTUPDATED', null=True)
    logofile = CharField(db_column='LOGOFILE', null=True)
    name = CharField(db_column='NAME', null=True)
    organisationid = CharField(db_column='ORGANISATIONID', primary_key=True)
    passwd = CharField(db_column='PASSWD', null=True)
    standardfooter = CharField(db_column='STANDARDFOOTER', null=True)
    standardheader = CharField(db_column='STANDARDHEADER', null=True)
    url = CharField(db_column='URL')

    class Meta:
        db_table = 'sam_organisation'

class SamRoad(BaseModel):
    bottom = DecimalField(db_column='BOTTOM', null=True)
    kommuneid = DecimalField(db_column='KOMMUNEID')
    left = DecimalField(db_column='LEFT', null=True)
    name = CharField(db_column='NAME', index=True, null=True)
    right = DecimalField(db_column='RIGHT', null=True)
    roadid = DecimalField(db_column='ROADID')
    top = DecimalField(db_column='TOP', null=True)

    class Meta:
        db_table = 'sam_road'
        primary_key = CompositeKey('kommuneid', 'roadid')

class SamRoadpoly(BaseModel):
    coorno = DecimalField(db_column='COORNO')
    kommuneid = DecimalField(db_column='KOMMUNEID')
    linieno = DecimalField(db_column='LINIENO')
    roadid = DecimalField(db_column='ROADID')
    updated = DecimalField(db_column='UPDATED', null=True)
    x = DecimalField(db_column='X', null=True)
    y = DecimalField(db_column='Y', null=True)

    class Meta:
        db_table = 'sam_roadpoly'
        primary_key = CompositeKey('coorno', 'kommuneid', 'linieno', 'roadid')

class SamRoadsinroute(BaseModel):
    areaid = CharField(db_column='AREAID')
    customizedroadname = CharField(db_column='CUSTOMIZEDROADNAME', null=True)
    districtno = DecimalField(db_column='DISTRICTNO')
    housecount = DecimalField(db_column='HOUSECOUNT', null=True)
    housefrom = CharField(db_column='HOUSEFROM', null=True)
    housenumberfrom = CharField(db_column='HOUSENUMBERFROM', null=True)
    housenumberspec = CharField(db_column='HOUSENUMBERSPEC', null=True)
    housenumberto = CharField(db_column='HOUSENUMBERTO', null=True)
    houseto = CharField(db_column='HOUSETO', null=True)
    kommuneid = DecimalField(db_column='KOMMUNEID', null=True)
    lastcountcalculation = DateTimeField(db_column='LASTCOUNTCALCULATION', null=True)
    lastupdated = DateTimeField(db_column='LASTUPDATED', null=True)
    organisationid = CharField(db_column='ORGANISATIONID')
    roadid = DecimalField(db_column='ROADID', null=True)
    routeid = DecimalField(db_column='ROUTEID')
    sequences = DecimalField(db_column='SEQUENCES')
    showerror = DecimalField(db_column='SHOWERROR', null=True)

    class Meta:
        db_table = 'sam_roadsinroute'
        primary_key = CompositeKey('areaid', 'districtno', 'organisationid', 'routeid', 'sequences')

class SamRoute(BaseModel):
    areaid = CharField(db_column='AREAID')
    customizedid = DecimalField(db_column='CUSTOMIZEDID', null=True)
    districtno = DecimalField(db_column='DISTRICTNO')
    lastupdated = DateTimeField(db_column='LASTUPDATED')
    maxzoom = CharField(db_column='MAXZOOM', null=True)
    note = CharField(db_column='NOTE', null=True)
    organisationid = CharField(db_column='ORGANISATIONID')
    routeid = DecimalField(db_column='ROUTEID')
    routename = TextField(db_column='ROUTENAME', null=True)
    scale = DecimalField(db_column='SCALE', null=True)
    serrelation = DecimalField(db_column='SERRELATION', null=True)
    showhouseonmap = DecimalField(db_column='SHOWHOUSEONMAP', null=True)
    showroadonmap = DecimalField(db_column='SHOWROADONMAP', null=True)
    text = TextField(db_column='TEXT', null=True)
    x = DecimalField(db_column='X', null=True)
    y = DecimalField(db_column='Y', null=True)
    households = IntegerField(null=True)

    class Meta:
        db_table = 'sam_route'
        primary_key = CompositeKey('areaid', 'districtno', 'organisationid', 'routeid')

class Updates(BaseModel):
    sekvensnummer = CharField(primary_key=True)
    tidspunkt = DateTimeField()

    class Meta:
        db_table = 'updates'
