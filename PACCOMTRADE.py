# ************************************************************************************************************************
#   _____        _____ _____ ____  __  __ _______ _____            _____  ______ 
#  |  __ \ /\   / ____/ ____/ __ \|  \/  |__   __|  __ \     /\   |  __ \|  ____|
#  | |__) /  \ | |   | |   | |  | | \  / |  | |  | |__) |   /  \  | |  | | |__   
#  |  ___/ /\ \| |   | |   | |  | | |\/| |  | |  |  _  /   / /\ \ | |  | |  __|  
#  | |  / ____ \ |___| |___| |__| | |  | |  | |  | | \ \  / ____ \| |__| | |____ 
#  |_| /_/    \_\_____\_____\____/|_|  |_|  |_|  |_|  \_\/_/    \_\_____/|______|
#                                                                                
# ************************************************************************************************************************

# ************************************************************************************************************************
# INITIALIZE LOGGER
# ************************************************************************************************************************

from datetime import datetime

logs=[]

def log(lvl, msg) :

    ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lvlpad=lvl+(" "*(7-len(lvl)))
    
    print(f"{ts} > {lvlpad} : {msg}")

    logs.append({"ts" : ts, "lvl" : lvl, "msg" : msg})

log("INFO", "START")

# ************************************************************************************************************************
# IMPORT LIBRARIES
# ************************************************************************************************************************

log("INFO", "Import modules")

from datetime import date
from datetime import timedelta

import time

from dateutil.relativedelta import relativedelta

import os

import requests

requests.packages.urllib3.disable_warnings()

import numpy as np

import pandas as pd

import sys

import json

import math

from requests_toolbelt.multipart.encoder import MultipartEncoder

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ************************************************************************************************************************
# SET GLOBAL PARAMETERS
# ************************************************************************************************************************

log("INFO", "Set global parameters")

rootFolder="."

secretsFile=f"{rootFolder}/secrets.json"

PICTCurrencies={"KI" : "AUD", "TO" : "TOP", "TV" : "AUD", "VU" : "VUV", }

mandatoryCols=[
    "DATE",
    "COMMODITY",
    "COMMODITY_CLASSIFICATION",
    "TRADE_FLOW",
    "VALUE",
    "INCOTERMS",
    "FREIGHT_PAID",
    "INSURANCE_PAID",
    "CURRENCY",
    "QUANTITY",
    "QUANTITY_UNIT",
    "COUNTRY_ORIGIN",
    "COUNTRY_DESTINATION",
    "TRADE_AGREEMENT",
    "TRANSPORT"
]

codelistFile=f"{rootFolder}/Structures/ALLOWEDCODES.xlsx"

hierarchyFile=f"{rootFolder}/Structures/HIERARCHIES.xlsx"

HSy={
    "2017" : "2017",
    "2018" : "2017",
    "2019" : "2017",
    "2020" : "2017",
    "2021" : "2017",
    "2022" : "2022",
    "2023" : "2022",
    "2024" : "2022",
    "2025" : "2022",
    "2026" : "2022"
}

# ************************************************************************************************************************
#  __          ______  _____  _  __ _____ _____        _____ ______ 
#  \ \        / / __ \|  __ \| |/ // ____|  __ \ /\   / ____|  ____|
#   \ \  /\  / / |  | | |__) | ' /| (___ | |__) /  \ | |    | |__   
#    \ \/  \/ /| |  | |  _  /|  <  \___ \|  ___/ /\ \| |    |  __|  
#     \  /\  / | |__| | | \ \| . \ ____) | |  / ____ \ |____| |____ 
#      \/  \/   \____/|_|  \_\_|\_\_____/|_| /_/    \_\_____|______|
#                                                                                                                                  
# ************************************************************************************************************************

def workspace(PICT) :

    global PICTCurrency

    PICTCurrency=PICTCurrencies.get(PICT)
    
# ************************************************************************************************************************
# FETCH SECRETS FROM JSON FILE
# ************************************************************************************************************************

    log("INFO", "Fetch secrets from JSON file")

    global AWUrlTemplate
    global AWUid
    global AWPwd
    global AWEarliest
    global DSSUid
    global DSSPwd
    global DSSKCAPI
    global DSSImportAPI
    global DSSDataspace
    global SMTPHost
    global SMTPPort
    global SMTPUser
    global SMTPPassword
    global SMTPRecipients
        
    with open(secretsFile) as f :

        secrets=json.load(f).get(PICT)

        AWUrlTemplate=secrets.get("AWUrlTemplate")
        AWUid=secrets.get("AWUid")
        AWPwd=secrets.get("AWPwd")
        AWEarliest=secrets.get("AWEarliest")
        DSSUid=secrets.get("DSSUid")
        DSSPwd=secrets.get("DSSPwd")
        DSSKCAPI=secrets.get("DSSKCAPI")
        DSSImportAPI=secrets.get("DSSImportAPI")        
        DSSDataspace=secrets.get("DSSDataspace")
        SMTPHost=secrets.get("SMTPHost")
        SMTPPort=secrets.get("SMTPPort")
        SMTPUser=secrets.get("SMTPUser")
        SMTPPassword=secrets.get("SMTPPassword")
        SMTPRecipients=secrets.get("SMTPRecipients")
        
# ************************************************************************************************************************
# SETUP WORKSPACE
# ************************************************************************************************************************
    
    log("INFO", "Setup process workspace")

    global workFolder
    global workFolderTS

    workspaceFolder=f"{rootFolder}/Workspace"
    if not os.path.exists(workspaceFolder):
       os.makedirs(workspaceFolder)
    
    workFolderTS=datetime.now().strftime("%Y%m%d-%H%M%S")

    workFolder=f"{workspaceFolder}/{PICT}-{workFolderTS}"

    os.mkdir(workFolder)

    logTable=pd.DataFrame(columns=["ts", "lvl", "msg"])

# ************************************************************************************************************************
#    _____ ____  _      _      ______ _____ _______ 
#   / ____/ __ \| |    | |    |  ____/ ____|__   __|
#  | |   | |  | | |    | |    | |__ | |       | |   
#  | |   | |  | | |    | |    |  __|| |       | |   
#  | |___| |__| | |____| |____| |___| |____   | |   
#   \_____\____/|______|______|______\_____|  |_|   
#                                                   
# ************************************************************************************************************************

def collect(reportMonth) :


# ************************************************************************************************************************
# SET REPORTING DATES
# ************************************************************************************************************************

    AWParameters={}
    
    log("INFO", "Set reporting dates")

    AWReportFrom=f"{reportMonth}-01"

    AWParameters.update({"AWReportFrom" : AWReportFrom})

    log("INFO", f"- report start date {AWReportFrom}")

    AWReportTo=(datetime.strptime(AWReportFrom, "%Y-%m-%d")+relativedelta(months=1)-relativedelta(days=1)).strftime("%Y-%m-%d")

    AWParameters.update({"AWReportTo" : AWReportTo})

    log("INFO", f"- report end date   {AWReportTo}")

# ************************************************************************************************************************
# BUILD URL TO REPORT
# ************************************************************************************************************************

    log("INFO", "Build URL to ASYCUDAWorld API")

    AWParameters.update({"AWUid" : AWUid})
    AWParameters.update({"AWPwd" : AWPwd})

    AWUrl=AWUrlTemplate

    for k, v in AWParameters.items() :

        AWUrl=AWUrl.replace(f"[{k}]", v)

# ************************************************************************************************************************
# DOWNLOAD AW REPORT DATA
# ************************************************************************************************************************

    log("INFO", "Download CSV data")

    csvFileName=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}.csv"

    headers={}

    retries=3
    for i in range(1, retries+1) :

        try :
        
            with requests.get(AWUrl, stream=True, headers=headers, verify=False) as r:
                
                if (not r.ok) :

                    log("ERROR", f"Could not download data from ASYCUDAWorld for month {reportMonth}, HTTP status code is {r.status_code}")

                with open(csvFileName, "wb") as f:

                    for chunk in r.iter_content(chunk_size=8192): 

                        f.write(chunk)

            break

        except :

            log("ERROR", f"Unable to download file, waiting 10s before retrying (attempt {i}/{retries})")

            time.sleep(10)

    if (os.path.getsize(csvFileName)==0) :

        log("ERROR", "Downloaded file is empty")

        return pd.DataFrame()


# ************************************************************************************************************************
# READ AW REPORT DATA
# ************************************************************************************************************************

    log("INFO", "Read CSV data")

    data=pd.read_csv(csvFileName, encoding="utf-8", sep=";", dtype=str, na_filter=False)

    log("INFO", f"CSV file contains {len(data.index)} rows")

# ************************************************************************************************************************
# RETURN DATASET
# ************************************************************************************************************************

    return data

# ***********************************************************************************************************************
#  __      __     _      _____ _____       _______ ______ 
#  \ \    / /\   | |    |_   _|  __ \   /\|__   __|  ____|
#   \ \  / /  \  | |      | | | |  | | /  \  | |  | |__   
#    \ \/ / /\ \ | |      | | | |  | |/ /\ \ | |  |  __|  
#     \  / ____ \| |____ _| |_| |__| / ____ \| |  | |____ 
#      \/_/    \_\______|_____|_____/_/    \_\_|  |______|
#                                                         
# ***********************************************************************************************************************

def validate(data) :

    log("INFO", f"VALIDATING data, starting with {len(data.index)} rows")

    dataErrors=pd.DataFrame(columns=mandatoryCols+["MESSAGE"])

# ************************************************************************************************************************
# CHECK [R01]: Presence of mandatory columns
# ************************************************************************************************************************

    log("INFO", "CHECK: Presence of mandatory columns")

    missingCols=[c for c in mandatoryCols if c not in data.columns]

    if (missingCols) :

        log("ERROR", "Missing mandatory columns: "+" ; ".join(missingCols)+", process will be interrupted.")

        sys.exit()
        
    else :

        log("INFO", "       OK")

# ************************************************************************************************************************
# HELPER FUNCTION TO SPLIT DATA/ERRORS ACCORDING TO BITMASK
# ************************************************************************************************************************

    def applyMask(data, bitMask, msg, dataErrors) :
        
        err=data[bitMask].copy()
       
        n=err.shape[0]
        
        if (n>0) :

            log("ERROR", f"       {n} row(s) excluded - {msg}")

            err["MESSAGE"]=msg

            dataErrors=pd.concat([dataErrors, err])

            data=data[~bitMask]

            log("INFO", f"       Dataset has now {data.shape[0]} rows")

        else :
                
            log("INFO", f"       OK")

        return data, dataErrors

# ************************************************************************************************************************
# CHECK [R02]: Duplicate rows
# ************************************************************************************************************************

    log("INFO", "CHECK: Duplicate rows")

    err=data[data.duplicated()].copy()

    n=err.shape[0]

    if (n>0) :

        log("WARNING", f"       {n} duplicate row(s)")

    else :

        log("INFO", f"       OK")
    
# ************************************************************************************************************************
# CHECK [R03-R12]: Missing values in mandatory columns
# ************************************************************************************************************************

    log("INFO", "CHECK: Missing values in mandatory columns")

    checkCols=["DATE", "COMMODITY", "COMMODITY_CLASSIFICATION", "TRADE_FLOW", "INCOTERMS", "CURRENCY", "COUNTRY_ORIGIN", "COUNTRY_DESTINATION", "TRANSPORT", "TRADE_AGREEMENT"]

    for col in checkCols :

        log("INFO", f"CHECK: Missing values in column {col}")

        bitMask=data[col].map(lambda x: x == "")        
        
        data, dataErrors=applyMask(data, bitMask, f"Missing value in column {col}", dataErrors)        

# ************************************************************************************************************************
# CHECK [R13]: DATE formats
# ************************************************************************************************************************

    log("INFO", "CHECK: DATE formats")

    bitMask=pd.to_datetime(data["DATE"], format="%Y-%m-%d", errors="coerce").isna()

    data, dataErrors=applyMask(data, bitMask, f"Invalid DATE", dataErrors)

# ************************************************************************************************************************
# CHECK: Commodity codes
# ************************************************************************************************************************

# ------------------------------------------------------------------------------------------------------------------------
# - [R14] Validity of HS classification specified
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", "CHECK: Validity of HS classification specified")

    codes=pd.read_excel(codelistFile, sheet_name="COMMODITY_CLASSIFICATION", dtype=str, na_filter=False)["CODE"].tolist()

    bitMask=~data["COMMODITY_CLASSIFICATION"].isin(codes)

    data, dataErrors=applyMask(data, bitMask, f"Invalid code in column COMMODITY_CLASSIFICATION", dataErrors)

# ------------------------------------------------------------------------------------------------------------------------
# - [R15] Validity of commodity codes in the HS classification specified
# ------------------------------------------------------------------------------------------------------------------------

    data.loc[:, "COMMODITY"]=data["COMMODITY"].str[:6]

    hss=data["COMMODITY_CLASSIFICATION"].unique().tolist()


    # PREPROCESSING STEP: Recodes HS codes starting with 93 or 99 to OTH

    bitMask=((data["COMMODITY"].str.startswith("93")) | data["COMMODITY"].str.startswith("99"))

    err=data[bitMask].copy()

    n=err.shape[0]

    if (n>0) :
        
        log("WARNING", f"       {n} row(s) with COMMODITY code starting with 93 or 99 recoded to OTHER")

        err["MESSAGE"]=f"COMMODITY code starting with 93 or 99 recoded to OTHER"

        dataErrors=pd.concat([dataErrors, err])

        data.loc[bitMask, "COMMODITY"]="OTH"

        log("INFO", f"       Dataset has now {data.shape[0]} rows")

    else :

        log("INFO", f"       OK")

    # -----

    for hs in hss :

        log("INFO", f"CHECK: Validity of commodity codes in {hs}")

        codes=pd.read_excel(codelistFile, sheet_name=hs, dtype=str, na_filter=False)

        codes=codes[codes["LVL"]=="4"]["CODE"].tolist()

        codes.append("OTH")
        
        bitMask=((data["COMMODITY_CLASSIFICATION"]==hs) & ~(data["COMMODITY"].isin(codes)))

        err=data[bitMask].copy()

        n=err.shape[0]
       
        if (n>0) :

            log("ERROR", f"       {n} row(s) with invalid {hs} COMMODITY recoded to UNKNOWN")

            err["MESSAGE"]=f"Invalid {hs} COMMODITY"

            dataErrors=pd.concat([dataErrors, err])

            data.loc[bitMask, "COMMODITY"]="_U"

            log("INFO", f"       Dataset has now {data.shape[0]} rows")

        else :

            log("INFO", f"       OK")
            
# ************************************************************************************************************************
# CHECK: Country codes
# ************************************************************************************************************************

# ------------------------------------------------------------------------------------------------------------------------
# - [R16] Validity of country codes
# ------------------------------------------------------------------------------------------------------------------------

    checkCols=["COUNTRY_ORIGIN", "COUNTRY_DESTINATION"]

    codes=pd.read_excel(codelistFile, sheet_name="COUNTRY", dtype=str, na_filter=False)["CODE"].tolist()

    for col in checkCols :

        log("INFO", f"CHECK: Validity of country codes in column {col}")

        bitMask=~data[col].isin(codes)

        data, dataErrors=applyMask(data, bitMask, f"Invalid code in column {col}", dataErrors)
        
# ------------------------------------------------------------------------------------------------------------------------
# - [R17] Country of destination for imports
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"CHECK: Country of destination for imports is {PICT}")

    bitMask=((data["TRADE_FLOW"].isin(["M", "M1", "M2"])) & (data["COUNTRY_DESTINATION"]!=PICT))

    data, dataErrors=applyMask(data, bitMask, f"Import with country of destination different of {PICT}", dataErrors)
 
# ------------------------------------------------------------------------------------------------------------------------
# - [R18] Country of origin for exports
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"CHECK: Country of origin for exports is {PICT}")

    bitMask=((data["TRADE_FLOW"].isin(["X", "X1", "X2"])) & (data["COUNTRY_ORIGIN"]!=PICT))

    data, dataErrors=applyMask(data, bitMask, f"Export with country of origin different of {PICT}", dataErrors)
    
# ------------------------------------------------------------------------------------------------------------------------
# - [R19] Transaction involves another counterpart
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"CHECK: Transaction involves another counterpart")

    bitMask=~((data["COUNTRY_ORIGIN"]!=PICT) | (data["COUNTRY_DESTINATION"]!=PICT))

    data, dataErrors=applyMask(data, bitMask, f"Both origin and destination countries are {PICT}", dataErrors)

# ************************************************************************************************************************
# CHECK [R20]: Currency code
# ************************************************************************************************************************

    log("INFO", f"CHECK: Currency code is {PICTCurrency}")

    bitMask=(data["CURRENCY"]!=PICTCurrency)

    data, dataErrors=applyMask(data, bitMask, "Invalid CURRENCY", dataErrors)

# ************************************************************************************************************************
# CHECK [R21-R25] : Other coded columns
# ************************************************************************************************************************

    checkCols=["TRADE_FLOW", "INCOTERMS", "QUANTITY_UNIT", "TRANSPORT", "TRADE_AGREEMENT"]

    for col in checkCols :

        log("INFO", f"CHECK: Validity of codes in column {col}")

        codes=pd.read_excel(codelistFile, sheet_name=col, dtype=str, na_filter=False)["CODE"].tolist()
        
        bitMask=~data[col].isin(codes)

        data, dataErrors=applyMask(data, bitMask, f"Invalid code in column {col}", dataErrors)

# ************************************************************************************************************************
# CHECK [R26-R29]: Numeric columns
# ************************************************************************************************************************

    checkCols=["VALUE", "FREIGHT_PAID", "INSURANCE_PAID", "QUANTITY"]

    for col in checkCols :

        log("INFO", f"CHECK: Numeric format in column {col}")

        bitMask=pd.to_numeric(data[col].replace("", 0), errors="coerce").isna()

        data, dataErrors=applyMask(data, bitMask, f"Invalid numeric format in column {col}", dataErrors)

# ************************************************************************************************************************
# SAVE AND RETURN DATA
# ************************************************************************************************************************

    log("INFO", f"Saving validated data to workspace, {data.shape[0]} rows")

    csvFileName=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-VALIDATED.csv"

    data.to_csv(csvFileName, encoding="utf-8", sep=";", index=False)
    
    log("INFO", f"Saving data errors to workspace, {dataErrors.shape[0]} rows")

    return data, dataErrors

# ***********************************************************************************************************************
#   _____  _____   ____   _____ ______  _____ _____ 
#  |  __ \|  __ \ / __ \ / ____|  ____|/ ____/ ____|
#  | |__) | |__) | |  | | |    | |__  | (___| (___  
#  |  ___/|  _  /| |  | | |    |  __|  \___ \\___ \ 
#  | |    | | \ \| |__| | |____| |____ ____) |___) |
#  |_|    |_|  \_\\____/ \_____|______|_____/_____/ 
#                                                   
# ***********************************************************************************************************************

def process(data) :
    
# ***********************************************************************************************************************
# MAP DATA STRUCTURE
# ***********************************************************************************************************************

# -----------------------------------------------------------------------------------------------------------------------
# TARGET STRUCTURE
# -----------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Define table structure")

    columns=[
        "FREQ", 
        "TIME_PERIOD", 
        "GEO_PICT", 
        "INDICATOR", 
        "TRADE_FLOW",
        "INCOTERMS", 
        "COMMODITY", 
        "COUNTERPART", 
        "TRANSPORT", 
        "TRADE_AGREEMENT", 
        "OBS_VALUE", 
        "UNIT_MEASURE", 
        "UNIT_MULT", 
        "OBS_STATUS", 
        "OBS_COMMENT", 
        "CONF_STATUS"
    ]

    nway=pd.DataFrame(columns=columns)

# -----------------------------------------------------------------------------------------------------------------------
# MAP DIMENSIONS
# -----------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Map dimensions")

    nway["TIME_PERIOD"]=data["DATE"].str[:7]
    nway["FREQ"]="M"

    nway["GEO_PICT"]=PICT

    nway.loc[nway["TRADE_FLOW"].isin(["M", "M1", "M2"]), "GEO_PICT"]=data["COUNTRY_DESTINATION"]
    nway.loc[nway["TRADE_FLOW"].isin(["X", "X1", "X2"]), "GEO_PICT"]=data["COUNTRY_ORIGIN"]    

    nway["TRADE_FLOW"]=data["TRADE_FLOW"]

    nway["INCOTERMS"]=data["INCOTERMS"]

    nway["COMMODITY"]=data["COMMODITY"]

    nway.loc[nway["TRADE_FLOW"].isin(["M", "M1", "M2"]), "COUNTERPART"]=data["COUNTRY_ORIGIN"]    
    nway.loc[nway["TRADE_FLOW"].isin(["X", "X1", "X2"]), "COUNTERPART"]=data["COUNTRY_DESTINATION"]

    nway["TRANSPORT"]=data["TRANSPORT"]

    nway["TRADE_AGREEMENT"]=data["TRADE_AGREEMENT"]

# -----------------------------------------------------------------------------------------------------------------------
# MAP MEASURES AND ATTRUBUTES
# -----------------------------------------------------------------------------------------------------------------------

    log("INFO", "Map measures and attributes")

    # INDICATOR: VALUE
    log("INFO", "- VALUE")

    VALUE=nway.copy()
    VALUE["INDICATOR"]="VALUE"
    VALUE["OBS_VALUE"]=data["VALUE"].astype(np.float64).round(0)
    VALUE["UNIT_MEASURE"]=data["CURRENCY"]
    VALUE["UNIT_MULT"]=""

    log("INFO", f"  has "+str(VALUE.shape[0])+" rows")

    # INDICATOR: FREIGHT_PAID
    log("INFO", "- FREIGHT_PAID")

    FREIGHT_PAID=nway.copy()
    FREIGHT_PAID["INDICATOR"]="FREIGHT_PAID"
    FREIGHT_PAID["OBS_VALUE"]=pd.to_numeric(data["FREIGHT_PAID"], errors="coerce").fillna(0).astype(np.float64).round(0)
    FREIGHT_PAID["UNIT_MEASURE"]=data["CURRENCY"]
    FREIGHT_PAID["UNIT_MULT"]=""

    log("INFO", f"  has "+str(FREIGHT_PAID.shape[0])+" rows")

    # INDICATOR: INSURANCE_PAID
    log("INFO", "- INSURANCE_PAID")

    INSURANCE_PAID=nway.copy()
    INSURANCE_PAID["INDICATOR"]="INSURANCE_PAID"
    INSURANCE_PAID["OBS_VALUE"]=pd.to_numeric(data["INSURANCE_PAID"], errors="coerce").fillna(0).astype(np.float64).round(0)
    INSURANCE_PAID["UNIT_MEASURE"]=data["CURRENCY"]
    INSURANCE_PAID["UNIT_MULT"]=""

    log("INFO", f"  has "+str(INSURANCE_PAID.shape[0])+" rows")

    # INDICATOR: TOTAL_AMOUNT
    log("INFO", "- TOTAL_AMOUNT")

    TOTAL_AMOUNT=nway.copy()
    TOTAL_AMOUNT["INDICATOR"]="TOTAL_AMOUNT"
    TOTAL_AMOUNT["OBS_VALUE"]=VALUE["OBS_VALUE"]+FREIGHT_PAID["OBS_VALUE"]+INSURANCE_PAID["OBS_VALUE"]
    TOTAL_AMOUNT["UNIT_MEASURE"]=data["CURRENCY"]
    TOTAL_AMOUNT["UNIT_MULT"]=""

    log("INFO", f"  has "+str(TOTAL_AMOUNT.shape[0])+" rows")

    nway=pd.concat([VALUE])

    log("INFO", f"NWAY table has "+str(nway.shape[0])+" rows")

# ------------------------------------------------------------------------------------------------------------------------
# DROP ZEROES AND BLANKS
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Drop zeroes and blanks")
    
    nway=nway[~(nway["OBS_VALUE"]==0)]

    nway=nway[~(nway["OBS_VALUE"].isna())]

    log("INFO", f"NWAY table has "+str(nway.shape[0])+" rows")
    
# ------------------------------------------------------------------------------------------------------------------------
# MAP VALUES
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Map unknown values")

    log("INFO", "- Counterpart")
    
    nway.loc[nway["COUNTERPART"].isin(["XX"]), "COUNTERPART"]="_U"

    log("INFO", "- Transport")

    nway.loc[nway["TRANSPORT"].isin(["9"]), "TRANSPORT"]="_U"

# ------------------------------------------------------------------------------------------------------------------------
# SET ATTRIBUTE VALUES
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Set attributes")

    nway["OBS_STATUS"]=""
    nway["OBS_COMMENT"]=""
    nway["CONF_STATUS"]=""

# ***********************************************************************************************************************
# AGGREGATE NWAY TABLE
# ************************************************************************************************************************

    log("INFO", f"Aggregate NWAY table")

    nway["OBS_VALUE"]=nway["OBS_VALUE"].astype(np.int64)

    nway=nway.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    log("INFO", f"NWAY table has "+str(nway.shape[0])+" rows")

    log("INFO", f"Export NWAY table")

    nwayFileName=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-NWAY.csv"

    nway.to_csv(nwayFileName, index=False, sep=";")

# ***********************************************************************************************************************
# CUBE LEVELS
# ************************************************************************************************************************

    log("INFO", f"Calculating CUBE levels")

    cube=nway.copy()

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# TRADE_FLOW
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for TRADE_FLOW")

    # ADD TOTAL EXPORTS AND TOTAL IMPORTS

    log("INFO", f"- Total imports and exports")

    part=cube.copy()

    m={"M1" : "M", "M2" : "M", "X1" : "X", "X2" : "X"}

    part["TRADE_FLOW"]=part["TRADE_FLOW"].map(m)

    part=part.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, part])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# INCOTERMS
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for INCOTERMS")

    # ADD TOTAL

    log("INFO", f"- Total")

    part=cube.copy()

    part["INCOTERMS"]="_T"

    part=part.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, part])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# COUNTERPART
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for COUNTERPART")

    # ADD TOTAL

    log("INFO", f"- Total")

    part=cube.copy()

    part["COUNTERPART"]="_T"

    part=part.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, part])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# TRANSPORT
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for TRANSPORT")

# ADD TOTAL

    log("INFO", f"- Total")

    part=cube.copy()

    part["TRANSPORT"]="_T"

    part=part.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, part])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# TRADE_AGREEMENT
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for TRADE_AGREEMENT")

    # ADD TOTAL

    log("INFO", f"- Total")

    part=cube.copy()

    part["TRADE_AGREEMENT"]="_T"

    part=part.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, part])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# COMMODITY 
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Calculate cube levels for COMMODITY")

    y=HSy.get(reportMonth[:4])

    # GET HS HIERARCHY

    log("INFO", f"- Get HS {y} hierarchy")

    hshier=pd.read_excel(hierarchyFile, sheet_name=f"HS{y}", dtype=str)

    # SUB_HEADINGS IS ORIGINAL DATA, EXCLUDE 

    log("INFO", f"- Sub-headings")

    hsl4=cube.copy()

    # ADD HEADINGS

    log("INFO", f"- Headings")

    hsl3=hsl4.copy()
  
    m=dict(zip(hshier[~(hshier["L4"].isna())]["L4"], hshier[~(hshier["L4"].isna())]["L3"]))

    hsl3["COMMODITY"]=hsl3["COMMODITY"].map(m)

    hsl3=hsl3.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    # ADD CHAPTERS

    log("INFO", f"- Chapters")

    hsl2=hsl4.copy()

    m=dict(zip(hshier[~(hshier["L4"].isna())]["L4"], hshier[~(hshier["L4"].isna())]["L2"]))

    hsl2["COMMODITY"]=hsl2["COMMODITY"].map(m)

    hsl2=hsl2.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    # ADD SECTIONS

    log("INFO", f"- Sections")

    hsl1=hsl4.copy()

    m=dict(zip(hshier[~(hshier["L4"].isna())]["L4"], hshier[~(hshier["L4"].isna())]["L1"]))

    hsl1["COMMODITY"]=hsl1["COMMODITY"].map(m)

    hsl1=hsl1.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    # ADD TOTAL

    log("INFO", f"- Total")

    hsl0=hsl4.copy()

    m=dict(zip(hshier[~(hshier["L4"].isna())]["L4"], hshier[~(hshier["L4"].isna())]["L0"]))

    hsl0["COMMODITY"]=hsl0["COMMODITY"].map(m)

    hsl0=hsl0.groupby(["FREQ", "TIME_PERIOD", "GEO_PICT", "INDICATOR", "TRADE_FLOW","INCOTERMS", "COMMODITY", "COUNTERPART", "TRANSPORT", "TRADE_AGREEMENT"], as_index=False).agg({ "OBS_VALUE" : "sum", "UNIT_MEASURE" : "first", "UNIT_MULT" : "first", "OBS_STATUS" : "first", "OBS_COMMENT" : "first", "CONF_STATUS" : "first" })

    cube=pd.concat([cube, hsl3, hsl2, hsl1, hsl0])

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ************************************************************************************************************************
# POST-PROCESS
# ************************************************************************************************************************

# ------------------------------------------------------------------------------------------------------------------------
# ROUNDED THOUSANDS GREATER THAN ZERO
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Rounded thousands, exclude zeroes")

    cube["OBS_VALUE"]=(cube["OBS_VALUE"]/1000).round().astype(np.int64)

    cube["UNIT_MULT"]="3"

    cube=cube[~(cube["OBS_VALUE"]==0)]

    log("INFO", f"  CUBE table has "+str(cube.shape[0])+" rows ("+str(cube.shape[0]-cube.drop_duplicates().shape[0]) + " duplicates)")

# ------------------------------------------------------------------------------------------------------------------------
# OBS_STATUS FLAG DATA<3 MONTHS MARKES AS PROVISONNAL
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Set observation status")

    d=date.today().replace(day=1)
    M0=date.strftime(d, "%Y-%m")
    M1=date.strftime(d-relativedelta(months=1), "%Y-%m")
    M2=date.strftime(d-relativedelta(months=2), "%Y-%m")
    M3=date.strftime(d-relativedelta(months=3), "%Y-%m")

    cube["OBS_STATUS"]=np.where(cube["TIME_PERIOD"].isin([M0, M1, M2, M3]), "P", cube["OBS_STATUS"])

# ------------------------------------------------------------------------------------------------------------------------
# ADD SDMX HEADER COLULN
# ------------------------------------------------------------------------------------------------------------------------

    log("INFO", f"Add SDMX header column")

    cube.insert(0, f"DATAFLOW", f"SPC:DF_PACCOMTRADE_{PICT}_HS{y}(1.0)")

# ************************************************************************************************************************
# RETURN DATAFRAME
# ************************************************************************************************************************

    return cube

# ***********************************************************************************************************************
#   __  __ ______ _______       _____       _______       
#  |  \/  |  ____|__   __|/\   |  __ \   /\|__   __|/\    
#  | \  / | |__     | |  /  \  | |  | | /  \  | |  /  \   
#  | |\/| |  __|    | | / /\ \ | |  | |/ /\ \ | | / /\ \  
#  | |  | | |____   | |/ ____ \| |__| / ____ \| |/ ____ \ 
#  |_|  |_|______|  |_/_/    \_\_____/_/    \_\_/_/    \_\
# 
# ***********************************************************************************************************************

def metadata(reportMonth) :
    
# ***********************************************************************************************************************
# REFENCE METADATASET WITH DATA COLLECTED
# ***********************************************************************************************************************

    log("INFO", f"Create metadata record for data source date")

    y=HSy.get(reportMonth[:4])

    record={
        "STRUCTURE"                             : "DATAFLOW",
        "STRUCTURE_ID"                          : f"SPC:DF_PACCOMTRADE_{PICT}_HS{y}(1.0)",
        "ACTION"                                : "I",
        "FREQ"                                  : "~",
        "GEO_PICT"                              : PICT,
        "INDICATOR"                             : "~",
        "TRADE_FLOW"                            : "~",
        "INCOTERMS"                             : "~",
        "COMMODITY"                             : "~",
        "COUNTERPART"                           : "~",
        "TRANSPORT"                             : "~",
        "TRADE_AGREEMENT"                       : "~",
        "TIME_PERIOD"                           : reportMonth,
        "DATA_SOURCE.DATA_SOURCE_DATE"          : datetime.now().strftime("%d/%m/%Y")
    }
    
    metadata=pd.DataFrame.from_records(record, index=[0])[record.keys()]

    return metadata

# ***********************************************************************************************************************
#   _____  _    _ ____  _      _____  _____ _    _ 
#  |  __ \| |  | |  _ \| |    |_   _|/ ____| |  | |
#  | |__) | |  | | |_) | |      | | | (___ | |__| |
#  |  ___/| |  | |  _ <| |      | |  \___ \|  __  |
#  | |    | |__| | |_) | |____ _| |_ ____) | |  | |
#  |_|     \____/|____/|______|_____|_____/|_|  |_|
#                                                  
# ***********************************************************************************************************************

# ***********************************************************************************************************************
# GET KEYKLOAK TOKEN
# ***********************************************************************************************************************

def getKcToken() :

    log("INFO", f"Get Keykloak token")

    r=requests.post(DSSKCAPI, data={"grant_type" : "password", "client_id" : "stat-suite", "username" : DSSUid, "password" : DSSPwd, "scope" : "openid"})    

    kcToken=r.json()["access_token"]

    return kcToken

# ***********************************************************************************************************************
# UPLOAD SDMX FILE
# ***********************************************************************************************************************
    
def publish(fileName) :

    y=HSy.get(reportMonth[:4])

    dfag="SPC"
    dfid=f"DF_PACCOMTRADE_{PICT}_HS{y}"
    dfve="1.0"

    kcToken=getKcToken()
    
    log("INFO", f"Upload to .STAT dataflow {dfid}")

    mp_encoder=MultipartEncoder(
        fields={
            "file" : (os.path.basename(fileName), open(fileName, "rb"), "application/xml"),
            "dataspace": (None, DSSDataspace),
            "dataflow": (None, f"{dfag}:{dfid}({dfve})"),
            "validationType": (None, "0")
        }
    )

    headers={"Authorization": "Bearer "+kcToken, "Content-Type": mp_encoder.content_type}

    r=requests.post(DSSImportAPI, headers=headers, data=mp_encoder)

    if (not r.ok) :
        log("ERROR", "Call to "+DSSImportAPI+" gives response code "+str(r.status_code))
        print(r.content)
        
    else :
        log("INFO", "File successfully uploaded")

# ***********************************************************************************************************************
# DELETE DATA FOR GIVEN TIME_PERIOD
# ***********************************************************************************************************************

def deletData(PICT, reportMonth) :

    log("INFO", f"Deleting data for {PICT} {reportMonth}")

    y=HSy.get(reportMonth[:4])
  
    record={
        "STRUCTURE"                             : "DATAFLOW",
        "STRUCTURE_ID"                          : f"SPC:DF_PACCOMTRADE_{PICT}_HS{y}(1.0)",
        "ACTION"                                : "D",
        "FREQ"                                  : "M",
        "TIME_PERIOD"                           : reportMonth,
        "GEO_PICT"                              : PICT,
        "INDICATOR"                             : "",
        "TRADE_FLOW"                            : "",
        "INCOTERMS"                             : "",
        "COMMODITY"                             : "",
        "COUNTERPART"                           : "",
        "TRANSPORT"                             : "",
        "TRADE_AGREEMENT"                       : "",
        "OBS_VALUE"                             : "",
        "UNIT_MEASURE"                          : "",
        "UNIT_MULT"                             : "",
        "OBS_STATUS"                            : "",
        "OBS_COMMENT"                           : "",
        "CONF_STATUS"                           : ""       
    }
    
    delete=pd.DataFrame.from_records(record, index=[0])[record.keys()]

    deletedDataFile=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-DELETE.csv"

    delete.to_csv(deletedDataFile, index=False, sep=";")

    publish(deletedDataFile)  

# ***********************************************************************************************************************
#  _____  ______ _____   ____  _____ _______ 
# |  __ \|  ____|  __ \ / __ \|  __ \__   __|
# | |__) | |__  | |__) | |  | | |__) | | |   
# |  _  /|  __| |  ___/| |  | |  _  /  | |   
# | | \ \| |____| |    | |__| | | \ \  | |   
# |_|  \_\______|_|     \____/|_|  \_\ |_|
# 
# ***********************************************************************************************************************

def report(logs, errors) :

# ***********************************************************************************************************************
# SAVE LOGS AND ERROR FILES
# ***********************************************************************************************************************

    logsFileName=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-LOGS.xlsx"

    pd.DataFrame(logs).to_excel(logsFileName, index=False)

    errorsFileName=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-ERRORS.xlsx"

    errors.to_excel(errorsFileName, index=False)

# ***********************************************************************************************************************
# SEND EMAIL
# ***********************************************************************************************************************

    message = MIMEMultipart()

    # Message header
    message["From"]=SMTPUser
    message["To"]=SMTPRecipients
    message["Subject"]=f"PACComtrade process executed: {PICT} {reportMonth}"

    # Message body
    body= f"""
    <html>
    <head></head>
    <body>
        <h1>PACComtrade process executed: {PICT} {reportMonth}</h1>
        {pd.DataFrame(logs).to_html(border=1, header=True, index=False)}
    </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    if (not collected.empty) :
             
        # Attachment
        attachment=open(errorsFileName, "rb")
        mime_base = MIMEBase("application", "octet-stream")
        mime_base.set_payload((attachment).read())
        encoders.encode_base64(mime_base)
        mime_base.add_header("Content-Disposition", f"attachment; filename={errorsFileName.split('/')[-1]}")
        message.attach(mime_base)

    # Send
    with smtplib.SMTP(SMTPHost, SMTPPort) as server:
        server.starttls()
        server.login(SMTPUser, SMTPPassword)
        server.send_message(message)


# ***********************************************************************************************************************
#    ____  _____   _____ _    _ ______  _____ _______ _____         _______ ______ 
#   / __ \|  __ \ / ____| |  | |  ____|/ ____|__   __|  __ \     /\|__   __|  ____|
#  | |  | | |__) | |    | |__| | |__  | (___    | |  | |__) |   /  \  | |  | |__   
#  | |  | |  _  /| |    |  __  |  __|  \___ \   | |  |  _  /   / /\ \ | |  |  __|  
#  | |__| | | \ \| |____| |  | | |____ ____) |  | |  | | \ \  / ____ \| |  | |____ 
#   \____/|_|  \_\\_____|_|  |_|______|_____/   |_|  |_|  \_\/_/    \_\_|  |______|
#                                                                                  
# ***********************************************************************************************************************

# Countries for which the process should be executed

PICTs=["KI", "TO", "TV", "VU"]

# Months for which the process should be executed, the past 4 months
# Instead of execution time one could also query .STAT about last recorded month
d=date.today().replace(day=1)
M0=date.strftime(d, "%Y-%m")
M1=date.strftime(d-relativedelta(months=1), "%Y-%m")
M2=date.strftime(d-relativedelta(months=2), "%Y-%m")
M3=date.strftime(d-relativedelta(months=3), "%Y-%m")
M4=date.strftime(d-relativedelta(months=4), "%Y-%m")

reportMonths=[M1, M2, M3, M4]

# Loop over countries and months and run the collect/validate/aggregate/publish process

#PICTs=["KI"]
#reportMonths=["2025-04"]

for PICT in PICTs :

    workspace(PICT)
        
    for reportMonth in reportMonths :

        log("INFO", f"*** PACCOMTRADE PROCESS FOR MONTH {PICT} {reportMonth}")

        mCur=datetime.strptime(reportMonth,  "%Y-%m")
        mMin=datetime.strptime(AWEarliest,  "%Y-%m")
        if (mCur<mMin) :
            log("Warning", f"Skipping {reportMonth}, before earliest month allowed {AWEarliest}")
            continue

        logs=[]

        log("INFO", f"*** COLLECT DATA")
        
        collected=collect(reportMonth)

        if (collected.empty) :

            report(logs, pd.DataFrame())

            continue

        log("INFO", f"*** VALIDATE DATA")

        validated, errors=validate(collected)

        log("INFO", f"*** AGGREGATE DATA")

        processed=process(validated)

        log("INFO", f"*** DELETE PREVIOUS DATA")

        deletData(PICT, reportMonth)

        log("INFO", f"*** PUBLISH DATA")

        dataFile=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-CUBE.csv"

        processed.to_csv(dataFile, index=False, sep=";")    

        publish(dataFile)

        log("INFO", f"*** PREPARE METADATA")

        metadataset=metadata(reportMonth)

        log("INFO", f"*** PUBLISH METADATA")

        metadataFile=f"{workFolder}/{PICT}-{workFolderTS}-{reportMonth}-METADATA.csv"

        metadataset.to_csv(metadataFile, index=False, sep=";")

        publish(metadataFile)

        log("INFO", f"*** SEND EXECUTION REPORT")

        report(logs, errors)

# ************************************************************************************************************************
# STOP
# ************************************************************************************************************************

log("INFO", "STOP")
