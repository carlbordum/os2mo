#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.converters import writing


class TestMoveOrgFunktion(unittest.TestCase):
    maxDiff = None

    def test_should_move_org_funktion_correctly(self):
        orgfunk = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'funktionsnavn': 'job-title 1 b688513d-11f7-'
                                     '4efc-b679-ab082a2055d0',
                    'brugervendtnoegle': "deadbeef-dead-beef-"
                                         "dead-deadbeefdead",
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }]
            },
            'note': 'Flyt engagement',
            'relationer': {
                'tilknyttedeenheder': [{
                    'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    'virkning': {
                        'to_included': False, 'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }],
                'tilknyttedebrugere': [{
                    'uuid': '2f9a3e4f-5f91-40a4-904c-68a376b7320f',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }],
                'opgaver': [{
                    'uuid': '11111111-1111-1111-1111-111111111111',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-12-01T00:00:00+00:00'
                    },
                    'gyldighed': 'Aktiv'
                }]
            }
        }

        expected_output = {
            'note': 'Flyt engagement',
            'relationer': {
                'tilknyttedeenheder': [{
                    'uuid': 'a1d4dabc-3fa3-496f-9b09-c19748547c37',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+00:00',
                        'from': '2017-01-01T00:00:00+00:00'
                    }
                }]
            }
        }

        org_unit = "a1d4dabc-3fa3-496f-9b09-c19748547c37"
        from_date = '2017-01-01'

        self.assertDictEqual(
            writing.move_org_funktion(org_unit, from_date, orgfunk),
            expected_output,
            'Unexpected output for move org funktion')