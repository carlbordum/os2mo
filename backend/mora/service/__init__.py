#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import address
from . import association  # noqa
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement  # noqa
from . import exports
from . import facet
from . import itsystem
from . import leave  # noqa
from . import manager  # noqa
from . import org
from . import orgunit
from . import related  # noqa
from . import role  # noqa
from . import integration_data
from . import configuration_options

blueprints = (
    address.blueprint,
    cpr.blueprint,
    detail_reading.blueprint,
    detail_writing.blueprint,
    employee.blueprint,
    exports.blueprint,
    facet.blueprint,
    integration_data.blueprint,
    itsystem.blueprint,
    org.blueprint,
    orgunit.blueprint,
    related.blueprint,
    exports.blueprint,
    integration_data.blueprint,
    configuration_options.blueprint,
)
