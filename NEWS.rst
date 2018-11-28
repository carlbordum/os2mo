Version 0.13.0 (in development)
===============================

Internal changes
----------------

* 23799: Added custom UUID url converter, stringifying UUID parameters in
  order to standardise our use of UUIDs internally.
* 25396: Added backend validation API, for validating individual fields from
  the front-end.

Version 0.12.0, 2018-11-16
==========================

New features
------------

* #23928: We now use our `Flask SAML SSO
  <https://github.com/magenta-aps/flask_saml_sso/>`_ module for
  authentication.
  Session is now shared between OS2MO and LoRa.
* #22382: Manager hierarchy - the service returns all managers in a
  hierarchical order
* #24077: We now support access addresses in addition to regular 
  addresses from Dansk Adresseregister, with combined autocompletion 
  of the two.


Internal changes
----------------

* #25193: Improved handling of external configuration files for OS2MO.
  A warning is no longer triggered on unknown settings.
* #24545: OS2MO 2.0 as an OS2 Level 3 Product
* #24664: Meet the requirements of the standard or explain why you do not
  https://mora.readthedocs.io/en/master/README.html?highlight=sag#lora-backend-model
* #24656: Documentation of the requirements for operating the solution
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24659: Only one version of the core code: https://github.com/OS2mo
* #24662: Best practice for implementing the solution in your organization
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24661: Presentation material
  https://www.magenta.dk/?service=rammearkitektur &
  https://os2.eu/projekt/os2mo
* #24663: Codestandards
  https://mora.readthedocs.io/en/master/README.html#kodestandarder
* #24665: Process plan for the implementation of the solution
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24655: Open Source license criteria are met 
  https://mora.readthedocs.io/en/master/README.html#licens-og-copyright


Bug fixes
---------
* #24738: Removed sorting and icons for some columns.

Known bugs
----------
* #25405: Validation errors when creating org unit relations outside of the
  parent org unit range are not properly shown in UI


Version 0.11.1 2018-11-02
==========================

Bug fixes
---------

* #25028: Timemachine now shows and updates the organisation unit 
  view when changing organisation unit


Version 0.11.0, 2018-10-30
==========================

New features
------------
* #24547: Backend support for modifying the name and CPR number of employees.
* #24400: Better documentation of command line interface.
* #24750: Added functionality for listing and retrieving generated
  export files from external directory.
* #24092: Added functionality for creating managers through the
  organisation interface in UI, including vacant managers.
* #24131: Added a simple configuration module that makes it possible
  to hide remove fields and tabs in the UI.
* #23960: A new page in the UI, ``/forespoergsler``, offers CSV
  exports of certain specific queries.
* #23276: Support for synchronising user names and CPR numbers added
  to the agent for fetching personal data from *Serviceplatformen*.
* #24214: Added associations to employees in the MED-organisation in
  Ballerup Kommune.


Internal changes
----------------

* #21966: Implemented use of Vuex in frontend.
* #24654: Source code is relocated to the `OS2mo organisation
  <https://github.com/OS2mo>`_ on GitHub.
* #24658: Technical implementation available as a `sub-page on our
  ReadTheDocs site
  <https://mora.readthedocs.io/en/development/dev.html>`_.
* #24657: The solution is fully documented on `ReadTheDocs
  <https://mora.readthedocs.io/>`_.
* #24660: Communication documents for the business and strategic level
  created at:

  - `OS2mo’s næste sprint går i retning af OS2-produktet og udvikling
    af integrationer
    <https://os2.eu/blog/os2mos-naeste-sprint-gaar-i-retning-af-os2-produktet-og-udvikling-af-integrationer>`_
  - `Lokal rammearkitektur og IDM med OS2MO & OS2rollekatalog
    <https://os2.eu/blog/lokal-rammearkitektur-og-idm-med-os2mo-os2rollekatalog>`_.


Bug fixes
---------

* #24150:  When terminating an employee, mark any manager roles it
  possesses as vacant rather than terminating them.
* #24069: Handle DAR address errors gracefully, displaying the error
  message rather than suppressing all addresses.
* #24077: Allow entering DAR access addresses as well as regular
  adresses in all fields, and allow reading historical addresses.
* #24810: Support for Internet Explorer 11.
* #24570: Sorting now works after performing an update.


Known bugs
----------


Version 0.10.1-post1, 2018-10-12
================================

Bug fixes
---------

* A missing check for Node packages broke the `mox
  <http://github.com/magenta-aps/mox/>` test suite.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.


Version 0.10.1, 2018-10-08
==========================

New features
------------

* #22849: Updated SAML implementation, with support for signed requests,
  single sign-on and single logout.
* #22381: Replace 'Enhedsnummer' with a description of the location of the organisational unit.
* #23558: Added the possibility to create managers without employees through the ou endpoint, thus allowing for vacant manager positions.
* #24014: Since we now model IT systems using an
  ``organisationfunktion``, we can now represent the account name.
* #22849: Added handling for user permissions, giving a fitting error if a user attempts an action without the correct permissions.
* #23976: Employees with their associated relations can now be created with one API call. All requests are now validated before being submitted to LoRa, to prevent half-writes.
* #24134: Columns in the UI can now be sorted.
* #24135: Dropdowns are now alphabetically sorted.
* #24068: Clicking the OS2-icon in the top left corner now takes you to the landing page.
* #23793: Support has been added for P-nummer as address type.
* #23781: Managers now have a separate set of address types.

Internal changes
----------------

* #23559: REST API now uses and enforces ISO 8601 dates in all cases
  except history display. All ``from`` or ``to`` dates must either
  lack a timestamp or correspond to midnight, Central European time.
* #23559: The ``terminate`` endpoints for employees as well as units
  now read the date from the ``to`` field rather than ``from``.
* #24198: We now model IT systems using ``organisationfunktion``
  rather than a direct relation.
* #23558: The employee is now optional on managers.

API changes
-----------

* #24200: Move all writing and editing APIs from ``/service/ou`` and
  ``/service/e/`` to a shared endpoint ``/service/details``. This
  primarily means that writing operations no longer require knowledge of the
  user, allowing e.g. vacant managers.

Bug fixes
---------

* #24067: Fixed being able to edit root organisational units
* #23559: Display end dates *inclusively*, so that the year ends 31
  December rather than 1 January.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.

Version 0.9.0, 2018-09-07
=========================

New features
------------

* #23778: Support for IT-systems on units
  
Internal changes
----------------

* #23992: Updated API documentation and README
* #23993: Reorganisation of source code layout
* #23994: Refactoring of frontend code

Bug fixes
---------

* #24012: Fixed hotkey support
* #24013: Fixed rename unit dialog not being populated correctly
