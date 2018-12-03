# -*- coding: utf-8 -*-
import os
import unittest

import mysql.connector
import pandas as pd
from app_config import DbCredentials
from utilities.excel_reader import ExcelReader
from utilities.woocommerce_updater import WooCommerceUpdater


class TestWooCommerceUpdater(unittest.TestCase):


    def testDbUpdate(self):
        # method for testing mysql updates, using mysql-connector-python package
        cnx = mysql.connector.connect(  # open a mysql connection - for now it's the test database
            user=DbCredentials.TEST_MYSQL_USER,  # new user created via plesk, with update permissions
            password=DbCredentials.TEST_MYSQL_PASSWORD,
            host=DbCredentials.TEST_MYSQL_HOST,
            database=DbCredentials.TEST_MYSQL_DATABASE
        )

        sqlStatement = \
            "update 4mnHYjMa6v_postmeta set meta_value=28 " \
            "WHERE post_id = 80 and meta_key = '_sale_price'"

        cnx.cursor().execute(sqlStatement)

        cnx.commit()
        cnx.close()

    def testSyncPrices(self):
        """
        test if the prices have been properly synced. Compare the contents
        of the two excel files exported from the ERP and WooCommerce
        :return:
        """
        # open the file exported from the ERP
        df = pd.read_excel('G:\\captain\\price-data\\times.xlsx', dtype=object)  # read the file with pandas
        # get data from the file into lists
        skuData = df[ExcelReader.FILE_COLUMN_NAMES[0]]
        unitData = df[ExcelReader.FILE_COLUMN_NAMES[1]]
        retailPrice1 = df[ExcelReader.FILE_COLUMN_NAMES[2]]
        retailPrice2 = df[ExcelReader.FILE_COLUMN_NAMES[3]]
        quantity = df[ExcelReader.FILE_COLUMN_NAMES[4]]

        # create a dictionary with the skus from the erp excel file
        skuDictionary = dict()
        for i in range(skuData.size):
            skuDictionary[skuData[i]] = i

        # open the file exported from Woocommerce

        # read the file with pandas
        wcdf = pd.read_excel('G:\\captain\\price-data\\wc_export_1-11-2018_1113.xlsx', dtype=object)

        wcCodeColumn = u'Κωδικός προϊόντος'
        wcRetailPrice1Column = u'Κανονική τιμή'
        wcRetailPrice2Column = u'Τιμή προσφοράς'
        wcQuantityColumn = u'Απόθεμα'
        # get the columns in the data frames
        wcSkuData = wcdf[wcCodeColumn]
        wcRetailPrice1 = wcdf[wcRetailPrice1Column]
        wcRetailPrice2 = wcdf[wcRetailPrice2Column]
        wcQuantity = wcdf[wcQuantityColumn]

        # check if the price update has been properly executed
        noOfChecks = 0
        noOfProblems = 0  # the number of problems found
        for i in range(wcSkuData.size):  # for each product in the WooCommerce database
            excelIndex = skuDictionary.get(WooCommerceUpdater.getErpCode(wcSkuData[i]))
            # the index of the product data in the ERP export file
            if excelIndex is not None:  # if the product data exist in the excel file exported from the ERP
                noOfChecks = noOfChecks + 1
                # first fix the problem with the erp quantity being nan
                if quantity.isna()[excelIndex] or quantity[excelIndex] < 0:
                    q = 0
                else:
                    q = quantity[excelIndex]

                if (
                        float(wcRetailPrice1[i]) != retailPrice1[excelIndex] or
                        float(wcRetailPrice2[i]) != retailPrice2[excelIndex] or
                        int(wcQuantity[i]) != q
                ):  # if you finds mistakes while comparing data
                    noOfProblems = noOfProblems + 1
            else:
                x = 4

        assert noOfProblems == 0  # assert no problems have been found
        assert noOfChecks == wcSkuData.size  # assert that all data have been checked

    def test_saveLogToFile(self):
        """
        testing the static method that saves logs to files. Scenarios:
        a) saving a success log msg. Check that the success file exists and that the message has been inserted
        b) saving an error log msg. Check that the errors file exists and that the message has been inserted
        :return:
        """
        # set folder and file names
        logFolderName = 'logs'
        successFileName = 'success.txt'
        errorsFileName = 'errors.txt'

        # Scenario a. Success log.
        # save some log
        filePath = os.path.join(logFolderName, successFileName)  # the success file path
        logMsg = 'Successful sync'  # the message that will be recorded
        WooCommerceUpdater.saveLogToFile(logMsg)
        # check that the file exists
        assert os.path.exists(filePath)
        # check that the file contains the log
        assert logMsg in open(filePath).read()
        # check that irrelevant messages do not exist in the log file
        assert not 'irrelevantblabla' in open(filePath).read()

        # Scenario b. Error log.
        # save some log
        filePath = os.path.join(logFolderName, errorsFileName)  # the error file pat
        logMsg = 'Problem with sync'  # the message that will be recorded
        WooCommerceUpdater.saveLogToFile(logMsg, False)
        # check that the file exists
        assert os.path.exists(filePath)
        # check that the file contains the log
        assert logMsg in open(filePath).read()
        # check that irrelevant messages do not exist in the log file
        assert not 'irrelevantblabla' in open(filePath).read()




