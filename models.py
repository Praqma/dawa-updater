import peewee

import config

database = peewee.MySQLDatabase(
    config.DATABASE_NAME,
    host=config.DATABASE_HOST,
    user=config.DATABASE_USER,
    passwd=config.DATABASE_PASSWORD,
)


class UnknownField:
    pass


class BaseModel(peewee.Model):
    class Meta:
        database = database


class SamArea(BaseModel):
    areacode = peewee.CharField(db_column='AREACODE')
    areaid = peewee.CharField(db_column='AREAID', primary_key=True)
    areaname = peewee.CharField(db_column='AREANAME')
    areatypeid = peewee.CharField(db_column='AREATYPEID')
    coordinates = peewee.TextField(db_column='COORDINATES', null=True)
    kommuneid = peewee.IntegerField(db_column='KOMMUNEID')

    class Meta:
        db_table = 'sam_area'


class SamAreaadmin(BaseModel):
    areacomment = peewee.CharField(db_column='AREACOMMENT', null=True)
    areaid = peewee.CharField(db_column='AREAID')
    lastupdated = peewee.DateTimeField(db_column='LASTUPDATED', null=True)
    organisationid = peewee.CharField(db_column='ORGANISATIONID')
    passwd = peewee.CharField(db_column='PASSWD', null=True)

    class Meta:
        db_table = 'sam_areaadmin'
        primary_key = peewee.CompositeKey('areaid', 'organisationid')


class SamAreatype(BaseModel):
    areatypeid = peewee.CharField(db_column='AREATYPEID', primary_key=True)
    areatypename = peewee.CharField(db_column='AREATYPENAME')

    class Meta:
        db_table = 'sam_areatype'


class SamDistrict(BaseModel):
    areaid = peewee.CharField(db_column='AREAID')
    coordinates = peewee.TextField(db_column='COORDINATES', null=True)
    customizedid = peewee.DecimalField(db_column='CUSTOMIZEDID', null=True)
    districtcomment = peewee.TextField(db_column='DISTRICTCOMMENT', null=True)
    districtno = peewee.DecimalField(db_column='DISTRICTNO')
    exportallowed = peewee.DecimalField(db_column='EXPORTALLOWED', null=True)
    footer = peewee.TextField(db_column='FOOTER', null=True)
    header = peewee.TextField(db_column='HEADER', null=True)
    lastupdated = peewee.DateTimeField(db_column='LASTUPDATED', null=True)
    name = peewee.CharField(db_column='NAME', null=True)
    organisationid = peewee.CharField(db_column='ORGANISATIONID')
    passwd = peewee.CharField(db_column='PASSWD', null=True)

    class Meta:
        db_table = 'sam_district'
        primary_key = peewee.CompositeKey('areaid', 'districtno', 'organisationid')


class SamHouseunits(BaseModel):
    adgangsadresse_uuid = peewee.CharField(db_column='ADGANGSADRESSE_UUID', unique=True)
    doorcount = peewee.DecimalField(db_column='DOORCOUNT', null=True, default=1)
    equalno = peewee.DecimalField(db_column='EQUALNO', null=True)
    houseid = peewee.CharField(db_column='HOUSEID')
    kommuneid = peewee.DecimalField(db_column='KOMMUNEID')
    roadid = peewee.DecimalField(db_column='ROADID')
    sognenavn = peewee.CharField(db_column='SOGNENAVN')
    sognenr = peewee.DecimalField(db_column='SOGNENR')
    x = peewee.DecimalField(db_column='X', null=True)
    y = peewee.DecimalField(db_column='Y', null=True)
    zip = peewee.DecimalField(db_column='ZIP')
    roadname = peewee.CharField(db_column='roadName', index=True, null=True)
    valgkreds = peewee.IntegerField(null=True)

    class Meta:
        db_table = 'sam_houseunits'
        primary_key = peewee.CompositeKey('houseid', 'kommuneid', 'roadid')


class SamHouseunitsindistrict(BaseModel):
    areaid = peewee.CharField(db_column='AREAID')
    districtid = peewee.IntegerField(db_column='DISTRICTID')
    houseid = peewee.CharField(db_column='HOUSEID')
    kommuneid = peewee.IntegerField(db_column='KOMMUNEID')
    organisationid = peewee.CharField(db_column='ORGANISATIONID')
    roadid = peewee.IntegerField(db_column='ROADID')

    class Meta:
        db_table = 'sam_houseunitsindistrict'
        primary_key = peewee.CompositeKey('areaid', 'districtid', 'houseid', 'organisationid', 'roadid')


class SamKommune(BaseModel):
    name = peewee.CharField(null=True)

    class Meta:
        db_table = 'sam_kommune'


class SamOrganisation(BaseModel):
    contactinfo = peewee.TextField(db_column='CONTACTINFO', null=True)
    defaultexportallowed = peewee.DecimalField(db_column='DEFAULTEXPORTALLOWED', null=True)
    exportallowed = peewee.DecimalField(db_column='EXPORTALLOWED', null=True)
    lastupdated = peewee.DateTimeField(db_column='LASTUPDATED', null=True)
    logofile = peewee.CharField(db_column='LOGOFILE', null=True)
    name = peewee.CharField(db_column='NAME', null=True)
    organisationid = peewee.CharField(db_column='ORGANISATIONID', primary_key=True)
    passwd = peewee.CharField(db_column='PASSWD', null=True)
    standardfooter = peewee.CharField(db_column='STANDARDFOOTER', null=True)
    standardheader = peewee.CharField(db_column='STANDARDHEADER', null=True)
    url = peewee.CharField(db_column='URL')

    class Meta:
        db_table = 'sam_organisation'


class SamRoad(BaseModel):
    bottom = peewee.DecimalField(db_column='BOTTOM', null=True)
    kommuneid = peewee.DecimalField(db_column='KOMMUNEID')
    left = peewee.DecimalField(db_column='LEFT', null=True)
    name = peewee.CharField(db_column='NAME', index=True, null=True)
    right = peewee.DecimalField(db_column='RIGHT', null=True)
    roadid = peewee.DecimalField(db_column='ROADID')
    top = peewee.DecimalField(db_column='TOP', null=True)

    class Meta:
        db_table = 'sam_road'
        primary_key = peewee.CompositeKey('kommuneid', 'roadid')


class SamRoadpoly(BaseModel):
    coorno = peewee.DecimalField(db_column='COORNO')
    kommuneid = peewee.DecimalField(db_column='KOMMUNEID')
    linieno = peewee.DecimalField(db_column='LINIENO')
    roadid = peewee.DecimalField(db_column='ROADID')
    updated = peewee.DecimalField(db_column='UPDATED', null=True)
    x = peewee.DecimalField(db_column='X', null=True)
    y = peewee.DecimalField(db_column='Y', null=True)

    class Meta:
        db_table = 'sam_roadpoly'
        primary_key = peewee.CompositeKey('coorno', 'kommuneid', 'linieno', 'roadid')


class SamRoadsinroute(BaseModel):
    areaid = peewee.CharField(db_column='AREAID')
    customizedroadname = peewee.CharField(db_column='CUSTOMIZEDROADNAME', null=True)
    districtno = peewee.DecimalField(db_column='DISTRICTNO')
    housecount = peewee.DecimalField(db_column='HOUSECOUNT', null=True)
    housefrom = peewee.CharField(db_column='HOUSEFROM', null=True)
    housenumberfrom = peewee.CharField(db_column='HOUSENUMBERFROM', null=True)
    housenumberspec = peewee.CharField(db_column='HOUSENUMBERSPEC', null=True)
    housenumberto = peewee.CharField(db_column='HOUSENUMBERTO', null=True)
    houseto = peewee.CharField(db_column='HOUSETO', null=True)
    kommuneid = peewee.DecimalField(db_column='KOMMUNEID', null=True)
    lastcountcalculation = peewee.DateTimeField(db_column='LASTCOUNTCALCULATION', null=True)
    lastupdated = peewee.DateTimeField(db_column='LASTUPDATED', null=True)
    organisationid = peewee.CharField(db_column='ORGANISATIONID')
    roadid = peewee.DecimalField(db_column='ROADID', null=True)
    routeid = peewee.DecimalField(db_column='ROUTEID')
    sequences = peewee.DecimalField(db_column='SEQUENCES')
    showerror = peewee.DecimalField(db_column='SHOWERROR', null=True)

    class Meta:
        db_table = 'sam_roadsinroute'
        primary_key = peewee.CompositeKey('areaid', 'districtno', 'organisationid', 'routeid', 'sequences')


class SamRoute(BaseModel):
    areaid = peewee.CharField(db_column='AREAID')
    customizedid = peewee.DecimalField(db_column='CUSTOMIZEDID', null=True)
    districtno = peewee.DecimalField(db_column='DISTRICTNO')
    lastupdated = peewee.DateTimeField(db_column='LASTUPDATED')
    maxzoom = peewee.CharField(db_column='MAXZOOM', null=True)
    note = peewee.CharField(db_column='NOTE', null=True)
    organisationid = peewee.CharField(db_column='ORGANISATIONID')
    routeid = peewee.DecimalField(db_column='ROUTEID')
    routename = peewee.TextField(db_column='ROUTENAME', null=True)
    scale = peewee.DecimalField(db_column='SCALE', null=True)
    serrelation = peewee.DecimalField(db_column='SERRELATION', null=True)
    showhouseonmap = peewee.DecimalField(db_column='SHOWHOUSEONMAP', null=True)
    showroadonmap = peewee.DecimalField(db_column='SHOWROADONMAP', null=True)
    text = peewee.TextField(db_column='TEXT', null=True)
    x = peewee.DecimalField(db_column='X', null=True)
    y = peewee.DecimalField(db_column='Y', null=True)
    households = peewee.IntegerField(null=True)

    class Meta:
        db_table = 'sam_route'
        primary_key = peewee.CompositeKey('areaid', 'districtno', 'organisationid', 'routeid')


class Updates(BaseModel):
    sekvensnummer = peewee.CharField(primary_key=True)
    tidspunkt = peewee.DateTimeField()

    class Meta:
        db_table = 'updates'
