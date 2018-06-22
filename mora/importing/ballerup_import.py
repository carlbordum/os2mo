#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import collections
import string
from datetime import datetime
import functools
import json
import os

import click
import pyexcel
from requests import Session

import csv

from . import spreadsheets
from .ballerup import dawa
from .ballerup import db
from ..service import common

session = Session()

LORA_URL = os.environ.get('LORA_URL', "http://10.220.213.154:8080")
MO_URL = os.environ.get('MO_URL', "http://localhost:5000/service")

ORG_UUID = os.environ.get('ORG_UUID', "3a87187c-f25a-40a1-8d42-312b2e2b43bd")

CSV_PATH = os.environ.get('CSV_PATH',
                          'mora/importing/ballerup/data/BALLERUP.csv')

ORG_UNIT_CSV = "/home/cm/proj/Ballerup/data/org.csv"
PERSON_CSV = "/home/cm/proj/Ballerup/data/person.csv"

MED_AMR_PATH = os.environ.get(
    'MED_AMR_PATH',
    '/home/cm/proj/Ballerup/data/MED-AMR-organisation.xlsx'
)

SD_LON_PATH = os.environ.get(
    'SD_LON_PATH',
    '/home/cm/proj/Ballerup/data/sd-lon-org.xlsx'
)

# Models

Enhed = collections.namedtuple(
    'Enhed',
    ['uuid', 'objectid', 'overordnetid', 'navn', 'enhedstype',
     'gyldig_fra', 'gyldig_til', 'bvn', 'addrs', 'type']
)

Person = collections.namedtuple(
    'Person',
    ['person_uuid', 'cpr', 'name', 'bvn']
)

Address = collections.namedtuple(
    'Address',
    ['person_uuid', 'value', 'type_uuid',
     'gyldig_fra', 'gyldig_til']
)

Engagement = collections.namedtuple(
    'Engagement',
    ['person_uuid', 'org_enhed_uuid', 'stillingsbetegnelse',
     'gyldig_fra', 'gyldig_til', 'bvn']
)

@functools.lru_cache(1024)
def get_class(typename, **kwargs):
    r = session.get(
        '{}/o/{}/f/{}'.format(
            MO_URL, ORG_UUID, typename),
    )

    assert r.ok

    for addrtype in r.json()['data']['items']:
        if all(addrtype[k] == v for k, v in kwargs.items()):
            return addrtype


@functools.lru_cache(1024)
def get_facet(typename, **kwargs):
    r = session.get(
        '{}/o/{}/f/{}'.format(
            MO_URL, ORG_UUID, typename),
    )
    assert r.ok
    return r.json()['uuid']


@functools.lru_cache(1024)
def get_unit(bvn):
    r = session.get(
        '{}/organisation/organisationenhed?bvn={}'.format(
            LORA_URL, bvn),
    )

    assert r.ok

    return r.json()['results'][0][0]



@functools.lru_cache(1024)
def lookup_addr_object(addr):
    addr_uuid = dawa.lookup(
        vejnavn=addr.vejnavn,
        husnummer=addr.husnummer,
        bynavn=addr.bynavn,
        postnummer=addr.postnummer
    )
    if not addr_uuid:
        fail(addr.uuid, addr.vejnavn, addr.husnummer, addr.postnummer, addr.bynavn)
    return addr_uuid


@functools.lru_cache(1024)
def lookup_addr_fuzzy(addr):
    addr_uuid = dawa.lookup_fuzzy(
        q=addr
    )
    if not addr_uuid:
        fail("Addr lookup failed:", addr)
    return addr_uuid


def log(msg, error=False):
    click.echo(msg, err=error)


def fail(*args):
    i = map(str, args)
    arg_string = ", ".join(i)
    log(arg_string, True)


def insert(path, payload, *args, method="POST"):
    r = session.request(
        method,
        path,
        json=payload
    )
    if not r:
        try:
            fail(json.dumps(r.json(), indent=2),
                 json.dumps(payload, indent=2), *args)
        except json.JSONDecodeError:
            fail(r, json.dumps(payload, indent=2), *args)
    else:
        return r.json()


def address_payload(value, address_type):
    payload = {
        "address_type": address_type,
        "type": "address",
        "validity": {
            "from": "2010-01-01T00:00:00+00:00",
            "to": None
        }
    }
    if address_type['scope'] == 'DAR':
        payload['uuid'] = value
    else:
        payload['value'] = value

    return payload


def org_unit_payload(unit: Enhed, parent_uuid, addrs=None):
    payload = {
        "name": unit.navn,
        "parent": {
            "uuid": parent_uuid
        },
        "org_unit_type": {
            "uuid": unit.enhedstype
        },
        "user_key": unit.bvn,
        "validity": {
            "from": "1970-01-01",
            "to": None
        },
    }
    if unit.uuid:
        payload['uuid'] = unit.uuid
    if addrs:
        addr_type = get_class('address_type', user_key='AdressePost')
        payload["addresses"] = [address_payload(addr, addr_type) for addr in addrs]

    return payload


def klasse_payload(bvn, titel, beskrivelse, ansvarlig, facet):
    virkning = {
        "from": "-infinity",
        "to": "infinity"
    }

    klasse = {
        "attributter": {
            "klasseegenskaber": [
                {
                    "brugervendtnoegle": bvn,
                    "titel": titel,
                    "beskrivelse": beskrivelse,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "klassepubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": virkning
                }
            ]
        },
        "relationer": {
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": ansvarlig,
                    "virkning": virkning
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facet,
                    "virkning": virkning
                }
            ]
        },
        "note": "Indlæst af Magenta"
    }

    return klasse


def stillingsbetegnelser():
    log('Importerer stillingsbetegnelser')

    # Get job titles by finding all rows referred to by engagements
    jobtitle_cache = {}

    asdb_jobtitles = db.session.query(
        db.Jobtitles
    ).join(
        db.Engagement, db.Jobtitles.uuid == db.Engagement.stillingUuid
    ).distinct().all()

    for row in asdb_jobtitles:
        title = row.title.lower()
        jobtitle_cache[title] = (row.uuid, klasse_payload(
                row.title.lower(),
                row.title,
                str(row.objektid),
                ORG_UUID,
                get_facet('job_function')
            ))

    with open(PERSON_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['Stillingsbetegnelse']
            if not jobtitle_cache.get(title.lower()):
                jobtitle_cache[title.lower()] = (None, klasse_payload(
                    title.lower(),
                    title,
                    title,
                    ORG_UUID,
                    get_facet('job_function')
                ))

    with click.progressbar(
        jobtitle_cache.values()
    ) as bar:
        for uuid, row in bar:
            if uuid:
                insert(
                    "{}/klassifikation/klasse/{}".format(LORA_URL, uuid),
                    row,
                    method="PUT"
                )
            else:
                insert(
                    "{}/klassifikation/klasse".format(LORA_URL),
                    row,
                    method="POST"
                )


def lederansvar():
    log('Importerer lederansvar')

    # Get responsibility by finding all rows referred to by function tasks
    responsibilities = db.session.query(
        db.Jobtitles
    ).join(
        db.Functiontasks, db.Jobtitles.uuid == db.Functiontasks.taskUuid
    ).distinct().all()

    with click.progressbar(
        responsibilities
    ) as bar:
        for row in bar:
            k = klasse_payload(
                row.uuid,
                row.title,
                str(row.objektid),
                ORG_UUID,
                get_facet('responsibility')
            )
            insert(
                "{}/klassifikation/klasse".format(LORA_URL),
                k,
                row,
                method="POST"
            )


def ledertyper():
    log('Importerer ledertyper')

    # Get manager types by finding all distinct names in Functions
    manager_types = db.session.query(
        db.Functions.name
    ).distinct().all()

    with click.progressbar(
        manager_types
    ) as bar:
        for row in bar:
            k = klasse_payload(
                row.name.lower(),
                row.name,
                row.name,
                ORG_UUID,
                get_facet('manager_type')
            )
            a = insert(
                "{}/klassifikation/klasse".format(LORA_URL),
                k,
                row,
                method="POST"
            )


def enhedstyper():
    log('Importerer enhedstyper')
    with open(ORG_UNIT_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        unit_types = {row['enhedstype'] for row in reader}

    with click.progressbar(
        unit_types
    ) as bar:
        for row in bar:
            unit = db.session.query(db.Jobtitles).filter(
                db.Jobtitles.uuid == row).one()
            k = klasse_payload(
                unit.brugervendtnoegle if unit.brugervendtnoegle else unit.title,
                string.capwords(unit.title),
                str(unit.objektid),
                ORG_UUID,
                get_facet('org_unit_type')
            )
            insert(
                "{}/klassifikation/klasse/{}".format(LORA_URL, unit.uuid),
                k,
                row,
                method="PUT"
            )


def enhed():
    """
    Due to the parent/child structure found in org units we are forced
    to analyze and insert the tree in the correct order
    """
    log('Importerer organisationsenheder')

    # objektid to uuid
    org_unit_map = {'0': ORG_UUID}
    # parent objektid to row
    structure = {}

    # Fetch dataset
    data = []
    with open(ORG_UNIT_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            asdb_unit = db.session.query(db.Unit).filter(
                db.Unit.uuid == row['uuid']).one_or_none()

            def format_date(d):
                return datetime.strptime(d, '%d/%m/%Y').isoformat()

            valid_from = format_date(row['gyldig_fra'])
            valid_to = None if row[
                                   'gyldig_til'] == "INFINITY" else format_date(
                row['gyldig_til'])

            # Lookup the enhed address
            addrs = db.session.query(
                db.GetGeographicDetails).filter(
                db.Unit.uuid == row['uuid'],
                db.Unit.uuid == db.Locations.unitUuid,
                db.Locations.GeographicUuid == db.GetGeographicDetails.uuid
            ).all()
            addr_type = get_class('address_type', user_key='AdressePost')
            addr_uuids = [lookup_addr_object(geo) for geo in addrs]
            addr_uuids = [uuid for uuid in addr_uuids if uuid]

            data.append(Enhed(
                row['uuid'],
                row['objectid'],
                row['overordnetid'],
                row['navn'],
                row['enhedstype'],
                valid_from,
                valid_to,
                asdb_unit.brugervendtNoegle if asdb_unit else None,
                addr_uuids,
                type=row['type']
            ))

    # Build structure
    for row in data:
        org_unit_map[row.objectid] = row.uuid
        entry = structure.setdefault(row.overordnetid, [])
        entry.append(row)

    def traverse_units(parent_id, bar):
        units = structure.get(parent_id, [])
        for u in units:
            parent_id = org_unit_map[u.overordnetid]
            if u.type == "root":
                path = "{}/organisation/organisationenhed/{}".format(
                    LORA_URL, u.uuid)
                addresses = [{
                    "uuid": a,
                    "objekttype": addr_type['uuid']
                } for a in u.addrs]
                payload = common.create_organisationsenhed_payload(
                    u.navn,
                    u.gyldig_fra,
                    "infinity" if u.gyldig_til is None else u.gyldig_til,
                    u.bvn,
                    ORG_UUID,
                    u.enhedstype,
                    ORG_UUID,
                    addresses,
                )
                insert(path, payload, u, method="PUT")
            # Normal units
            else:
                path = "{}/ou/create".format(MO_URL)
                addresses = [address_payload(a, addr_type) for a in u.addrs]
                payload = org_unit_payload(
                    u,
                    parent_id,
                    addresses
                )
                insert(path, payload, u)
            bar.update(1)
            traverse_units(u.objectid, bar)

    with click.progressbar(length=len(org_unit_map) - 1) as bar:
        # 0 is the root enhed
        traverse_units("0", bar)


def bruger():
    log('Importerer brugere')

    def bruger_payload(person: Person):
        return {
            'uuid': person.person_uuid,
            'cpr_no': person.cpr,
            'name': person.name,
            'user_key': person.bvn,
            'org': {
                'uuid': ORG_UUID
            }
        }

    bruger_cache = {}

    attachedpersons = db.session.query(
        db.Attachedpersons.personUuid).subquery()
    functionpersons = db.session.query(
        db.Functionpersons.personUuid).subquery()

    asdb_persons = db.session.query(db.Person).filter(
        db.Person.uuid.in_(attachedpersons.select()) |
        db.Person.uuid.in_(functionpersons.select())
    ).all()

    with open(PERSON_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cpr = row['Cpr-nummer']
            bruger_cache[cpr] = Person(
                person_uuid=row['PersonUID'],
                cpr=cpr,
                name="{} {}".format(row['Fornavn'], row['Efternavn']),
                bvn=row['BrugerID']
            )


    for row in asdb_persons:
        cpr = row.personNumber
        if not bruger_cache.get(cpr):
            bruger_cache[cpr] = Person(
                person_uuid=row.uuid,
                cpr=cpr,
                name=row.addresseringsnavn,
                bvn=None
            )

    with click.progressbar(
        bruger_cache.values(),
    ) as bar:
        for person in bar:
            payload = bruger_payload(person)
            insert('{}/e/create'.format(MO_URL), payload)


def engagement():
    log('Importerer engagementer')

    def engagement_payload(unit_id, job_function, engagement_type,
                           bvn, valid_from, valid_to):
        payload = [{
            "type": "engagement",
            "org_unit": {
                "uuid": unit_id
            },
            "job_function": {
                "uuid": job_function
            },
            "engagement_type": {
                "uuid": engagement_type
            },
            "validity": {
                "from": valid_from,
                "to": valid_to
            },
            "user_key": bvn
        }]

        return payload

    data = []
    with open(PERSON_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            def format_date(d):
                try:
                    return datetime.strptime(d, '%d-%m-%Y').isoformat()
                except ValueError:
                    return datetime.strptime(d, '%m/%d/%Y').isoformat()

            valid_from = format_date(row['Ansættelse gyldig fra'])
            d = row['Ansættelse gyldig til']
            valid_to = None if d == "31-12-9999" or d == "12/31/9999" else format_date(
                d)
            bvn = row['BrugerID']

            data.append(Engagement(
                person_uuid=row['PersonUID'],
                org_enhed_uuid=row['Org-enhed OUID'],
                stillingsbetegnelse=row['Stillingsbetegnelse'],
                gyldig_fra=valid_from,
                gyldig_til=valid_to,
                bvn=bvn
            ))

    with click.progressbar(
        data,
    ) as bar:
        for engagement in bar:  # type: Engagement
            bruger_uuid = engagement.person_uuid

            if engagement.stillingsbetegnelse:
                stilling_uuid = get_class(
                    'job_function',
                    user_key=engagement.stillingsbetegnelse.lower())['uuid']
            else:
                stilling_uuid = get_class(
                    'job_function', user_key='unknown')['uuid']
            e = engagement_payload(
                engagement.org_enhed_uuid,
                stilling_uuid,
                get_class('engagement_type', user_key='Ansat')['uuid'],
                engagement.bvn,
                engagement.gyldig_fra,
                engagement.gyldig_til
            )
            insert("{}/e/{}/create".format(MO_URL, bruger_uuid), e)


def adresser():
    log('Importerer adresser')

    engagement_map = {}

    with open(PERSON_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        engagement_map = {e['EngagementUuid']: e['PersonUID'] for e in reader}

    with click.progressbar(
        engagement_map.items(),
    ) as bar:
        for e_uuid, p_uuid in bar:
            addrs = db.session.query(db.ContactChannel).filter(
                db.ContactChannel.ownerUuid == e_uuid,
                db.ContactChannel.value != ' ').all()

            addr_payload = [
                address_payload(
                    addr.value,
                    get_class('address_type', user_key=addr.typeUuid)
                )
                for addr in addrs
            ]
            path = "{}/e/{}/create".format(MO_URL, p_uuid)
            insert(path, addr_payload)


def tilknytning():
    log('Importerer tilknytninger')

    attachedpersons = db.session.query(db.t_attachedpersons).all()

    def tilknytning_payload(unit_id):
        payload = [{
            "org_unit": {
                "uuid": unit_id
            },
            "job_function": get_class('job_function', user_key='unknown'),
            "association_type": get_class('association_type',
                                          user_key='Tilknyttet'),
            "validity": {
                "from": "2010-01-01T00:00:00+00:00",
                "to": None
            },
            "type": "association"
        }]

        return payload

    with click.progressbar(
        attachedpersons
    ) as bar:
        for row in bar:
            a = tilknytning_payload(row.unitUuid)
            insert("{}/e/{}/create".format(MO_URL, row.personUuid), payload=a)


def leder():
    log("Importerer ledere")

    def leder_payload(unit, task, name):
        payload = [{
            "type": "manager",
            "org_unit": {
                "uuid": unit,
            },
            "manager_type": {
                "uuid": get_class("manager_type", user_key=name.lower())[
                    'uuid']
            },
            "responsibility": {
                "uuid": get_class("responsibility", user_key=task)['uuid']
            },
            "manager_level": {
                "uuid": get_class("manager_level", user_key="unknown")['uuid']
            },
            "validity": {
                "from": "2010-01-01T00:00:00+00:00",
                "to": None
            }
        }]

        return payload

    ledere = db.session.query(
        db.Functionpersons.personUuid, db.Functionunits.unitUuid,
        db.Functiontasks.taskUuid, db.Functions.name
    ).join(
        db.Functions,
        db.Functions.functionUuid == db.Functionpersons.functionUuid
    ).join(
        db.Functionunits,
        db.Functionunits.functionUuid == db.Functions.functionUuid
    ).join(
        db.Functiontasks,
        db.Functiontasks.functionUuid == db.Functionunits.functionUuid
    ).all()

    with click.progressbar(ledere) as bar:
        for person, unit, task, name in bar:
            payload = leder_payload(unit, task, name)
            insert("{}/e/{}/create".format(MO_URL, person), payload=payload)


def load_csv():
    log('Importerer CSV')
    spreadsheets.run(LORA_URL, (CSV_PATH,), False, False, 1, False, False,
                     False, False)

def med_amr_unit_types():
    sheet = pyexcel.get_sheet(file_name=MED_AMR_PATH, name_columns_by_row=0)
    records = sheet.to_records()
    types = {u['OrgType'] for u in records}
    for type in types:
        k = klasse_payload(
            bvn=type.lower(),
            titel=type,
            beskrivelse=type,
            ansvarlig=ORG_UUID,
            facet=get_facet('org_unit_type')
        )
        insert(
            "{}/klassifikation/klasse".format(LORA_URL),
            k,
            method="POST"
        )


def med_amr():
    def med_amr_bvn(key):
        return "MED_AMR_{}".format(key)

    def convert_from_sheet():
        sheet = pyexcel.get_sheet(file_name=MED_AMR_PATH, name_columns_by_row=0)
        records = sheet.to_records()
        for row in records:
            unit_type = get_class(
                'org_unit_type',
                user_key=row['OrgType'].lower()
            )['uuid']
            yield Enhed(
                uuid=None,
                objectid=row['Id'],
                overordnetid=row['ParentID'],
                navn=row['OrgEnhed'],
                enhedstype=unit_type,
                gyldig_fra=None,
                gyldig_til=None,
                bvn=med_amr_bvn(row['Id']),
                addrs=None
            )

    rows = list(convert_from_sheet())

    # parent objektid to row
    structure = {}

    for row in rows:  # type: Enhed
        parent_id = row.overordnetid if row.overordnetid else 0
        entry = structure.setdefault(parent_id, [])
        entry.append(row)

    def traverse_units(parent_id, bar):
        units = structure.get(parent_id, [])
        parent_uuid = get_unit(med_amr_bvn(parent_id))
        if not parent_uuid:
            print(med_amr_bvn(parent_id), parent_uuid)
            return
        for u in units:  # type: Enhed
            payload = org_unit_payload(
                u,
                parent_uuid
            )
            insert("{}/ou/create".format(MO_URL), payload, u)
            bar.update(1)
            traverse_units(u.objectid, bar)

    with click.progressbar(length=len(rows)) as bar:
        traverse_units(0, bar)


def sd_lon():
    def sd_lon_bvr(key):
        return "SD_LON_{}".format(key)

    def convert_from_sheet():
        sheet = pyexcel.get_sheet(file_name=SD_LON_PATH, name_columns_by_row=0)
        records = sheet.to_records()
        for row in records:
            unit_type = get_class(
                'org_unit_type',
                user_key='unknown'
            )['uuid']
            address = row['Lokation-navn']
            addr_uuid = lookup_addr_fuzzy(address) if address else None
            yield Enhed(
                uuid=None,
                objectid=row['objektid'],
                overordnetid=row['overordnetid'],
                navn=row['Unit-navn'],
                enhedstype=unit_type,
                gyldig_fra=None,
                gyldig_til=None,
                bvn=sd_lon_bvr(row['objektid']),
                addrs=[addr_uuid] if addr_uuid else []
            )

    rows = list(convert_from_sheet())

    # parent objektid to row
    structure = {}

    for row in rows:  # type: Enhed
        parent_id = row.overordnetid if row.overordnetid else 0
        entry = structure.setdefault(parent_id, [])
        entry.append(row)

    def traverse_units(parent_id, bar):
        units = structure.get(parent_id, [])
        for u in units:  # type: Enhed
            if parent_id is 0:
                addr_type = get_class('address_type', user_key='AdressePost')
                addresses = [{
                    "uuid": a,
                    "objekttype": addr_type['uuid']
                } for a in u.addrs]
                payload = common.create_organisationsenhed_payload(
                    enhedsnavn=u.navn,
                    valid_from="1970-01-01",
                    valid_to="infinity",
                    brugervendtnoegle=u.bvn,
                    tilhoerer=ORG_UUID,
                    enhedstype=u.enhedstype,
                    overordnet=ORG_UUID,
                    adresser=addresses
                )
                insert(
                    "{}/organisation/organisationenhed".format(LORA_URL),
                    payload,
                    u,
                    method="POST"
                )
            else:
                parent_uuid = get_unit(sd_lon_bvr(parent_id))
                payload = org_unit_payload(
                    u,
                    parent_uuid
                )
                insert("{}/ou/create".format(MO_URL), payload, u)
            bar.update(1)
            traverse_units(u.objectid, bar)

    with click.progressbar(length=len(rows)) as bar:
        traverse_units(0, bar)

def run(*args, **kwargs):
    # load_csv()
    # stillingsbetegnelser()
    # lederansvar()
    # ledertyper()
    # enhedstyper()

    # MED-AMR
    # med_amr_unit_types()
    # med_amr()

    # SD Løn
    # sd_lon()

    # IDM
    enhed()
    # bruger()
    # engagement()
    # adresser()
    # tilknytning()
    # leder()
    # Importer orlov?
    # Importer IT?
