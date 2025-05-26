# PACComtrade
Processing of national Pacific commodity trade datasets for the Pacific Data Hub.

## Running and parameterizing the program

TODO

## Resource files and folder structure 

secrets.json file

Dictionnary of parameters by country represented by and ISO 3166-alpha2 code

| Parameter name        | Description  |
| --------------------- | ------------ |
| AWUrlTemplate         | ???          |
| AWUid                 | ???          |
| AWPwd                 | ???          |
| AWEarliest            | ???          |
| DSSUid                | ???          |
| DSSPwd                | ???          |
| DSSKCAPI              | ???          |
| DSSImportAPI          | ???          |
| DSSSdmxAPI            | ???          |
| DSSDataspace          | ???          |
| SMTPHost              | ???          |
| SMTPPort              | ???          |
| SMTPUser              | ???          |
| SMTPPassword          | ???          |
| SMTPRecipients        | ???          |

## Process and methodology overview

![image](https://github.com/user-attachments/assets/cc46771e-d048-4899-bc01-64ef3f5c622f)

### Collect

TODO
- Data collcted under DLA between national customs and SPC
- ASYCUDAWorld repoting template
- CSV fetched through API call

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

TODO

### Publish

TODO
- Delete/reload all data when a month is processed
- Data published under Creative Commons Attribution 4.0 International Public License

### Add metadata

TODO
- SDMX reference metadataset linked to each dataset
- Date of data collection added to reference metadata for each months of data processed

### Orchestrate

TODO
- For list of countries specified in execution parameters
- Last 3 month flagged as provisional
- last 4 months processed, for month of execution M, M-4 becomes final, M-3 and M-2 are revised and M-1 is calculated for the first time.
- 


