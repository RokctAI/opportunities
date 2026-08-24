Private Bag X828, PRETORIA, 0001 Dr AB Xuma Building1112 Voortrekker Road, Pretoria Townlands 351-JR,
PRETORIA, 0187 Tel (012) 395 8000
webDHIS (DHIS2) Technical Stack Overview
1. Core Platform
Platform
• Application Platform: DHIS2 (webDHIS), using a stable production release.
• Primary Function: National health information management platform supporting
aggregate reporting, indicator management, programme monitoring, dashboards,
analytics, and Tracker-based use cases.
Architecture
The platform follows a standard three-tier architecture:
Presentation Layer
• Browser-based web user interface.
• HTML5, CSS, and JavaScript technologies.
• Responsive design supporting desktop and mobile access.
Application Layer
• Java-based DHIS2 application stack.
• Web API services.
• Apache Tomcat application server.
• Support for custom applications and extensions using approved DHIS2 frameworks and
APIs.
Data Layer
• PostgreSQL database platform.
• Storage of metadata, transactional data, analytics tables, system configuration, and
audit information.

Deployment Model
• Centrally hosted and managed.
• Multi-instance deployments.
• Physical, virtualised, cloud-hosted.
1. Client Access and Security
Supported Clients
• DHIS2 Capture.
• Data Entry applications.
• Dashboard and Analytics applications.
• Pivot Tables.
• Maps and GIS tools.
• Event and Tracker applications.
• Custom DHIS2 applications developed using approved DHIS2 development
frameworks.
Browser Support
• Google Chrome.
• Microsoft Edge.
• Mozilla Firefox.
Mobile and Offline Capability
• DHIS2 Android Capture application.
• Browser-based offline caching and synchronisation features.
• Support for low-bandwidth and intermittent-connectivity environments.
Identity and Access Management
• Role-Based Access Control.
• Organisation-unit-based data access controls.
• User groups and programme-specific permissions.
• Integration with enterprise identity services such as:
o Active Directory (AD)
o LDAP
o Single Sign-On (SSO)
o Other approved authentication mechanisms
1. Data and Metadata Management
Metadata Standards
The platform maintains nationally approved metadata including:
• Organisation Units
• Data Elements
• Indicators
• Data Sets
• Category Combinations

• Programmes
• Tracked Entity Types
• Validation Rules
•
All metadata changes are subject to established NDoH governance processes in line with
approved National Indicator Data Set (NIDS).
Data Domains
The platform supports:
• Aggregate routine health information.
• Tracker-based individual records.
• Disease and programme monitoring.
This includes, but is not limited to:
• HIV and AIDS
• Tuberculosis (TB)
• Maternal, Child and Women's Health (MCWH)
• Non-Communicable Diseases (NCDs)
• Emergency Medical Services (EMS)
1. Integration and Interoperability
API Framework
The primary integration mechanism is the DHIS2 REST Web API.
Supported exchange formats may include:
• JSON
• CSV
• XML
• ADX
• FHIR-based payloads
1. Infrastructure, Operations and Security
Hosting Environment
The production environment conforms to:
• High availability
• Redundancy
• Backup and recovery
• Disaster recovery capabilities
• Secure network architecture

Monitoring and Support
The operational environment includes:
• Application monitoring.
• Database monitoring.
• Infrastructure monitoring.
• Performance management.
• Incident and problem management processes.

Server name URL GB Ram GB Storage CPU DB Server
za-nat-db-1 N/A 128 5448 8 N/A
national-db-server N/A 192 3836 8 N/A
national-upgrade-db-server N/A 192 2485 8 N/A
za-stack5-lb-1-vm N/A 2 100 8 N/A
zandoh-db N/A 256 4200 48 N/A
prod-lb-1-vm N/A 8 200 8 N/A
za-nhc-dhis-1-vm https://nhc-portal.dhis.dhmis.org 12 100 16 zandoh-db-01
za-nqpr-dhis-1-vm https://nqpr.dhis.dhmis.org 18 100 16 zandoh-db-01
za-ripda-dhis-1-vm https://ripda.dhis.dhmis.org 18 100 16 zandoh-db-01
za-sarms-dhis-1-vm https://sarms.dhis.dhmis.org 18 100 16 zandoh-db-01
za-idsr-dhis-1-vm https://za-idsr.dhis.dhmis.org 24 100 16 zandoh-db-01
za-schoolhealth-dhis-1-vm https://schoolhealth.dhis.dhmis.org 18 100 16 zandoh-db-01
za-dd-dhis-1-vm https://dd.dhmis.org 24 100 16 zandoh-db-01
NDOH Instances za-art-dhis-1-vm https://art.dhis.dhmis.org 24 100 16 zandoh-db-01
za-pec-dhis-2-vm https://pec.dhis.dhmis.org 18 200 16 zandoh-db-01
za-nat-dhis-1-vm https://za.dhis.dhmis.org 32 200 8 za-nat-db-1
non-prod-db N/A 256 4200 48 N/A
non-prod-lb-vm N/A 2 100 8 N/A
za-nat-staging-dhis-1-vm https://staging.dhis.dhmis.org/za 32 200 8 national-db-server
za-stage-ishp-1-vm https://staging.dhis.dhmis.org/schoolhealth 8 100 8 non-prod-db
za-pec240-1-vm https://staging.dhis.dhmis.org/pec240 8 100 8 non-prod-db
za-ripda240-1-vm https://staging.dhis.dhmis.org/ripda240 8 100 8 non-prod-db
za-zaidsr240-1-vm https://staging.dhis.dhmis.org/zaidsr240 8 100 8 non-prod-db
za-nqpr240-1-vm https://staging.dhis.dhmis.org/nqpr240 8 100 8 non-prod-db
za-ripda-training-1-vm https://training.dhis.dhmis.org/ripda 8 100 8 non-prod-db
za-ndd-stage-1-vm https://staging.dhis.dhmis.org/nidsintegrated 8 100 8 non-prod-db
za-prov-db N/A 256 4200 48 N/A
prod-lb-1-vm N/A 8 200 8 N/A
Prov Instances

za-ec-dhisweb-1-vm https://ec.dhis.dhmis.org 18 100 16 za-prov-db
za-lp-dhisweb-1-vm https://lp.dhis.dhmis.org 18 100 16 za-prov-db
za-gp-dhisweb-1-vm https://gp.dhis.dhmis.org 18 100 16 za-prov-db
za-mp-dhisweb-1-vm https://mp.dhis.dhmis.org 18 100 16 za-prov-db
za-nw-dhisweb-1-vm https://nw.dhis.dhmis.org 18 100 16 za-prov-db
za-fs-dhisweb-1-vm https://fs.dhis.dhmis.org 18 100 16 za-prov-db
za-wc-dhisweb-1-vm https://wc.dhis.dhmis.org 12 100 16 za-prov-db
za-nc-dhisweb-1-vm https://nc.dhis.dhmis.org 18 100 16 za-prov-db
za-kz-dbserv-1 N/A 192 2500 8 N/A
za-int1-lb-1-vm N/A 2 100 8 N/A
za-kz-dhisweb-1-vm https://kz.dhis.dhmis.org/ 40 500 8 za-kz-dbserv-1
za-kz-dhisweb-2-vm https://kz.dhis.dhmis.org/ 16 500 8 za-kz-dbserv-1
za-kz-dhisweb-3-vm https://kz.dhis.dhmis.org/ 16 500 8 za-kz-dbserv-1
dbserver kzstaging N/A 128 2500 8 N/A
za-kz-stage-1-vm https://staging.dhis.dhmis.org/kz 8 100 8 dbserver kzstaging
Prov Instances
national-upgrade-db-
za-kz-dev-1-vm https://reporting.dhis.dhmis.org 16 100 8 server
za-kz-stage-2-vm 8 100 8
non-prod-db N/A 256 4200 48 N/A
non-prod-lb-vm N/A 2 100 8 N/A
gp-stage-web-1-vm https://staging.dhis.dhmis.org/gp 12 100 8 non-prod-db
lp-stage-web-1-vm https://staging.dhis.dhmis.org/lp 10 100 8 non-prod-db
mp-stage-web-1-vm https://staging.dhis.dhmis.org/mp 10 100 8 non-prod-db
nc-stage-web-1-vm https://staging.dhis.dhmis.org/nc 10 100 8 non-prod-db
ec-stage-web-1-vm https://staging.dhis.dhmis.org/ec 10 100 8 non-prod-db
wc-stage-web-1-vm https://staging.dhis.dhmis.org/wc 8 100 8 non-prod-db
kz-stage-web-1-vm 12 100 8 non-prod-db
fs-stage-web-1-vm https://staging.dhis.dhmis.org/fs 10 100 8 non-prod-db
nw-stage-web-1-vm https://staging.dhis.dhmis.org/nw 10 100 8 non-prod-db

Prov Instances
hisp-hispland-vm https://playground.hisp.org/hispland 8 100 8 non-prod-db
za-train-hispland-dhis-1-vm https://training.dhis.dhmis.org/hispland 8 100 8 non-prod-db
za-fs240-1-vm https://staging.dhis.dhmis.org/fs240 8 100 8 non-prod-db

webDHIS
❑ DHIS2 is an open source, web-based platform most commonly used as a health
management information system (HMIS). In this regard, the NDoH has a non-
exclusive license to use the DHIS software modules. The District Health
Management Information System Policy serves as an overarching policy for the
use of DHIS together with the relevant Standard Operating Procedures (SOPs).
❑ The webDHIS system used in South Africa has multiple instances, and each has
an organisation hierarchy where the names of all public health facilities are
captured according to the following hierarchy: province, district, sub-district,
health facility, and reporting unit within or under a health facility. The hierarchy is
continually aligned with the Master Health Facility List (MHFL). A DHIS instance
consists of the DHIS database, a PostgreSQL database, and the webDHIS
application front-end which is web-based. Each instance is hosted on a server
with the database server and one or more web servers accessible through a
URL.
1

webDHIS
2

ACTIVE DHIS USERS DHIS2 RECORDS NDOH TRAINED DHIS EXPERTS
8476
493 205 144
46
YOUR TITLE
YOUR TITLE
The number of active DHIS2 users in SA has CurTreynpte nyuomurb edre soirfe DdH teISx2t hreecreo rfdosr more Over the last T2y ypeea yrso uHrI SdPes hiraesd t treaixnte hde erex pfeorrt ms ore
steadily increased by 58% since Sep 2019 information on the type of template in Provinces ainnfdo trhmea Ntioanti oonna tl hleev teyl poen o Df HteImS2p late
that’s being made..
adminitshtraatt’sio bneing made..
DAILY DATA CAPTURING (%) FACILITY CAPTURING (%)
100 150
80
100 95 97
60 86
76 78
40 50 60
41
20 34 40 47 48 51 53 57
0
0
2019 2020 2021 2022 2023 2024 2025
2019 2020 2021 2022 2023 2024 2025
DATA SET TIMELINESS RATE (%) DATA ENTRY TIMELINESS RATE (%)
100 100
94.9
90.2
80 83.8 86.8 80
73
60 63.1 60
4087.7 91.6 92 92.3 95
40 38.7
20
20
0
0
2021 2022 2023 2024 2025
2019 2020 2021 2022 2023 2024 2025
