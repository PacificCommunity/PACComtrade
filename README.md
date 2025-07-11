# PACComtrade

The PACComtrade database is designed to provide timely and detailed information on goods imported and exported across Pacific Island Countries and Territories (PICTs). Developed by the Pacific Community (SPC) in collaboration with regional organisations including the Pacific Islands Forum Secretariat (PIFS), the Oceania Customs Organisation (OCO), and the Melanesian Spearhead Group (MSG), with support from UNCTAD and other UN agencies, the database aims to enhance decision-making in areas such as food security, trade negotiations, and economic planning. It sources data directly from Customs Administrations using the ASYCUDAWorld application, and offers granular trade data at the 6-digit Harmonized System (HS) code level. Hosted onthe Pacific Data Hub, PACComtrade datasets will complement existing International Merchandise Trade Statistics (IMTS) by providing more timely and detailed commodity-level insights, thereby supporting regional integration and development efforts.

## Running and parameterizing the program

Dependenices for running the Python script are listed in the _requirements.txt_ file.

The program requires a _secrets.json_ file to be present in the same folder. A template for this file is provided in the _secrets-template.json_ file and different parameters are explained in the following section.

## Resource files and folder structure 

### secrets.json file

Dictionnary of of dictionnaries, first level identifying the country to which parameters apply using ISO 3166-alpha2 code, second level providing the series of parameters described below.  

| Parameter name        | Description                                                                                                                                                                                                          |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWUrlTemplate         | URL template for the ASUCUDAWorld report from whiohc CSV dataset is downloaded, using paceholders [AWReportFrom] and [AWReportTo] for he rporting date, and [AWUid] and [AWPwd] for tthe user account to be used.    |
| AWUid                 | User id to be used to connect to the ASYCUDAWorld report.                                                                                                                                                            |
| AWPwd                 | Password to be used to connect to the ASYCUDAWorld report.                                                                                                                                                           |
| AWEarliest            | Earliest month for with PACComtrade may be calculated, in the form YYY-MM.                                                                                                                                           |
| DSSUid                | User id to be used for publication on .Stat Suite.                                                                                                                                                                   | 
| DSSPwd                | Password to be used for publication on .Stat Suite.                                                                                                                                                                  |
| DSSKCAPI              | URL of the .Stat Suite Keycloak APIto be used for authetication.                                                                                                                                                     |
| DSSImportAPI          | URL of the .Stat Suite import API of the transfer service to which content is tu be published..                                                                                                                      |
| DSSSdmxAPI            | URL of the .Stat Suite SDMX endpoint to which content is tu be published..                                                                                                                                           |
| DSSDataspace          | Identifier of the .Stat Suite dataspace to which content is tu be published.                                                                                                                                         |
| SMTPHost              | URL of the SMTP server to be used to send email notifications.                                                                                                                                                       |
| SMTPPort              | Port of the SMTP server to be used to send email notifications.                                                                                                                                                      |
| SMTPUser              | Userid of the account used to send email notifications.                                                                                                                                                              |
| SMTPPassword          | Password of the account used to send email notifications.                                                                                                                                                            |
| SMTPRecipients        | Addresses to which email notifications should be sent.                                                                                                                                                               |
| HSCodeAssignement     | Start and End years for when Entities used certain versions of HS code (e.g. HS2017 vs. HS2022)                                                                                                                      |

### Structures

| File name             | Description                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| ALLOWEDCODES.xlsx     | Provides the list of allowed codes for each field in the ASYCUDAWorld report.                       |
| HIERARCHIES.xlsx      | Provides hierarchies among codes of the HS classification.                                          |

The SDMX folder contains SDMX structures to which data is published.

## Process and methodology overview

![image](https://github.com/user-attachments/assets/cc46771e-d048-4899-bc01-64ef3f5c622f)

### Collect

Data collcted from national customs according to a Data License Agreement (DLA), specifying the conditions of data collection.

For this purpose a specific ASYCUDAWorld repoting template is defined and data is fetched through an API call to collect data in CSV format.

### Validate

| Rule Id     |    Rule name                                              | Level                                            |
| ----------- | --------------------------------------------------------- | ------------------------------------------------ |
| R01         | Presence of mandatory columns                             | Fatal, processing of the month is interrupted    |
| R02         | Duplicate rows                                            | Warning, duplicate rows are kept                 |
| R03         | Missing value in column DATE                              | Error, corresponding records are excluded        |
| R04         | Missing value in column COMMODITY                         | Error, corresponding records are excluded        |
| R05         | Missing value in column COMMODITY_CLASSIFICATION          | Error, corresponding records are excluded        |
| R06         | Missing value in column TRADE_FLOW                        | Error, corresponding records are excluded        |
| R07         | Missing value in column INCOTERMS                         | Error, corresponding records are excluded        |
| R08         | Missing value in column CURRENCY                          | Error, corresponding records are excluded        |
| R09         | Missing value in column COUNTRY_ORIGIN                    | Error, corresponding records are excluded        |
| R10         | Missing value in column COUNTRY_DESTINATION               | Error, corresponding records are excluded        |
| R11         | Missing value in column TRANSPORT                         | Error, corresponding records are excluded        |
| R12         | Missing value in column TRADE_AGREEMENT                   | Error, corresponding records are excluded        |
| R13         | Format of values in column DATE                           | Error, corresponding records are excluded        |
| R14         | Validaty of HS classification version declared            | Error, corresponding records are excluded        |
| R15         | Validity of commodity codes given HS version declared     | Warning, invalid codes are recoded to unknown    |
| R16         | Validity of country codes for origin and destination      | Error, corresponding records are excluded        |
| R17         | Country of destination for imports                        | Error, corresponding records are excluded        |
| R18         | Country of origin for export                              | Error, corresponding records are excluded        |
| R19         | Transaction involves another counterpart                  | Error, corresponding records are excluded        |
| R20         | Currency code for being processed country                 | Error, corresponding records are excluded        |
| R21         | Allowed codes in column TRADE_FLOW                        | Error, corresponding records are excluded        |
| R22         | Allowed codes in column INCOTERMS                         | Error, corresponding records are excluded        |
| R23         | Allowed codes in column QUANTITY_UNIT                     | Error, corresponding records are excluded        |
| R24         | Allowed codes in columnTRANSPORT                          | Error, corresponding records are excluded        |
| R25         | Allowed codes in column TRADE_AGREEMENT                   | Error, corresponding records are excluded        |
| R26         | Value in column VALUE is numeric                          | Error, corresponding records are excluded        |
| R27         | Value in column FREIGHT_PAID is numeeic                   | Error, corresponding records are excluded        |
| R28         | Value in column INSURANCE_PAID is numeric                 | Error, corresponding records are excluded        |
| R29         | Value in column QUANTITY is numeric                       | Error, corresponding records are excluded        |

### Aggregate

Data aggregated on the dimensions of the dataset: 

- For TRADE_FLOW, INCOTERMS, COUNTERPART, TRANSPORT and TRADE_AGREEMENT a total is added.

- For COMMODITY data is aggregated at headings, chapters, sections and total.

### Publish

When a month of data is loaded to the .Stat Suite, data previously present for that months is deleted before reloading the complete month of newly processed data. This way data is fully replaced each time a month is executed.

Data is published under the Creative Commons Attribution 4.0 International Public License.

### Add metadata

An SDMX reference metadataset is linked to each PACComtrade dataset.

Most of the information remains identical across the different months of data published, but the ate of data collection is updated in associated reference metadata for each time a month of datais  processed.

### Report

An execution report is sent by email at the end ofthe process.

The report contains a complete execution log inlcuding a series of execution metrucs, this log is in the body of the email and attahced.

A file with a copy of records having caused validation errors is also attached to the email.

Execution report is send to receipients listed in the secrets.josn file for a given country.

### Orchestrate

The list of countries for which the process is executed is specified in execution parameters, using ISO 3166-alpha2 code like this:

PICTs=["KI", "TO", "TV"]

For each country the process is executed, corresponding parameters from the _secrets.jon_ file loaded and data calculated with the following approach:

- Last 3 month flagged as provisional

- last 4 months processed, for month of execution M, M-4 becomes final, M-3 and M-2 are revised and M-1 is calculated for the first time.
