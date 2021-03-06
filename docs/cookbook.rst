Best practices for implementering
=================================

.. raw:: html

   <style>
   table.table-100{
       width: 100% !important
   }
   table.table-100 * {
       white-space: normal !important;
       vertical-align: top !important;
       font-size: 95% !important;
   }
   </style>

.. list-table:: Beskrivelse af implementeringsfaserne ved installation af OS2MO 2.0
   :header-rows: 1
   :widths: 1 1 100 1
   :class: table-100

   * - ID
     - Opgave
     - Beskrivelse
     - Ansvarlig/ udførende
   * - 1.
     - Tilvejebringelse af servermiljø
     - Der er behov for fire servere:

       1. Udviklingsserver
       2. Testserver
       3. Produktionsserver
       4. Applikationsovervågningsserver

       Det er muligt at installere oven på myndighedens eget container-miljø (VMware el.lign.).

       Servere:

       * Produktions-VM bestykket med 4 cores, 8GB Ram og 60 GB SSD harddisk

       * Andre VM’er (udvikling og test): 2 cores, 4GB Ram og 30 GB SSD harddisk

       * Ubuntu 16.04

       * Tillade udgående trafik på portene 80, 443, 4505 og 4506

       * Send den anvendte eksterne IP-adresse til Magenta, så der kan åbnes for adgang.
     - Kunde
   * - 2.
     - Adgange til servermiljø
     -
       * VPN-forbindelse tilvejebringes

       * Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.

       * Deploymentserverens IP-adresse er ``178.23.177.238``, og dens værtsnavn er ``ctrl1.magenta.dk``.
     - Kunde
   * - 3.
     - Indgåelse af aftaler
     -
       * Databehandleraftale; *påkrævet*.

       * Fortrolighedsaftale, om nødvendigt.
     - Kunde
   * -
     -
     -
       * Kontrakt
     - Leverandør
   * - 4.
     - Tilvejebringelse af SSL certifikater
     - OS2MO 2.0 skal udstilles på Kundens interne netværk (skyen eller lokalt) via HTTPS.
     - Kunde
   * - 5.
     - Tilvejebringelse af certifikater til Serviceplatformen
     - Der skal laves en aftale til at slå personer op i Serviceplatformens CPR-service (LaesPerson) og til hændelsesdata (LaesPersonAendringer), så personoplysninger forbliver ajourførte I OS2MO 2.0.
       Serviceplatformens CPR-data:Hvert it-system, der er oprettet på Serviceplatformen, registreres med ét unikt certifikat. Dvs. at det ikke er muligt at anvende samme certifikat for flere it-systemer på Serviceplatformen.

       * Kommunen skal bestille et Funktionscertifikat (FOCES) fra NETS til OS2MO 2.0-installationen

       * Kommunen skal oprette et it-systemet på
         Serviceplatformen til OS2MO 2.0-installationen

       * Kommunen skal oprette en serviceaftale på denne `service <https://www.serviceplatformen.dk/administration/serviceOverview/show?uid=e6be2436-bf35-4df2-83fe-925142825dc2>`_

       * Send de respektive FOCES inkl. keystore password, samt de 4 UUID'erne fra serviceaftalen til leverandøren
     - Kunde
   * - 6.
     - Installation af OS2MO 2.0 og tilhørende agenter
     - Se de enkelte trin nedenfor.
     - Leverandør
   * - 6. 1
     - Agent tilautentificering (SAML 2.0SSO)
     - Simpel rollestyring (rettigheder til at skrive alt, eller så har man ingen rettigheder) styres via oprettelse af en bruger i AD'et.

       * OS2MO 2.0 skal oprettes som en SP (Service Provider) hos IdP'en. OS2MO 2.0 udstiller metadata i XML-format, når løsningen er udrullet, så kunden får en URL til et metadata endpoint, som de kan give til IdP'en. Derefter sker konfigurationen automatisk

       * Kunden sender en URL til IdP'ens metadata for SAML SSO

       * Brugerens navn, og eventuelle roller skal i IdP'en tilføjes til de claims, der kommer tilbage i SAML-token

       * Hvis det er påkrævet at forespørgsler er signerede, kræves et sæt certifikater (public certificate og private key)

       Opgaven forudsætter, at Kunden har en IdP, der understøtter SAML 2.0 SSO.
     - Kunde / Leverandør
   * - 6. 2
     - Agent til Dansk Adresse Register (DAR)
     - Implementeringen foregår normalt automatisk, men en konfiguration i OS2MO 2.0 skal informere brugergrænsefladen om, at den nu befinder sig i given kommune og skal slå adresser op inden for kommunegrænsen
     - Leverandør
   * - 6. 3
     - Agent til Serviceplatformens CPR-data
     - Se også ID 5
       Der er behov for to services:
       1.Opslag på Serviceplatformen ved ansættelse af en medarbejder (LaesPerson)
       2.Løbende synkronisering mellem databasen (LoRa) og Serviceplatformens CPR-service (LaesPersonAendringer)
     - Leverandør
   * - 7.
     - Data iOS2MO 2.0
     - OS2MO 2.0 populeres med Kundens organisaions- og medarbejderdata.
       Se de enkelte trin nedenfor.
     - Kunde / Leverandør
   * - 7. 1
     - Tilvejebringelse af data
     - Kunden tilvejebringer adgang til API eller et databasedump med myndighedens organisaions- og medarbejderdata
     - Kunde
   * - 7. 2
     - Indlæsning af data
     - Leverandøren mapper data til OIO-standarden og indlæser dem i OS2MO 2.0’s database, LoRa
     - Leverandør

