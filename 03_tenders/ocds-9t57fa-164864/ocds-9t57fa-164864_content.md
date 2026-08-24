REQUEST FOR INFORMATION
(PRE-MARKET CONSULTATION)
SARS RFI 01/2025
BUSINESS REQUIREMENTS SPECIFICATION
RFI 01/2026- THE PROVISION OF A VENDOR RECONCILIATION AUTOMATION
SOLUTION, INCLUDING MAINTENANCE AND SUPPORT FOR A PERIOD OF THREE
(3) YEARS.

Page 2 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
TABLE OF CONTENTS:
1 EXECUTIVE SUMMARY 4
2 BACKGROUND 4
3 TECHNOLOGY SOLUTION 5
4 SOLUTION SCOPE 5
5 DESIGN ASSUMPTIONS, RISKS, CONSTRAINTS AND DEPENDENCIES 6
6 CONCEPTUAL SOLUTION DESIGN 8
7 PROCESS DEFINITION 9
8 REPORTING REQUIREMENTS 33
9 NON-FUNCTIONAL REQUIREMENTS 34

Page 3 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
LIST OF ACRONYMS
Acronym Description
ACT Activity Identifier
AFS Annual Financial Statements
AI Artificial Intelligence
AP Accounts Payable
ASS Assumption Identifier
BAPI Business Application Programming Interface
BPR Business Process Reference
BRS Business Requirements Specification
CON Constraint Identifier
CO Controlling – SAP management accounting module
DEP Dependency Identifier
ECC ERP Central Component – SAP enterprise resource planning system
EDI Electronic Data Interchange
ERP Enterprise Resource Planning
ESB Enterprise Service Bus
FI Financial Accounting – Core SAP finance module
FIN Financial Officer role identifier
FIM Finance Manager role identifier
GL General Ledger
GR/IR Goods Receipt / Invoice Receipt
GRN Goods Received Note
ICT Information and Communications Technology
Intermediate Documents – SAP electronic message format used for exchanging data between SAP and other
IDocs
systems
IFRS International Financial Reporting Standards
JSON JavaScript Object Notation
LLM Large Language Model
MFA Multi-Factor Authentication
MM Materials Management
MS Microsoft
Optical Character Recognition – technology that reads text from scanned invoices, statements, or PDF
OCR
documents and converts it into electronic data for automated processing
PDF Portable Document Format
PFMA Public Finance Management Act
PO Purchase Order
POPIA Protection of Personal Information Act
PRN Principle Identifier
RBAC Role-Based Access Control
REP Report Identifier
REST Representational State Transfer
RFI Request for Inofrmation
RSK Risk Identifier
RUL Business Rule Identifier
SAP Systems, Applications, and Products
SAP SAP Process Integration / Process Orchestration – SAP middleware used to integrate SAP with external
PI/PO applications
SARS South African Revenue Service
SD Sales and Distribution
SLA Service Level Agreement
SOAP Simple Object Access Protocol
SoD Segregation of Duties
SOP Standard Operating Procedures
SSO Single Sign-On
S/4HANA SAP S/4HANA – SAP’s next-generation enterprise resource planning suite
XML Extensible Markup Language

Page 4 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
RFI 01/2026
Business Requirements Specification
This document forms part of the RFI 01/2026 pack. The document sets out SARS’s business requirements for the
Appointment of a Service Provider for the Provision of a Vendor Reconciliation Automation Solution, Including
Maintenance and Support for a Period of Three (3) Years.
1 EXECUTIVE SUMMARY
The South African Revenue Service (SARS) is committed to strengthening financial governance, improving operational
efficiency, and enhancing the accuracy, completeness, and reliability of financial information. As part of its ongoing
modernisation agenda, SARS seeks to leverage technology-enabled solutions that improve internal controls, support
regulatory compliance, and promote effective financial management across the organisation.
Vendor account reconciliation is a critical financial control activity that supports the validation of vendor balances,
liabilities, payments, and related financial transactions recorded within the SARS financial environment. Effective
vendor reconciliation contributes directly to the integrity of financial reporting, the accuracy of the Annual Financial
Statements (AFS), and the maintenance of sound supplier relationships.
This Business Requirements Specification (BRS) defines the business, functional, technical, integration, reporting,
security, compliance, and operational requirements for a Vendor Reconciliation Automation Solution that will enable
SARS to modernise and optimise its vendor reconciliation capability and strengthen financial control. The solution
must be compatible with and/or housed within SAP to support seamless integration with SARS financial processes
and systems.
2 BACKGROUND
SARS currently performs vendor account reconciliations through a predominantly manual process that requires the
collection, review, comparison, and reconciliation of vendor statements against financial records maintained within
SAP and supporting documentation. The process is labour-intensive, time-consuming, and highly dependent on
spreadsheets and manual intervention.
The current environment presents several operational, governance, and financial control challenges, including limited
process automation, delayed identification and resolution of discrepancies, increased risk of human error, limited
visibility of outstanding reconciliation items, extensive manual effort, and a growing administrative burden associated
with increasing transaction volumes and financial close activities. These challenges impact the efficiency of
reconciliation activities and may adversely affect financial reporting, financial close processes, supplier management,
and audit readiness.
To address these challenges, SARS intends to implement a Vendor Reconciliation Automation Solution that will enhance
financial control, improve operational efficiency, strengthen governance and auditability, and support the
organisation’s broader objective of becoming a modern, efficient, and digitally enabled institution. The initiative
supports SARS strategic outcomes by improving internal efficiency, strengthening financial governance, enhancing
accountability, and reinforcing public trust through improved financial oversight and control.

Page 5 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
2.1 Current Environment and Transaction Volumes
a) SARS currently processes approximately 53,862 invoices annually.
b) Vendor reconciliation activities are performed across more than 1,400 vendor accounts, including trade
vendors, municipalities, utilities, and other vendor categories.
c) The reconciliation process supports multiple vendor reconciliation scenarios and requires the automated
identification, investigation, and resolution of reconciliation exceptions.
d) Service providers should consider these volumes when proposing the solution, implementation approach,
sizing assumptions, and pricing
3 TECHNOLOGY SOLUTION
SARS seeks to procure a Vendor Reconciliation Automation Solution through a competitive Request for Proposal (RFP)
process. The proposed solution must support the modernisation and optimisation of vendor reconciliation activities
within SARS and align with the organisation’s strategic objectives of strengthening financial governance, improving
operational efficiency, enhancing financial reporting integrity, and supporting effective financial management
practices.
The solution must be compatible with and/or housed within SAP and support seamless integration with SARS
financial systems and related business processes. The solution must integrate with SAP ECC and/or SAP S/4HANA.
The objective of the solution is to automate the reconciliation of vendor accounts and general ledger balances within
SAP, improving accuracy, reducing manual effort, and ensuring compliance.
The solution must enable the electronic ingestion of vendor statements and supporting documentation, perform
automated matching against SAP records, identify reconciliation discrepancies and exceptions, and support workflow-
driven investigation, review, approval, and reporting processes with minimal manual intervention.
The solution must provide a single, integrated platform that supports the end-to-end vendor reconciliation lifecycle
and enhances visibility, control, auditability, and operational efficiency across the reconciliation process.
For a comprehensive understanding of the end-to-end business, functional, technical, reporting, integration,
compliance, and operational requirements, this document should be read in conjunction with the process models,
process definitions, reporting requirements, integration requirements, and non-functional requirements contained
within this BRS.
4 SOLUTION SCOPE
4.1 SCHEDULE EXECUTION (1ST OF EACH MONTH)
a) Run SAP Vendor Account Analysis
b) Filter by reconciliation date range
c) Export open items report
4.2 INTELLIGENT DATA PROCESSING
a) Accepts multiple formats (PDF, Excel, EDI)
b) Uses intelligent OCR to extract structured data from various layouts.
c) Performs automated format validation
d) Organize by vendor number/priority (high-value vendors first)

Page 6 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
4.3 AUTOMATED RECONCILIATION AND MATCHING
a) Matches vendor statements to SAP AP Open Items (FBICS3) and GR/IR Items (FBICA3)
b) Utilises advanced, rule based matching logic with user defined tolerances
c) Flag unapplied credits
4.4 PROACTIVE EXCEPTION HANDLING & WORKFLOW
a) Automatically flags all discrepancies (missing invoices, amount mismatches, etc.)
b) Provides interface for manual review, assignment and resolution
c) User designed approval workflows with notifications and escalations
d) Users can categorize discrepancies for clear tracking (i.e., Timing Difference, Unmatched GRN, Vendor
Error)
e) Adjustment Posting (if required) for Credit memo creation, Payment reversal and Journal entry etc.
f) Validation & enrichment of financial data
g) GL recording and automated routing to the Reconciliation Hub
h) Automated matching of large-volume transactions
i) Manual adjustment workflow for exceptions
j) Real-time discrepancy scanning and reporting
k) Reconciliation Ledger creation and management
l) Financial close acceleration and reporting dashboards
4.5 INTEGRATED REPORTING & ANALYTICS
a) Offers interactive dashboards that provides real-time status tracking, aging analysis, and performance
metrics
b) Generates exportable reports (PDF/Excel)
c) Integration with SAP ECC or S/4HANA, supporting multi-company code environments, and handling high-
volume transactions.
d) General Ledger Reconciliation Audit trail
4.6 PERFORMANCE
a) Deliver reliable and responsive performance to ensure uninterrupted operations, including:
1. 99.9% uptime
2. Load balancing and fail-over
b) The solution must be capable of supporting increasing volumes of vendor, financial, and reconciliation data
without compromising performance or system stability.
4.7 EXCLUSIONS
a) Modifications to upstream SAP modules
b) Legacy spreadsheet-based reconciliation

Page 7 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
5 DESIGN ASSUMPTIONS, RISKS, CONSTRAINTS AND DEPENDENCIES
5.1 ASSUMPTIONS
ASSUMPTION ID ASSUMPTION STATEMENT
ASS001 SARS has resources and capabilities for the project
ASS002 Corporate Finance have required skills to use the Automated Vendor Reconciliation system
ASS003 Proposed business requirements will leverage on existing SARS processes
Sourcing a tailored, cost-effective and more convenient system which is preferably compatible
ASS004
with SAP
Adding qualitative opportunities to improve internal systems, vendor relationships and
ASS005
management
5.2 RISKS
RISK ID RISK STATEMENT RISK MITIGATION
The software requires ongoing Maintenance and support costs in the total cost of
annual maintenance, and additional ownership and budget forecasts, and negotiate clear
RSK001
consulting costs may be incurred if support agreements and service level commitments with
issues arise during the rollout phase. the vendor
Staff may be resistant to adopting the Implement a structured change management and
new technology, potentially communication plan to address staff concerns, foster
impacting implementation and engagement, and encourage adoption of the new
RSK002
adoption timelines technology, thereby minimizing potential delays in
implementation
Staff may be concerned about
Establish a formal change communication strategy that
potential job redundancy as the
clearly outlines the purpose of automation initiatives,
software automates vendor account
RSK003
focusing on productivity enhancement and improved
reconciliation, which could impact
process effectiveness rather than job losses.
morale and change adoption.
Employees attending training on the Introducing a more user-friendly system
new system will result in reduced
RSK004
productivity.

Page 8 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
RISK ID RISK STATEMENT RISK MITIGATION
Employees resist the change over to Parallel integration of the system
the new system, which will result in
RSK005
employee relations issues.
Delays in the implementation of the Providing a more agile approach in the integration of the
system could potentially demotivate system.
RSK006
employees.
5.3 CONSTRAINTS
CONSTRAINT ID CONSTRAINT STATEMENT
CON001 Unavailability of funds may impact the implementation of the project
Stakeholders are not timeous available to review and approve the business requirements
CON002
documented
CON003 Development and Testing effort
5.4 DEPENDENCIES
DEPENDENCY ID DEPENDENCY STATEMENT
Stakeholder availability
DEP001
Maintenance contracts
DEP002
Integration between impacted systems is seamless to support the execution of the process
DEP003
designed
Resource and system availability
DEP004
Stakeholder availability
DEP005
6 CONCEPTUAL SOLUTION DESIGN
6.1 SOLUTION DESIGN PRINCIPLES
PRINCIPLE ID PRINCIPLE STATEMENT
The solution must be designed to comply with all applicable legislation, regulations, and internal
PRN001
policies, including PFMA, SARS Act, POPIA (where applicable), and audit requirements
PRN002 Data Extraction (OCR/AI): Uses AI (Large Language Models or Intelligent OCR) to read and extract
structured data (invoice number, date, amount, currency) from various PDF and document formats,
even poor-quality or non-standard statements. Automated Import: Can often connect directly to an
email inbox or use a drag-and-drop feature for bulk upload.

Page 9 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
PRINCIPLE ID PRINCIPLE STATEMENT
PRN003 ERP Integration: Directly connects to your SAP system (S/4HANA or current version of SAP) to pull
your Accounts Payable (Vendor) line items. Automated Matching: Matches the transactions from
the supplier's PDF statement against your SAP records. This typically uses multiple criteria (e.g.,
invoice number, date, amount) and fuzzy logic to find near-matches
PRN004 GR/IR Clearance: By identifying invoices on the supplier statement that are missing from SAP, the
system helps proactively chase those invoices, which is a key activity in managing and clearing the
GR/IR (Goods Receipt/Invoice Receipt) account
PRN005 The solution should support real-time or near real-time interfaces with vendors and internal systems
to improve reconciliation timeliness and reduce outstanding open items.
PRN006 The solution must be scalable to accommodate increases in vendor volumes, transaction volumes,
and future business requirements
PRN007 The automated solution must integrate seamlessly with SAP or other core financial systems to
ensure a single source and eliminate duplicate data capture
PRN008 The system must be intuitive and easy to use, reducing reliance on manual workarounds and
extensive training while improving productivity within Corporate Finance.
PRN009 The solution must provide real-time dashboards and management reports on reconciliation status,
exceptions, aging, and resolution performance to support oversight and decision-making.
PRN010 The solution must support backup, recovery, and failover mechanisms to ensure continuity of
reconciliation processes in the event of system failures.
PRN011 Discrepancy Highlighting: The primary output is an exception report showing all transactions that
could not be automatically matched. Workflows and Dashboards: Provides interactive dashboards
for AP staff to investigate, assign, and track the resolution of exceptions (e.g., 'Supplier Invoice
Missing,' 'Amount Discrepancy,' 'Requires Write-Off'). Audit Trail: Maintains a full, auditable history
of the reconciliation and exception resolution process
PRN012 The system must ingest raw transactional data from SAP FI, MM, SD, and CO modules with high
fidelity
PRN013 The system must enforce standardized formatting and structure of financial data
PRN014 The system must support high-volume, high-speed matching

Page 10 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
7 PROCESS DEFINITION
7.1 HIGH LEVEL BUSINESS PROCESS MODEL MANAGE VENDOR ACCOUNT RECONCILIATION
7.2 BUSINESS PROCESS/SUB-PROCESS LISTING BUSINESS PROCESS/SUB-PROCESS
BUSINESS BUSINESS PROCESS BUSINESS PROCESS PRE-CONDITION POST CONDITION
PROCESS ID NAME DESCRIPTION (INPUT) (OUTPUT)
The process involves Supporting documentation Vendor account
reviewing, matching, and (purchase orders, goods balances are accurately
Administer Vendor reconciling vendor receipt notes, contracts, and reconciled
Account invoices, payments, proof of payment) is
BPR001
Reconciliation credit notes, and vendor available and accessible
statements to identify
and resolve discrepancies
in a timely manner
BPR002 The process involves the Vendor invoices, credit Vendor account
system performing real- notes, and payments have transactions are
time matching of been electronically received automatically matched,
transactions based on and posted in the SAP cleared, or flagged as
Execute Vendor
configurable criteria such exceptions.
Account
as invoice number,
Reconciliation
amount, vendor
reference, purchase
order number, and
posting date

Page 11 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS BUSINESS PROCESS BUSINESS PROCESS PRE-CONDITION POST CONDITION
PROCESS ID NAME DESCRIPTION (INPUT) (OUTPUT)
BPR003 The process involves Vendor invoices, credit All valid transactions are
extraction of vendor notes, and payments have matched, cleared, or
account balances and been correctly captured and appropriately explained
open item reports from posted in the financial
Perform Vendor
SAP, together with the system.
Account
receipt of vendor
Reconciliation
statements. Transactions
are matched against
supporting
documentation.
BPR004 The process involves Vendor account Identified discrepancies
Administer Vendor investigating reconciliation has been are fully investigated,
Account reconciliation exceptions performed, and resolved, or formally
Reconciliation or unmatched items are discrepancies or exceptions escalated in accordance
Investigation identified through have been identified. with procedures
automated reconciliation
BPR005 The process involves Vendor account Vendor account
submission of completed reconciliations have been reconciliations are
Coordinate Vendor vendor account completed and submitted reviewed, validated,
Account reconciliations, including for review and formally approved
Reconciliation all supporting
Review documentation and
discrepancy to the
reviewer for approval
BPR006 The process involves Vendor account Vendor account
collection and reconciliations have been reconciliation reports
consolidation of performed and updated in are accurately
Administer Vendor
reconciliation data from the SAP generated, validated,
Account
the SAP including open and reviewed.
Reconciliation
item reports, matched
Reporting
and unmatched
transactions, cleared
items, adjustments, and

Page 12 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS BUSINESS PROCESS BUSINESS PROCESS PRE-CONDITION POST CONDITION
PROCESS ID NAME DESCRIPTION (INPUT) (OUTPUT)
investigation outcomes
and generate report
7.2.1 PROCESS/SUB-PROCESS DIAGRAM ADMINISTER VENDOR RECONCILIATION ACCOUNT INITIATION
7.2.1.1 PROCESS USER STORY ADMINISTER VENDOR ACCOUNT RECONCILIATION INITIATION
The Vendor Account Reconciliation Initiation process is the first step in ensuring that vendor accounts are accurate,
complete, and aligned with internal financial records and vendor statements. This process involves accessing SAP,
selecting vendor accounts, extracting Open Items Transaction validating transaction data and triggering the
reconciliation workflow.
7.2.1.2 PROCESS/SUB-PROCESS ACTIVITIES LISTING ADMINISTER VENDOR ACCOUNT INITIATION
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
BPR001
This activity involves accessing SAP to extract a list of
Extract Open Item
ACT001
all open items for selected vendor accounts
Transaction

Page 13 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
This activity involves requesting, accessing and
BRP001
downloading the vendor statement to ensure the
ACT002 Retrieve Vendor Statement
company has the most up-to-date and accurate
transaction information from the vendor
7.2.2 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS EXTRACT OPEN ITEMS TRANSACTION
Extract Open Item Transaction
ACTIVITY NAME
ACT001
ACTIVITY ID
The process entails retrieving of all outstanding vendor transactions from SAP to facilitate
BRIEF DESCRIPTION
accurate reconciliation
The system must allow extraction of all open vendor transactions including invoices, debit
ACTIVITY
notes and credit memos. Extraction should support filtering by vendor, date range,
REQUIREMENTS
transaction type, and status
BUSINESS PROCESS
NAME (PART OF) Administer Vendor Account Initiation
BUSINESS PROCESS
BPR001
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Only transactions that are unpaid or partially paid must be classified and
extracted as open items. Fully cleared transactions must be excluded from the
RUL001
extract.
SAP system must of record all open item transaction data used in vendor
BUSINESS RULES
RUL002
reconciliation.
Open item transactions may only be extracted for active vendor accounts
RUL003
Open item extraction must be performed using a defined cut-off date (e.g.,
RUL004
month-end). Transactions posted after the cut-off date must not be included
ROLE DETAIL
SAP001
ROLE ID
Systems, Applications, and Products in Data Processing
ROLE NAME
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their
status as open or cleared items. It supports end-to-end financial processes such as vendor
ROLE DESCRIPTION
account reconciliation, payment processing, financial reporting, and audit compliance.

Page 14 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Corporate Finance
BUSINESS AREA
Vendor invoices, credit notes, debit notes, and relevant payments have been correctly
PRECONDITION
posted in SAP
Payment terms and reconciliation account
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
User selects Open Items indicator SAP filters out cleared items and prepares
FLOW)
open items only
ALTERNATE FLOW OF No Open Items Found
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Extracted data in a usable format
All outstanding vendor transactions unpaid or partially paid are accurately retrieved from
CONCLUSION
SAP for review and reconciliation
7.2.3 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS RETRIEVE VENDOR STATEMENT
Retrieve Vendor Statement
ACTIVITY NAME
ACT002
ACTIVITY ID
This activity involves obtaining the vendor’s official account statement for a defined
BRIEF DESCRIPTION
period, through the SAP system.
The system must retrieve the vendor statement in a format that is readable and
ACTIVITY
REQUIREMENTS compatible with SAP
BUSINESS PROCESS
Administer Vendor Account Initiation
NAME (PART OF)
BUSINESS PROCESS
BPR001
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
The system must only retrieve vendor statements for active vendors with a
RUL001
valid vendor master record in SAP.
Vendor statements must be retrieved for the approved reconciliation period
RUL002
only.
The statement format must be readable and compatible with SAP and
BUSINESS RULES
RUL003
reconciliation tools (e.g. PDF, Excel, or system extract).
The system must validate completeness of the statement before it is used for
RUL004
reconciliation.
Access to retrieve vendor statements must be restricted to authorised users
RUL005
or system roles.
ROLE DETAIL

Page 15 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
ROLE ID SAP001
Systems, Applications, and Products in Data Processing
ROLE NAME
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their
status as open or cleared items. It supports end-to-end financial processes such as vendor
ROLE DESCRIPTION
account reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Relevant vendor transactions (invoices, credit notes, payments) must be posted in the
PRECONDITION
system, and transactions should be correctly recorded against the vendor account.
Vendor account details, including reconciliation account and payment terms
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
The Accounts Payable user initiates the The system accesses the defined source of
FLOW)
the vendor statement
Retrieve Vendor Statement activity as part
of the vendor reconciliation process
ALTERNATE FLOW OF The selected statement period is invalid, or the financial period is closed.
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT System-generated confirmation indicating successful retrieval of the vendor statement
The system successfully retrieves the vendor statement for the selected vendor and
CONCLUSION
period.
7.2.4 PROCESS/SUB-PROCESS DIAGRAM EXECUTE VENDOR ACCOUNT RECONCILIATION

Page 16 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
7.2.4.1 PROCESS USER STORY EXECUTE VENDOR ACCOUNT RECONCILIATION
The Execute Vendor Account Reconciliation process involves comparing the retrieved vendor statement with internal
open item transactions recorded on SAP. The process identifies matched and unmatched items, highlights
discrepancies, and enables investigation and resolution to ensure the vendor account balance is accurate and
complete.
7.2.4.2 PROCESS/SUB-PROCESS ACTIVITIES LISTING EXECUTE VENDOR ACCOUNT RECONCILIATION
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
This activity involves retrieving supporting
BPR002
documentation related to vendor transactions, such as
Retrieve Supporting
ACT001 invoices, credit notes, purchase orders, delivery notes,
Documentation
or payment confirmations, to validate and reconcile
vendor account balances.
This activity involves comparing the vendor account
BRP002
Compare Vendor Account statement against retrieved supporting documentation
ACT002 Statement Against so that all vendor transactions are validated,
Documentation discrepancies are identified, and vendor balances are
accurately reconciled in the system.
This activity involves automating generation of vendor BRP002
Generate Vendor Account
ACT003 account reconciliations by comparing vendor invoices
Reconciliation
and statements with internal financial records.
7.2.5 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS RETRIEVE SUPPORTING DOCUMENTATION
Retrieve Supporting Documentation
ACTIVITY NAME
ACT001
ACTIVITY ID
The process entails accessing and retrieving all relevant supporting documentation, such as
invoices, credit notes, purchase orders, delivery notes, or payment confirmations, required
BRIEF DESCRIPTION
to validate and reconcile vendor transactions.
The system must provide a mechanism to retrieve, view, and attach the document to the
ACTIVITY
REQUIREMENTS vendor reconciliation record
BUSINESS PROCESS
Execute Vendor Account Reconciliation
NAME (PART OF)
BUSINESS PROCESS
BPR002
ID

Page 17 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Supporting documentation retrieved must be linked to the corresponding
RUL001
vendor transaction and reconciliation record.
Retrieved documentation must include all required details: invoice number,
RUL002
date, amount, vendor details, and reference to the related transaction
BUSINESS RULES
Vendor account reconciliation cannot be completed without retrieving and
RUL003
validating all necessary supporting documents for the transactions
If a documentation is missing, incomplete, or corrupted, the issue must be
RUL004
flagged, and corrective action must be initiated
ROLE DETAIL
SAP001
ROLE ID
Systems, Applications, and Products in Data Processing
ROLE NAME
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their
status as open or cleared items. It supports end-to-end financial processes such as vendor
ROLE DESCRIPTION
account reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Vendor statement or transaction has been identified for reconciliation.
PRECONDITION
Vendor statement
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
User requests a supporting documentation Supporting documentation are retrieved
FLOW)
for a specific vendor transaction. from the system/repository and displayed
to the user.
ALTERNATE FLOW OF Retrieved documentation are unreadable or missing key information
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Retrieved supporting documentation linked to the transaction with confirmation of
successful retrieval.
Supporting documentation are retrieved and attached to the reconciliation record.
CONCLUSION
7.2.5.1 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS COMPARE VENDOR ACCOUNT STATEMENT AGAINST
DOCUMENTATION

Page 18 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Compare Vendor Account Statement Against Documentation
ACTIVITY NAME
ACT002
ACTIVITY ID
The process involves reviewing the vendor account statement against retrieved supporting
documentation such as invoices, credit notes, purchase orders, and payment records to
BRIEF DESCRIPTION
confirm accuracy and identify mismatches for the vendor account reconciliation process.
The system must automatically compare vendor statement entries against supporting
ACTIVITY
REQUIREMENTS documentation, identify and flag unmatched or mismatched transactions for investigation
BUSINESS PROCESS
Execute Vendor Account Reconciliation
NAME (PART OF)
BUSINESS PROCESS
BPR002
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
All discrepancies must be investigated and documented.
RUL001
BUSINESS RULES
Reconciliation cannot be finalised with unresolved material variances.
RUL002
All comparison activities must be auditable and retained per policy.
RUL003
ROLE DETAIL
ROLE ID SAP001
Systems, Applications, and Products in Data Processing
ROLE NAME
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their status
as open or cleared items. It supports end-to-end financial processes such as vendor account
ROLE DESCRIPTION
reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Supporting documentation have been retrieved and linked to transactions.
PRECONDITION
Vendor account statement, Supporting documentation and Open item transaction data
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
System automatically matches transactions Unmatched items are flagged for
FLOW)
based on defined rules. investigation.
ALTERNATE FLOW OF System errors preventing comparison.
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Reconciled transactions and Discrepancy and exception list
Transactions are reconciled and flagged for investigation
CONCLUSION

Page 19 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
7.2.6 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS GENERATE VENDOR ACCOUNT RECONCILIATION
Generate Vendor Account Reconciliation
ACTIVITY NAME
ACT003
ACTIVITY ID
The process involves automatically produces vendor account reconciliations by matching
vendor invoices and statements with internal records, identifying matched items and
BRIEF DESCRIPTION
exceptions for review.
The system must automatically generate vendor account reconciliations using vendor
ACTIVITY
REQUIREMENTS invoices and statements received via the real-time interface.
BUSINESS PROCESS
Generate Vendor Account Reconciliation
NAME (PART OF)
BUSINESS PROCESS
BPR002
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Vendor invoices and statements must be successfully received and validated
RUL001
before reconciliation is performed.
Reconciliation must be executed per vendor, per account, and for a defined
RUL002
accounting period.
Matching must be performed using predefined criteria (e.g. invoice number,
BUSINESS RULES
RUL003
amount, date, purchase order, and vendor reference).
Transactions that meet matching criteria must be automatically marked as
RUL004
reconciled.
Transactions that do not meet matching criteria must be classified as
RUL005
exceptions.
ROLE DETAIL
ROLE ID SAP001
Systems, Applications, and Products in Data Processing
ROLE NAME
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their status
as open or cleared items. It supports end-to-end financial processes such as vendor account
ROLE DESCRIPTION
reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Vendor invoices and statements must be received and available in the system.
PRECONDITION
Internal vendor account transactions and open items from SAP
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
System generates reconciliation report A detailed vendor account reconciliation
FLOW)
report is produced, showing reconciled
items, open items, and exceptions.

Page 20 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
ALTERNATE FLOW OF Transactions that cannot be matched automatically due to discrepancies (amount, date, or
ACTIVITIES (NEGATIVE
reference mismatch) are flagged as exceptions.
FLOW)
OUTPUT Reconciliation report with:
Matched transactions (reconciled items)
Unmatched transactions (exceptions requiring manual review)
The automated vendor account reconciliation generated
CONCLUSION
7.2.7 PROCESS/SUB-PROCESS DIAGRAM EXECUTE VENDOR ACCOUNT RECONCILIATION VERIFICATION
7.2.7.1 PROCESS USER STORY PERFORM VENDOR ACCOUNT RECONCILIATION VERIFICATION
The Perform Vendor Account Reconciliation Verification this process involves verifying the accuracy and
completeness of vendor account reconciliations by reviewing reconciled and unreconciled items, validating
supporting documentation to confirm that reconciliation outcomes comply with standard operational procedure
and accounting standard.
7.2.7.2 PROCESS/SUB-PROCESS ACTIVITIES LISTING PERFORM VENDOR ACCOUNT RECONCILIATION VERIFICATION

Page 21 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
This activity ensures that financial records accurately reflect
Initiate Correction known errors, timing differences, or unresolved disputes BPR003
ACT001
Reserve Entry while investigations are in progress, in line with accounting
policies and control requirements
This activity ensures that timing differences are clearly
Document Payment in
ACT002 explained, supported by valid documentation, and accurately BRP003
Transit
reflected in the vendor reconciliation process.
This activity ensures that timing differences are resolved within BRP003
Monitor Payment in
ACT003 an acceptable period and that outstanding payments do not
Transit
indicate processing errors, failed payments, or potential fraud.
7.2.8 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS INITIATE CORRECTION RESERVE ENTRY
Initiate Correction Reserve Entry
ACTIVITY NAME
ACT001
ACTIVITY ID
The process involves initiating a temporary accounting reserve entry to correct identified
discrepancies during vendor account reconciliation, ensuring that vendor balances and
BRIEF DESCRIPTION
financial records remain accurate while outstanding issues are investigated and resolved.
The reserve entry is processed in the financial system (e.g. SAP) using approved reserve or
ACTIVITY
REQUIREMENTS provision accounts.
BUSINESS PROCESS
Perform Vendor Account Reconciliation Verification
NAME (PART OF)
BUSINESS PROCESS
BPR003
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Correction reserve entries may only be initiated for discrepancies identified
RUL001
through an approved vendor reconciliation or verification process.
Reserve entries must comply with approved accounting standards, standard
RUL002
operational procedure and materiality thresholds.
BUSINESS RULES
All correction reserve entries require documented justification and supporting
RUL003
evidence.
Reserve entries must be reviewed and approved by an authorized finance
RUL004
approver before posting
ROLE DETAIL

Page 22 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
FIN001
ROLE ID
Financial Officer
ROLE NAME
A Financial Officer is a professional responsible for performing account reconciliations,
preparing, managing, and reporting an organization’s financial information in line with
ROLE DESCRIPTION
accounting standards.
Corporate Finance
BUSINESS AREA
Discrepancy or unreconciled item has been identified
PRECONDITION
Vendor Account Reconciliation Report
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Financial Accountant identifies an Financial Accountant initiates the
FLOW)
unreconciled item during vendor account correction reserve journal entry in the SAP
reconciliation.
ALTERNATE FLOW OF During review, the discrepancy is found to be unsupported or incorrect.
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Discrepancy amount reserved or adjusted in the general ledger.
No reserve entry is initiated; item is returned for further investigation
CONCLUSION
7.2.9 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS DOCUMENT PAYMENT IN TRANSIT
Document Payment in Transit
ACTIVITY NAME
ACT002
ACTIVITY ID
The process involves recording and tracking vendor payments that have been initiated and
recorded but have not yet been reflected on the vendor statement or cleared by the bank at
BRIEF DESCRIPTION
the reconciliation date.
Payment has been processed and recorded in the SAP and Payment is not yet cleared in the
ACTIVITY
REQUIREMENTS bank or vendor statement.
BUSINESS PROCESS
Perform Vendor Account Reconciliation Verification
NAME (PART OF)
BUSINESS PROCESS
BPR003
ID
RISK SENSITIVITY Medium
INDEX
RULE ID DETAIL
Only payments that have been successfully posted in the SAP system but are not
BUSINESS RULES
yet reflected on the bank or vendor statement may be classified as Payment in
RUL001
Transit

Page 23 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Payment in Transit must be supported by valid documentation
RUL002
Payments classified as in transit must relate to transactions initiated before the
RUL003
reconciliation cut-off date.
ROLE DETAIL
ROLE ID FIN001
Financial Officer
ROLE NAME
A Financial Officer is a professional responsible for performing account reconciliations,
preparing, managing, and reporting an organization’s financial information in line with
ROLE DESCRIPTION
accounting standards.
Corporate Finance
BUSINESS AREA
FIN001
PRECONDITION
Financial Officer
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Finance Officer identifies a vendor payment System displays unmatched payment item
FLOW)
not yet reflected on the vendor statement
during reconciliation.
ALTERNATE FLOW OF Duplicate Payment in Transit detected.
ACTIVITIES (NEGATIVE
System must block duplication and displays error message
FLOW)
OUTPUT Payment successfully classified as Payment in Transit
Valid vendor payments which have been initiated but not yet reflected on vendor or bank
CONCLUSION statements are accurately identified, documented, and monitored during the reconciliation
process.
7.2.9.1 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS MONITOR PAYMENT IN TRANSIT
Monitor Payment in Transit
ACTIVITY NAME
ACT003
ACTIVITY ID
The process involves verifying the accuracy and completeness of vendor account balances by
BRIEF
DESCRIPTION comparing the records with vendor statements and supporting documentation.
ACTIVITY
Vendor account balances and transactions are extracted from SAP system
REQUIREMENTS
BUSINESS
Perform Vendor Account Reconciliation Verification
PROCESS NAME
(PART OF)
BUSINESS
BPR003
PROCESS ID
RISK SENSITIVITY
Medium
INDEX
BUSINESS RULES RULE ID DETAIL

Page 24 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
All the transactions included in the reconciliation must have valid supporting
RUL001
documentation
Any differences between SAP balances and vendor statements must be recorded
RUL002
Transactions must be matched line by line with vendor statements to ensure no
RUL003
overpayment, duplicate posting, or unrecorded item exists.
All unreconciled or exception items must be documented and escalated according
to Standard Operational Procedure
RUL004
ROLE DETAIL
ROLE ID FIN001
Financial Officer
ROLE NAME
A Financial Officer is a professional responsible for performing account reconciliations,
ROLE
preparing, managing, and reporting an organization’s financial information in line with
DESCRIPTION
accounting standards.
Corporate Finance
BUSINESS AREA
Vendor statements and supporting documentation (invoices, payment confirmations, credit
PRECONDITION
notes) are available.
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES
Compare SAP and vendor statement
(POSITIVE FLOW)
Compare SAP and vendor statement
System identifies matched and unmatched items
ALTERNATE FLOW Access denied; process escalated for unauthorised user attempts verification
OF ACTIVITIES
(NEGATIVE FLOW)
OUTPUT Verified reconciliation report showing matched and unmatched items
Accurate reconciliation verification enables ensures vendor balances reflect the true financial
CONCLUSION
position of SARS.

Page 25 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
7.2.10 PROCESS/SUB-PROCESS DIAGRAM ADMINISTER VENDOR ACCOUNT RECONCILIATION INVESTIGATION
7.2.11 PROCESS USER STORY ADMINISTER VENDOR ACCOUNT RECONCILIATION INVESTIGATION
This process Administer Vendor Account Reconciliation Investigation involves investigating discrepancies identified
during the vendor account reconciliation. It ensures that all exceptions, timing differences, or errors are analysed,
validated, and resolved in accordance with accounting policies and standard operational procedure.
7.2.11.1 PROCESS/SUB-PROCESS ACTIVITIES LISTING PERFORM VENDOR ACCOUNT RECONCILIATION VERIFICATION
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
This activity involves requesting an updated or
corrected vendor statement when a payment in transit BPR004
ACT001 Request Correct Statement
has been identified during vendor account
reconciliation.
This activity involves reviewing and comparing
supporting documentation against SAP system records BRP004
Investigate Match
ACT002 and vendor statements to verify the accuracy and
Documentation
validity of matched or disputed transactions identified
during vendor account reconciliation.

Page 26 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
7.2.12 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS REQUEST CORRECT STATEMENT
Request Correct Statement
ACTIVITY NAME
ACT001
ACTIVITY ID
Request Correct Statement is the activity of formally contacting the vendor to obtain an
updated or corrected vendor statement when a validated payment in transit has been
BRIEF DESCRIPTION
identified during vendor account reconciliation.
ACTIVITY
System must identify and validate payment in transit during vendor account reconciliation.
REQUIREMENTS
BUSINESS PROCESS
Administer Vendor Account Reconciliation Investigation
NAME (PART OF)
BUSINESS PROCESS
BPR004
ID
RISK SENSITIVITY
Low
INDEX
RULE ID DETAIL
A corrected statement may only be requested when a Payment in Transit has
been validated as correctly posted on SAP but not reflected on the vendor
RUL001
statement.
BUSINESS RULES
Upon receipt, the corrected vendor statement must be reviewed to confirm the
RUL002
payment is accurately reflected.
Once the corrected statement is verified, the Payment in Transit must be
RUL003
cleared during the next reconciliation cycle.
ROLE DETAIL
FIN001
ROLE ID
Financial Officer
ROLE NAME
A Financial Officer is a professional responsible for performing account reconciliations,
preparing, managing, and reporting an organization’s financial information in line with
ROLE DESCRIPTION
accounting standards.
Corporate Finance
BUSINESS AREA
A Payment in Transit has been identified and validated internally
PRECONDITION
Vendor statement (showing missing payment)
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Identify a payment in transit during vendor Item flagged during reconciliation
FLOW)
reconciliation.
ALTERNATE FLOW OF Vendor not responding within agreed timeframe, follow-up request sent; escalate if
ACTIVITIES (NEGATIVE
necessary.
FLOW)
OUTPUT Corrected or updated vendor statement received

Page 27 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
The vendor statements requested accurately reflect validated payments in transit, enabling
CONCLUSION
correct and timely vendor account reconciliation.
7.2.13 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS INVESTIGATE MATCH DOCUMENTATION
Investigate Match Documentation
ACTIVITY NAME
ACT002
ACTIVITY ID
This activity involves confirming valid matches, identifying errors or omissions, and
BRIEF DESCRIPTION
determine the appropriate resolution for discrepancies.
ACTIVITY
Vendor account reconciliation has identified matched or disputed items
REQUIREMENTS
BUSINESS PROCESS
Administer Vendor Account Reconciliation Investigation
NAME (PART OF)
BUSINESS PROCESS
BPR004
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
All transactions under investigation must be supported by valid documentation.
RUL001
Each SAP transaction must correspond to a single supporting documentation
BUSINESS RULES RUL002
The details (amount, date, vendor, reference number) must match across SAP
RUL003
records and supporting documents.
ROLE DETAIL
ROLE ID FIN001
Financial Officer
ROLE NAME
A Financial Officer is a professional responsible for performing account reconciliations,
preparing, managing, and reporting an organization’s financial information in line with
ROLE DESCRIPTION
accounting standards.
Corporate Finance
BUSINESS AREA
FIN001
PRECONDITION
Financial Officer
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Select transaction for investigation Transaction details displayed
FLOW)
ALTERNATE FLOW OF Mismatch identified
ACTIVITIES (NEGATIVE
• Amounts, dates, or references do not match.
FLOW)
• Item flagged for correction or further investigation
OUTPUT Verified and documented investigation results

Page 28 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Vendor transactions are validated against supporting documentation, confirming the
CONCLUSION
accuracy and legitimacy of reconciled or disputed items.
7.2.14 PROCESS/SUB-PROCESS DIAGRAM COORDINATE VENDOR ACCOUNT RECONCILIATION REVIEW
7.2.14.1 PROCESS USER STORY COORDINATE VENDOR ACCOUNT RECONCILIATION REVIEW
This process Coordinate Vendor Account Reconciliation Review involves overseeing and managing the review of
vendor account reconciliation reports to ensure accuracy, completeness, and compliance with the standard
operational procedure and accounting standard.
7.2.14.2 PROCESS/SUB-PROCESS ACTIVITIES LISTING COORDINATE VENDOR ACCOUNT RECONCILIATION REVIEW
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
The Review Vendor Reconciliation Adjustment activity
Review Vendor Reconciliation involves examining adjustments to the vendor BPR005
ACT001
Adjustment reconciliation report to ensure they are accurate,
justified, and compliant with accounting standard.
The Post Reconciliation Adjustment activity involves
Post Reconciliation
ACT002 recording and applying approved adjustments to the BRP005
Adjustment
vendor reconciliation report
Approve Vendor Account Approve Vendor Account Reconciliation activity involves BRP005
ACT003
Reconciliation validating and authorising the vendor account

Page 29 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION
PROCESS ID
reconciliation after all reviews and adjustments have
been completed.
7.2.15 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS REVIEW VENDOR RECONCILIATION ADJUSTMENT
Review Vendor Reconciliation Adjustment
ACTIVITY NAME
ACT001
ACTIVITY ID
Review Vendor Reconciliation Adjustment activity involves reviewing proposed adjustments
to the vendor reconciliation report to ensure accuracy, completeness, and compliance with
BRIEF DESCRIPTION
financial policies before approval and implementation.
ACTIVITY
Workflow approval for adjustments is generated
REQUIREMENTS
BUSINESS PROCESS
Coordinate Vendor Account Reconciliation Review
NAME (PART OF)
BUSINESS PROCESS
BPR004
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Only authorized Finance Managers reviewers may approve reconciliation
RUL001
adjustments.
BUSINESS RULES
All adjustments must be supported with appropriate documentation.
RUL002
Adjustments must comply with accounting standard.
RUL003
No adjustment may be applied without workflow approval.
RUL004
ROLE DETAIL
FIM001
ROLE ID
Financial Manager
ROLE NAME
The Finance Manager is the authorised reviewer responsible for receiving the workflow
ROLE DESCRIPTION
approval request and approving the vendor reconciliation report.
Corporate Finance
BUSINESS AREA
Workflow approval request for adjustment review has been generated.
PRECONDITION
Vendor reconciliation report with proposed adjustments
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Receive workflow approval request to review Approve adjustments via the workflow
FLOW)
adjustments system
ALTERNATE FLOW OF Reject the proposed adjustments in the workflow system and provide detailed feedback
ACTIVITIES (NEGATIVE
FLOW)

Page 30 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
OUTPUT Updated vendor reconciliation report reflecting approved adjustments
Adjustment to vendor accounts is accurate, justified, and compliant with Standard Operating
CONCLUSION
Procedure and Accounting Standard
7.2.15.1 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS POST RECONCILIATION ADJUSTMENT
Post Reconciliation Adjustment
ACTIVITY NAME
ACT002
ACTIVITY ID
This activity involves posting and recording all approved adjustments to the vendor
reconciliation report in the SAP, ensuring accurate vendor balances and compliance with
BRIEF DESCRIPTION
Accounting Standard.
Approved reconciliation adjustments are available and supporting documentation for
ACTIVITY
REQUIREMENTS adjustments are complete.
BUSINESS PROCESS
Coordinate Vendor Account Reconciliation Review
NAME (PART OF)
BUSINESS PROCESS
BPR004
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Only authorised Finance Manager may post reconciliation adjustments.
RUL001
All posted adjustments must have been approval and supporting documentation
BUSINESS RULES RUL002
Adjustments must be accurately reflected in both the vendor accounts and the
RUL003
general ledger
ROLE DETAIL
ROLE ID FIM001
Financial Manager
ROLE NAME
The Finance Manager is the authorized reviewer responsible for receiving the workflow
ROLE DESCRIPTION
approval request and approving the vendor reconciliation report
Corporate Finance
BUSINESS AREA
Adjustments have been approved through the workflow system.
PRECONDITION
Approved vendor reconciliation adjustments
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Retrieve the approved reconciliation Post each approved adjustment to the
FLOW)
adjustments and supporting documentation vendor accounts and general ledger
ALTERNATE FLOW OF Post approved adjustments and have system errors or incorrect data
ACTIVITIES (NEGATIVE
FLOW)

Page 31 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
OUTPUT Vendor accounts and general ledger updated with adjustments
CONCLUSION Approved adjustments are accurately reflected in vendor accounts and the general ledger
7.2.16 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS APPROVE VENDOR ACCOUNT RECONCILIATION
Approve Vendor Account Reconciliation
ACTIVITY NAME
ACT003
ACTIVITY ID
This activity involves approving the vendor account reconciliation after all reviews,
BRIEF DESCRIPTION
adjustments, and postings have been completed.
Vendor reconciliation report has been reviewed and verified, and adjustments have been
ACTIVITY
REQUIREMENTS posted and reflected in the report.
BUSINESS PROCESS
Coordinate Vendor Account Reconciliation Review
NAME (PART OF)
BUSINESS PROCESS
BPR004
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Only authorised Finance Managers approvers may approve the reconciliation.
RUL001
Approval may be allowed when all discrepancies are resolved, and all
BUSINESS RULES RUL002
adjustments are posted.
The approved vendor account reconciliation must reconcile with vendor
RUL003
statements and the general ledger.
ROLE DETAIL
ROLE ID FIM001
Financial Manager
ROLE NAME
The Finance Manager is the authorized reviewer responsible for receiving the workflow
ROLE DESCRIPTION
approval request and approving the vendor reconciliation report
Corporate Finance
BUSINESS AREA
Vendor reconciliation Account has been reviewed, adjusted, and posted
PRECONDITION
Workflow approval notification
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Receive workflow approval request for final Approve the vendor reconciliation account
FLOW)
approval in the workflow/system
ALTERNATE FLOW OF Access the reconciliation account and identify unresolved discrepancies
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Recorded approval in the workflow/system for audit purposes

Page 32 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Vendor balances, adjustments, and supporting documentation are accurate, complete, and
CONCLUSION
compliant with accounting standard
7.2.17 PROCESS/SUB-PROCESS DIAGRAM ADMINISTER VENDOR ACCOUNT RECONCILIATION REPORTING
7.2.18 PROCESS USER STORY ADMINISTER VENDOR ACCOUNT RECONCILIATION REPORTING
This process Administer Vendor Account Reconciliation Reporting ensure that the outcomes of vendor account
reconciliations are accurately compiled, reviewed, approved, and reported to management, it also provides visibility
of reconciled balances, outstanding variances, and risk exposures to support financial control and compliance.
7.2.19 PROCESS/SUB-PROCESS ACTIVITIES LISTING ADMINISTER VENDOR ACCOUNT RECONCILIATION REPORTING
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION PROCESS
ID
Generate Vendor Reconciliation Report activity involves
Generate Vendor generating a consolidated reconciliation report that reflects the BPR006
ACT001
Reconciliation Report reconciliation status of vendor accounts for a specific reporting
period.
Submit Vendor Submit Vendor Reconciliation Report activity involves formally
ACT002
Reconciliation Report submitting the completed vendor reconciliation report to the BRP006

Page 33 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
BUSINESS
ACTIVITY ID ACTIVITY NAME ACTIVITY DESCRIPTION PROCESS
ID
Finance Manager stakeholders for review, approval and
distribution
Review Vendor Reconciliation Report activity involves examining BRP006
Review Vendor the completed vendor reconciliation report to ensure accuracy,
ACT003
Reconciliation Report completeness, and compliance with Standard Operating
Procedures and accounting standards.
7.2.19.1 PROCESS/SUB-PROCESS ACTIVITY GENERATE VENDOR RECONCILIATION REPORT
Generate Vendor Reconciliation Report
ACTIVITY NAME
ACT001
ACTIVITY ID
This activity involves compiling and producing a consolidated reconciliation report that
reflects the reconciliation status of vendor accounts for a defined reporting period,
BRIEF DESCRIPTION
highlighting reconciled balances, outstanding items, and variances.
The system must extract reconciled and unreconciled vendor account data for the selected
ACTIVITY
reporting period and consolidate reconsolidate reconciliation report with balances per
REQUIREMENTS
vendor and in total
BUSINESS PROCESS
Administer Vendor Account Reconciliation Reporting
NAME (PART OF)
BUSINESS PROCESS
BPR006
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Vendor reconciliation reports must be generated for each defined reporting
RUL001
period in line with the financial close calendar.
All report balances must reconcile to the Accounts Payable sub-ledger and the
RUL002
General Ledger.
BUSINESS RULES
Material unreconciled items must be identified, explained, and flagged for
RUL003
management review
Reports must be reviewed and approved before final distribution.
RUL004
Generate reconciliation reports per vendor and company code
RUL005
Flag unmatched items for manual review
RUL006
ROLE DETAIL
SAP001
ROLE ID
Systems, Applications, and Products in Data Processing
ROLE NAME

Page 34 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their
status as open or cleared items. It supports end-to-end financial processes such as vendor
ROLE DESCRIPTION
account reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Vendor account reconciliations have been completed.
PRECONDITION
Approved Vendor Account Reconciliation
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Generate vendor reconciliation report Validate report totals against GL
FLOW)
ALTERNATE FLOW OF Report generation delayed
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Vendor Reconciliation Report (draft)
Generate Vendor Reconciliation Report to ensures accurate, timely, and auditable reporting
CONCLUSION
of vendor reconciliation outcomes
7.2.19.2 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS SUBMIT VENDOR RECONCILIATION REPORT
Submit Vendor Reconciliation Report
ACTIVITY NAME
ACT002
ACTIVITY ID
This activity involves formally submitting the completed vendor reconciliation report to the
Finance Manager for review and approval, ensuring timely communication of reconciliation
BRIEF DESCRIPTION
results, exceptions, and variances for financial control and compliance purposes.
The Vendor Reconciliation Report is accurate, with all reconciled and unreconciled items
ACTIVITY
REQUIREMENTS properly documented
BUSINESS PROCESS
Administer Vendor Account Reconciliation Reporting
NAME (PART OF)
BUSINESS PROCESS
BPR006
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
Reports must be submitted only after validation against the General Ledger and
RUL001
supporting documentation.
Any changes post-submission must formally be approved on the workflow and
BUSINESS RULES
RUL002
documented.
The reviewer must receive and act on the workflow approval request before
RUL003
approving the vendor reconciliation report.
ROLE DETAIL
ROLE ID SAP001
Systems, Applications, and Products in Data Processing
ROLE NAME

Page 35 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
SAP records vendor invoices, payments, credit notes, and debit notes, and tracks their status
as open or cleared items. It supports end-to-end financial processes such as vendor account
ROLE DESCRIPTION
reconciliation, payment processing, financial reporting, and audit compliance.
Corporate Finance
BUSINESS AREA
Vendor Reconciliation Report has been generated and validated.
PRECONDITION
Completed Vendor Reconciliation Report
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Submit the report to designated Report is received by reviewers
FLOW)
management or finance stakeholders
ALTERNATE FLOW OF Stakeholders do not acknowledge receipt
ACTIVITIES (NEGATIVE
FLOW)
OUTPUT Submitted Vendor Reconciliation Report
CONCLUSION Vendor Reconciliation Report successfully submitted
7.2.19.3 PROCESS/SUB-PROCESS ACTIVITY REQUIREMENTS REVIEW VENDOR RECONCILIATION REPORT
Review Vendor Reconciliation Report
ACTIVITY NAME
ACT003
ACTIVITY ID
This activity involves reviewing the vendor reconciliation report to confirm accuracy,
BRIEF DESCRIPTION
completeness, and compliance with financial policies before approval or submission.
ACTIVITY
Vendor statements and supporting documents are attached and accessible
REQUIREMENTS
BUSINESS PROCESS
Administer Vendor Account Reconciliation Reporting
NAME (PART OF)
BUSINESS PROCESS
BPR006
ID
RISK SENSITIVITY
Medium
INDEX
RULE ID DETAIL
The vendor reconciliation report must be reviewed by an authorised and
RUL001
independent reviewer
Vendor balances must agree with the general ledger extract and vendor
BUSINESS RULES RUL002
statements
No reconciliation may be approved without required evidence and explanations
RUL003
All unreconciled items must have valid explanations and supporting
RUL004
documentation.
ROLE DETAIL
ROLE ID FIM001
Finance Manager
ROLE NAME

Page 36 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
The Finance Manager is the authorized reviewer responsible for receiving the workflow
ROLE DESCRIPTION
approval request and approving the vendor reconciliation report.
Corporate Finance
BUSINESS AREA
The workflow approval request has been generated and sent to the Finance Manager
PRECONDITION
Completed vendor reconciliation report
INPUT
TYPICAL FLOW OF ACTION RESPONSE
ACTIVITIES (POSITIVE
Receive Workflow Approval – The Finance Access Reconciliation Report –Open the
FLOW)
Manager receives the workflow approval submitted vendor reconciliation report with
request to review the vendor reconciliation all supporting documents
report.
ALTERNATE FLOW OF Return for Correction – Reject the report in the workflow system and provide detailed
ACTIVITIES (NEGATIVE
feedback to the preparer for correction.
FLOW)
OUTPUT Approved vendor reconciliation report if all items are accurate and complete
Finance Manager confirms accuracy, completeness, and compliance with financial policies,
CONCLUSION approves the report for submission, and maintains proper records for audit and compliance
purposes.
7.3 SUPPORTING DOCUMENT REQUIREMENTS
Supporting
Activity
Document Supporting Document Name Activity Name
ID
ID
SD001 Approved reconciliation adjustments ACT002 Post Reconciliation Adjustment
SD002 Bank statements ACT002 Document Payment in Transit
Correspondence related to discrepancies or disputes Compare Vendor Account
SD003 ACT002 Statement Against
Documentation
SD004 Credit notes ACT003 Monitor Payment in Transit
Delivery Note Retrieve Supporting
SD005 ACT001
Documentation
General ledger extracts Review Vendor Reconciliation
SD006 ACT003
Report
SD007 Invoices ACT001 Extract Open Item Transaction
SD008 Payment confirmations / proof of payment ACT001 Retrieve Vendor Statement

Page 37 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
Purchase Order Retrieve Supporting
SD009 ACT001
Documentation
SD010 Vendor statements ACT001 Retrieve Vendor Statement
8 REPORTING REQUIREMENTS
8.1 REPORT LISTING
REPORT REPORT TARGET DISTRIBUTION
REPORT NAME REPORT DESCRIPTION /PURPOSE
ID FREQUENCY AUDIENCE FORMAT
The system must keep audit trials of all
permission and authorisation changes made
to objects, indicating responsibility, action
type, date, and time
Audit output must link each reconciliation
Vendor record back to its SAP FI/MM/SD source
REP00 Reconciliation transaction. Email
Monthly Manager
1 Audit Trail Audit status must display as "Verified" once Notification
Report reconciliation lineage is complete.
Audit output must link each reconciliation
record back to its SAP FI/MM/SD source
transaction.
Audit status must display as "Verified" once
reconciliation lineage is complete.
The purpose of this report to identify
unreconciled items, discrepancies, and
variances arising from the reconciliation of
general ledger accounts, sub-ledgers, bank
statements, or vendor/customer
Vendor
statements. The system must detect
REP00 Reconciliation Finance Email
discrepancies in real time, including: Weekly
2 Exception Manager Notification
• Missing goods receipts
Report
• Variances correct pricing
The system must flag issues before month-
end close.
Alerts must be delivered through
dashboards and notifications

Page 38 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
REPORT REPORT TARGET DISTRIBUTION
REPORT NAME REPORT DESCRIPTION /PURPOSE
ID FREQUENCY AUDIENCE FORMAT
Vendor
The purpose of this report is to detail
REP00 Reconciliation Finance Email
reconciled items, open items, and Monthly
3 Report Manager Notification
exceptions
Vendor The purpose of this report is to identify and
REP00 Reconciliation list outstanding transactions that remain Finance Email
Monthly
4 Open Items unresolved, unpaid, or unmatched as at a Team Notification
Report specific reporting date
9 NON-FUNCTIONAL REQUIREMENTS
9.1 DEPLOYMENT MODEL
a) The proposed solution must support a Hybrid deployment model, whereby the solution may be cloud-
hosted and/or deployed within a private cloud environment while integrating with SARS's on-premise SAP
environment.
b) The proposed solution must integrate with SAP, which will remain the system of record for vendor,
financial, and reconciliation-related data.
c) The Service Provider must clearly describe the proposed deployment architecture, integration approach,
and any dependencies required for the successful implementation and operation of the solution.
d) The proposed solution must be capable of securely exchanging data and interacting with SAP and any other
authorised SARS systems required for the vendor reconciliation process.
e) Note: The solution is expected to be deployed on the SARS MS (Microsoft Azure) cloud tenant. Other
components may be deployed on SARS on-prem data centre. Therefore, we expect the infrastructure costs
to be covered by SARS
9.2 PLATFORM END-TO-END SOLUTION
a) The solution must provide a single, integrated platform for Vendor Reconciliation Automation that supports
vendor and general ledger reconciliation processes, including data ingestion, automated matching,
exception handling, workflow approvals, reporting, dashboards, audit trails, and SAP integration through a
common user interface and administration framework.
b) The platform should eliminate the need for multiple standalone tools, spreadsheets, or separate
reconciliation applications.
9.3 INTEGRATION WITH SAP
a) Compatible with and/or housed in SAP.
b) Secure storage and encrypted audit logs.
c) Role-based access controls for adjustments.
d) SAP ECC 6.0 and/or SAP S/4HANA compatibility.
e) Integration with SAP modules, including Financial Accounting (FI), Materials Management (MM), and
Accounts Payable (AP).
f) Use of IDocs, BAPIs, SAP PI/PO, REST APIs, SOAP services, Enterprise Service Bus (ESB) technologies, or
equivalent integration mechanisms for interfacing.

Page 39 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
g) Support for industry-standard data and message formats, including XML, JSON, EDI, or equivalent
standards.
h) Support for secure large-volume data and file transfers.
i) Email integration for statement ingestion.
j) OCR capability for scanned documents.
9.4 DATA RESIDENCY AND COMPLIANCE
a) The Service Provider must ensure that any data generated, processed, stored, backed up, or replicated by
the solution outside SARS environments resides within data centres located in the Republic of South Africa
and complies with applicable South African legislation, including POPIA, as well as SARS information
security and data governance requirements.
9.5 SECURITY REQUIREMENTS
The solution must provide security controls that support the protection of sensitive financial and vendor data
and align with SARS information security requirements, including but not limited to:
a) User access control, including support for authentication and authorization mechanisms.
b) Role-Based Access Control (RBAC).
c) Segregation of Duties (SoD).
d) Multi-Factor Authentication (MFA).
e) Support for Single Sign-On (SSO), where applicable.
f) Encryption of data at rest and in transit.
g) Audit logging and traceability of user activities, reconciliation activities, workflow actions, and system
changes.
h) Secure administration and management of user accounts, roles, permissions, and access rights.
i) Secure storage and protection of reconciliation records, supporting documentation, and audit trails.
j) Accountability, non-repudiation, and traceability through comprehensive audit trails and logging
mechanisms.
k) Support for SARS information security, access management, and data protection requirements.
9.6 REGULATORY COMPLIANCE
Compliance includes but is not limited to:
a) International Financial Reporting Standards (IFRS) and internal audit requirements.
b) The Public Finance Management Act (PFMA) and applicable National Treasury Regulations, Instructions,
and Circulars, where relevant to financial management, record keeping, auditability, and reporting.
c) The Protection of Personal Information Act (POPIA) and applicable data protection requirements.
d) Applicable SARS information security, ICT governance, and cybersecurity requirements.
e) Applicable statutory, regulatory, audit, and record-retention requirements.
f) Applicable National Treasury and financial governance requirements relevant to financial reporting,
auditability, and reconciliation processes.
9.7 SYSTEM REQUIREMENTS
a) Handle high-volume vendor reconciliation transactions efficiently.
b) Process and reconcile high volumes of financial, vendor, supplier statement, and invoice data.
c) Support real-time or near-real-time discrepancy detection and exception identification.

Page 40 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
d) Support automated matching and reconciliation of vendor statements against SAP vendor balances
and transactions.
e) Accommodate multiple vendor reconciliation scenarios, including trade vendors, municipalities,
utilities, and other vendor categories.
f) Maintain performance, stability, and data integrity during peak processing periods and high-volume
reconciliation activities.
9.8 LANGUAGE REQUIREMENTS
a) The solution and related materials are required to be provided in English.
9.9 MAINTENANCE AND SUPPORT SERVICES
a) SARS will require maintenance and support services for the Vendor Reconciliation Automation Solution
following implementation for a period of three (3) years.
b) Maintenance and support services must be provided in accordance with an agreed Service Level Agreement
(SLA).
c) The Service Provider must provide:
1 Solution support and incident management services.
2 Software updates, upgrades, security patches, and defect resolution.
3 Maintenance of system configurations, reconciliation rules, and workflow configurations where
applicable.
4 A helpdesk and support service for authorised SARS users.
5 A dedicated support team and account manager.
6 Access to a knowledge base and support documentation.
7 Regulatory, security, and compliance-related updates required to maintain the solution.
8 Functional enhancements and updates to support evolving reconciliation and business requirements.
9 Service availability and performance commitments as agreed in the SLA.
10 Planned maintenance notifications provided in advance and preferably scheduled outside normal
business hours.
9.10 TRAINING AND KNOWLWDGE TRANSFER
a) The Service Provider must be available to provide training on the operation, administration, and
maintenance of the solution, including:
1 Super User (Administrator) Training – 10 users. Training must be tailored for administrators and
technical support personnel responsible for solution configuration, maintenance, monitoring, and user
administration.
2 End-User Training – 14 users. Training must be tailored for business users responsible for performing
vendor reconciliation activities and day-to-day operation of the solution.
3 Tailored Training Programmes- The Service Provider must design and deliver role-based training
programmes to ensure that different user groups receive relevant practical instruction aligned to their
responsibilities. Training must be available through a combination of classroom, virtual, and self-
service formats, including user manuals, online documentation, and video tutorials.
4 Train-the-Trainer Approach- The Service Provider must provide a hybrid train-the-trainer programme
comprising both in-person and virtual training sessions. An initial group of Super Users and End Users
will be trained and will subsequently deliver training to approximately 76 users nationally. The user
numbers specified above represent the initial estimated training requirement and may be refined

Page 41 of 41
Business Requirements Specification (BRS)
RFI 01/2026- The Provision of a Vendor Reconciliation Automation Solution, Including Maintenance and Support for a Period of
Three (3) Years.
during implementation planning. The Service Provider must be able to accommodate additional users
and provide further training and knowledge transfer services as required by SARS.
b) The Service Provider must provide training on new features, enhancements, updates, and releases of the
solution.
c) The Service Provider must conduct knowledge transfer and provide a sustainability plan to enable SARS to
independently administer, support, and maintain the solution.
d) The Service Provider must implement change management and user adoption activities to facilitate the
successful transition and utilisation of the solution across SARS.
9.11 LICENSING, SUBSCRIPTION AND ONCE OFF COSTS (PACKAGES)
a) The Service Provider must ensure that the proposed pricing structure is comprehensive, transparent, and
supported by a detailed cost breakdown.
b) The Service Provider is required to provide a subscription-based pricing model
c) The Service Provider must submit pricing in accordance with the Pricing Template provided by SARS.
d) The Service Provider must clearly distinguish between Once-off cost, Recurring costs, Annual support and
maintenance costs; and Any usage-based or consumption-based charges.
e) The Service Provider must provide scalable licensing options capable of accommodating future growth in
business requirements.
9.12 POST-IMPLEMENTATION SUPPORT
The Service Provider must provide post-implementation support services, including:
a) Knowledge transfer to SARS personnel.
b) End-user and administrator training.
c) User guides, technical documentation, and operational manuals.
d) Transition support to enable business-as-usual operations following implementation.
