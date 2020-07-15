#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os
from pyfiglet import Figlet
from BDNS_validation import BDNSValidator
import config.config_def as config
from qrcode_gen import make_qrc
import numpy as np
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


__author__ = "Francesco Anselmo, Anushan Kirupakaran, Annalisa Romano"
__copyright__ = "Copyright 2019, Francesco Anselmo"
__credits__ = ["Francesco Anselmo"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Francesco Anselmo, , Anushan Kirupakaran, Annalisa Romano"
__email__ = "francesco.anselmo@arup.com, anushan.kirupakaran@arup.com, annalisa.romano@arup.com"
__status__ = "Dev"



SPREADSHEET_ID = config.SPREADSHEET_ID
WORKSHEET = config.WORKSHEET
CREDENTIAL_FILE_PATH = config.CREDENTIAL_FILE_PATH
OUTFOLDER_GS = config.OUTFOLDER
URL_BDNS = config.URL_BDNS
BDNS_VALIDATION = config.BDNS_VALIDATION

if not os.path.exists(OUTFOLDER_GS):
    os.mkdir(OUTFOLDER_GS)


DICTFONT = { "small":5,
             "medium":10,
             "large":15
            }

SCOPES = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]



def create_qrcode(row,dict_font):
    color_text = row['color_text']
    caption = row['asset_name']
    try:
        font = row['boxsize']
        boxsize = dict_font[font]
    except:
        boxsize = 10
    print("Creating the qr code for %s"%caption)

    img = make_qrc(row['asset_guid'], caption, boxsize, color_text)
    img.save(OUTFOLDER_GS + "/%s.png" % caption)


def show_title():
    """Show the program title
    """
    f1 = Figlet(font='standard')
    print(f1.renderText('GSheet2QRcode'))


def main():

    show_title()

    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE_PATH, SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SPREADSHEET_ID)
    wks = sh.worksheet(WORKSHEET)

    data = wks.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    bdns_csv = pd.read_csv(URL_BDNS)
    bdns_abb = bdns_csv[['abbreviation', 'ifc_class']]


    if BDNS_VALIDATION:
        BDNSVal = BDNSValidator(df)


        print('The following devices fail the GUID validation tests:')
        failed_GUID = BDNSVal.validate_GUID()
        print("-------------------")

        print('The following devices fail the device role name validation tests:')
        failed_DeviceName = BDNSVal.validate_DeviceName()
        print("-------------------")

        print('The following devices fail to follow the BDNS abbreviation:')
        faild_abb = BDNSVal.validate_abb(bdns_csv)
        print("-------------------")


        l =  failed_GUID+failed_DeviceName+faild_abb
        df['color_text'] = np.where(df['asset_name'].isin(l), 'red', 'black')


        checkdup = BDNSVal.check_duplicates()
        if not checkdup.empty:
            print("Duplicate GUID are:")
            print(checkdup)
            print("-------------------")


    df.apply(create_qrcode, dict_font=DICTFONT, axis=1)




if __name__ == "__main__":
    main()

