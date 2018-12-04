# -*- coding: utf-8 -*-

# Resource for accessing excel data with pandas: https://pythonspot.com/read-excel-with-pandas/
import datetime
import os

import pandas as pd
import mysql.connector  # install mysql-connector-python

from app_config import DbCredentials
from utilities.excel_reader import ExcelReader


class WooCommerceUpdater:
    """
    class that updates woocommerce data
    """

    LOG_TYPE_SUCCESS = 1
    LOG_TYPE_ERRORS = 2
    LOG_TYPE_CHECK_SYNC = 3

    @staticmethod
    def handleWoocommerceDataSync(excelFileName, progressBar, lblStatus, isCheck=False):
        """
        Method that either executes the update of product data on the WooCommerce database or
        checks if the updating has been successful, depending on the value of the isCheck parameter.

        :param excelFileName: the file name of the excel file that will be imported
        :param progressBar: the progressbar showing the progress. The function will update it
        :param lblStatus: the label that will contain the status of the update
        :param isCheck: if False, then the method updates Woocommerce. If True, it compares product data
        (Wocommerce vs Excel), writes comparison results to a log file and show a results message.
        :return: False, if the file is not valid
        """
        # open the file and get the columns
        df = pd.read_excel(excelFileName, dtype=object)  # read the file with pandas

        # put the column names in a list
        columns = []
        for col in df.columns:
            columns.append(col)

        # check the validity of the filename and columns
        fileValidityResult, validityErrorMessage = ExcelReader.isValid(excelFileName, columns)
        if fileValidityResult is False:  # if not valid, return False
            errorMsg = u'Πρόβλημα με την ανάγνωση του αρχείου-'+validityErrorMessage
            WooCommerceUpdater.saveLogToFile(errorMsg, WooCommerceUpdater.LOG_TYPE_ERRORS)
            return False, errorMsg
        else:  # if valid, then load data from the excel file and update WooCommerce

            try:
                # get data from the file into lists
                skuData = df[ExcelReader.FILE_COLUMN_NAMES[0]]
                unitData = df[ExcelReader.FILE_COLUMN_NAMES[1]]
                retailPrice1 = df[ExcelReader.FILE_COLUMN_NAMES[2]]
                retailPrice2 = df[ExcelReader.FILE_COLUMN_NAMES[3]]
                quantity = df[ExcelReader.FILE_COLUMN_NAMES[4]]

                # create an index for SKUs to use when searching for a specific product data
                skuIndex = dict()
                for i in range(0, skuData.size):
                    skuIndex[skuData[i]] = i  # key: sku, value: the line(index) in the prev lists for
                    # the specific sku

                # connect to the database
                cnx = mysql.connector.connect(  # open a mysql connection - for now it's the test database
                    user=DbCredentials.MYSQL_USER,  # new user created via plesk, with update permissions
                    password=DbCredentials.MYSQL_PASSWORD,
                    host=DbCredentials.MYSQL_HOST,
                    database=DbCredentials.MYSQL_DATABASE,
                    buffered=True  # fetch items immediately after you query. Solves problem with unread items
                )

                # get the number of products in the database
                noOfSKUSSqlStatement = "SELECT count(*) FROM 4mnHYjMa6v_postmeta " \
                                       "WHERE meta_key='_sku' and meta_value is not null and meta_value !=''"
                noOfSkuCursor = cnx.cursor()
                noOfSkuCursor.execute(noOfSKUSSqlStatement)
                for a in noOfSkuCursor:
                    noOfSKUSinWoocommerce = a[0]

                # initialize the progress bar
                progressBar['maximum'] = noOfSKUSinWoocommerce

                # get the product skus that exist in the woocommerce database
                skuSqlStatement = "SELECT meta_value FROM `4mnHYjMa6v_postmeta` " \
                                  "WHERE meta_key = '_sku' and meta_value !=''"
                skuCursor = cnx.cursor()
                skuCursor.execute(skuSqlStatement)

                counter = 0  # counter that will be used for progress bar and status
                updatedCounter = 0  # counter only for the items whose sku was found in the excel file
                syncErrorCounter = 0  # errors found while checking the sync

                # in case of check sync, initialize the file (overwrite the old content)
                WooCommerceUpdater.saveLogToFile(
                    u'Έναρξη ελέγχου συγχρονισμού ' + str(datetime.datetime.now()),
                    WooCommerceUpdater.LOG_TYPE_CHECK_SYNC,
                    False
                )

                # for each product in the Woocommerce database, update the woocommerce product data
                # based on the data from the Excel file
                for productData in skuCursor:

                    sku = productData[0]  # get the product sku in Soft1 format
                    counter = counter + 1  # increase the counter

                    # get the index of the product with the specific sku
                    productIndex = skuIndex.get(WooCommerceUpdater.getErpCode(sku))

                    # update or check the woocommerce data of the specific product
                    if productIndex is not None:  # if the product sku exists in the excel file
                        if not isCheck:  # case of updating Woocommerce product data
                            # increase the counter of the items updated
                            updatedCounter = updatedCounter + 1

                            # update the e-shop price
                            if retailPrice2[productIndex] > 0:  # if the e-shop price is a positive number
                                if retailPrice2[productIndex] < retailPrice1[productIndex]:
                                    # update this price only if it is lower than the one of the shop
                                    WooCommerceUpdater.updateElementData(sku, '_sale_price', str(retailPrice2[productIndex]), cnx)
                                elif retailPrice2[productIndex] == retailPrice1[productIndex]:
                                    # update the _price field. Else, you won't see the price of the product
                                    WooCommerceUpdater.updateElementData(sku, '_price', str(retailPrice2[productIndex]), cnx)
                                    WooCommerceUpdater.updateElementData(sku, '_sale_price', str(retailPrice2[productIndex]), cnx)

                            # update the shop price
                            if retailPrice1[productIndex] > 0:  # if the shop price is a positive number
                                WooCommerceUpdater.updateElementData(sku, '_regular_price', str(retailPrice1[productIndex]), cnx)

                            # update the stock
                            stock = quantity[productIndex]
                            if stock < 0 or quantity.isna()[productIndex]:
                                # if the stock is less than zero or contains the NaN value (pandas), then make it zero
                                stock = 0
                            WooCommerceUpdater.updateElementData(sku, '_stock', str(stock), cnx)
                            WooCommerceUpdater.updateElementData(sku, '_manage_stock', "'yes'", cnx)

                            # update the status
                            lblStatus['text'] = u'Ενημερώνονται ' \
                                                + str(updatedCounter) + u' από ' + str(noOfSKUSinWoocommerce)
                        else:  # case that the method checks if product data are ok
                            # for each SKU, get the Woocommerce product data and check
                            eshopPrice, storePrice, stock = WooCommerceUpdater.getElementData(sku, cnx)

                            # setup the variables. Be careful of nan values!
                            if retailPrice2.isna()[productIndex]:
                                soft1EshopPrice = 0
                            else:
                                soft1EshopPrice = retailPrice2[productIndex]

                            if retailPrice1.isna()[productIndex]:
                                soft1StorePrice = 0
                            else:
                                soft1StorePrice = retailPrice1[productIndex]

                            if quantity.isna()[productIndex]:
                                soft1Stock = 0
                            else:
                                soft1Stock = quantity[productIndex]

                            eshopPriceCheck = float(eshopPrice) == soft1EshopPrice  # check the eshop price
                            storePriceCheck = float(storePrice) == soft1StorePrice  # check the store price
                            # check the stock. The values must be equal or the stock in Soft1 less than zero and
                            # in WooCommerce zero.

                            stockCheck = (soft1Stock == int(stock)) or \
                                         (int(stock) == 0 and soft1Stock < 0)

                            if eshopPriceCheck and storePriceCheck and stockCheck:
                                pass
                                # return True, ''
                            else:
                                WooCommerceUpdater.saveLogToFile(
                                    u'Πρόβλημα στα δεδομένα του προϊόντος με κωδικό ' + sku,
                                    WooCommerceUpdater.LOG_TYPE_CHECK_SYNC
                                )
                                syncErrorCounter += 1
                                # return False, u'Υπάρχουν διαφορές στις τιμές'

                    else:  # the product does not exist in the excel file. Report to the log files.
                        if not isCheck:  # case of update. Report it in the success log
                            WooCommerceUpdater.saveLogToFile(
                                u'Το προϊόν με κωδικό ' + sku + u' δεν υπάρχει στο αρχείο excel',
                                WooCommerceUpdater.LOG_TYPE_SUCCESS
                            )
                        else:  # case of check. Report it in the sync log file
                            WooCommerceUpdater.saveLogToFile(
                                u'Το προϊόν με κωδικό ' + sku + u' δεν υπάρχει στο αρχείο excel',
                                WooCommerceUpdater.LOG_TYPE_CHECK_SYNC
                            )

                    # update the progress bar
                    progressBar['value'] = counter
                    progressBar.update()

                cnx.commit()  # commit the transactions
                cnx.close()  # close the database connection

                if not isCheck:  # case of woocommerce updating
                    WooCommerceUpdater.saveLogToFile(
                        u'Ενημερώθηκαν '
                            + str(updatedCounter) + u' από ' + str(noOfSKUSinWoocommerce),
                        WooCommerceUpdater.LOG_TYPE_SUCCESS
                    )  # store success log in log file
                    return True, ''
                else:  # case of checking the sync
                    if syncErrorCounter == 0:
                        WooCommerceUpdater.saveLogToFile(
                            u'Όλα τα δεδομένα ελέγχθηκαν με επιτυχία',
                            WooCommerceUpdater.LOG_TYPE_CHECK_SYNC
                        )
                        return True, ''
                    else:
                        return False, u'Υπάρχουν διαφορές στα δεδομένα των προϊόντων'

            except Exception, e:
                # if any exception occurs, return False
                return False, u'Πρόβλημα με την ενημέρωση των στοιχείων των προϊόντων. '  # + e.msg


    @staticmethod
    def updateElementData(sku, element, elementData, dbConnection):
        """
        Function that updates the element data (eshop price, shop price, stock etc.) for a specific sku
        :param: sku - the product sku
        :param: element - the name of the element that will be updated
        :param: elementData - the data that will be inserted in the element
        :param: dbConnection - the db connection
        :return:
        """
        sqlStatement = \
            "update 4mnHYjMa6v_postmeta as a inner join 4mnHYjMa6v_postmeta as b on  " \
            "(b.meta_key='_sku' and a.post_id=b.post_id AND " \
            "(b.meta_value='" + sku + "' or b.meta_value like concat('" + sku + "','-%')) and " \
              "a.meta_key='"+element+"') " \
              "set a.meta_value=" + elementData
        dbConnection.cursor().execute(sqlStatement)  # execute statement

    @staticmethod
    def getElementData(sku, dbConnection):
        """
        Method that returns the element data (store price, eshop price, stock) from the Woocommerce MYSQL Database
        :param sku: the sku of the specific product (string)
        :param dbConnection: the db connection
        :return: a tuple containing the store price, the eshop price and the stock of the product with the specific sku
        """
        # first get the eshop price
        sqlStatement = \
        "select a.meta_value from 4mnHYjMa6v_postmeta as a inner join 4mnHYjMa6v_postmeta as b on  " \
            "(b.meta_key='_sku' and a.post_id=b.post_id AND " \
            "(b.meta_value='" + sku + "' or b.meta_value like concat('" + sku + "','-%')) and " \
            "a.meta_key='_sale_price')"
        cnxCursor = dbConnection.cursor()
        cnxCursor.execute(sqlStatement)
        eshopPrice = 0  # initialize the eshop price
        for a in cnxCursor:
            eshopPrice = a[0]

        # get the store (normal) price
        sqlStatement = \
            "select a.meta_value from 4mnHYjMa6v_postmeta as a inner join 4mnHYjMa6v_postmeta as b on  " \
            "(b.meta_key='_sku' and a.post_id=b.post_id AND " \
            "(b.meta_value='" + sku + "' or b.meta_value like concat('" + sku + "','-%')) and " \
            "a.meta_key='_regular_price')"
        cnxCursor = dbConnection.cursor()
        cnxCursor.execute(sqlStatement)
        storePrice = 0  # initialize the store price
        for a in cnxCursor:
            storePrice = a[0]

        # get the stock
        sqlStatement = \
            "select a.meta_value from 4mnHYjMa6v_postmeta as a inner join 4mnHYjMa6v_postmeta as b on  " \
            "(b.meta_key='_sku' and a.post_id=b.post_id AND " \
            "(b.meta_value='" + sku + "' or b.meta_value like concat('" + sku + "','-%')) and " \
            "a.meta_key='_stock')"
        cnxCursor = dbConnection.cursor()
        cnxCursor.execute(sqlStatement)
        stock = 0  # initialize the stock
        for a in cnxCursor:
            stock = a[0]

        return eshopPrice, storePrice, stock

    @staticmethod
    def getErpCode(wcSku):
        """

        :param wcSku:  the SKU in Woocommerce
        :return: the sku as it is stored in the ERP
        """

        sku = wcSku.lstrip('z')  # strip the z character
        sku = sku.lstrip('Z')  # strip the z character
        sku = sku.split('-')[0]  # get the part before the dash (-)

        return sku

    @staticmethod
    def saveLogToFile(text, logType, isAppendMode=True):
        """
        Static method that will be called when a log needs to be saved. If the log is related to success, it will
        be saved in success.txt, else it will be saved in errors.txt
        :param text: the text message accompanying the log (string)
        :param logType: int value showing if the log is about success, failure or sync check log
        :param isAppendMode: parameter for choosing if you wish to append or overwrite the previous contents of the file
        used for now only for sync log.
        :return: None if everything ok, else msg related to the problem of saving log
        """

        # define the file names and the folder
        logFolderName = 'logs'
        successFileName = 'success.txt'
        errorsFileName = 'errors.txt'
        checkSyncFileName = 'check_sync_log.txt'

        try:
            text = text.encode('utf8')  # encode the text. Needed for greek characters.

            # create the log folder, if it does not exist
            if not os.path.exists('logs'):
                os.makedirs(logFolderName)

            if logType == WooCommerceUpdater.LOG_TYPE_SUCCESS:  # case of successful log
                # create/open the file for appending adata
                successFile = open(os.path.join(logFolderName, successFileName), 'a+')  #
                # write the info into the file
                msgToWrite = 'Date: ' + str(datetime.datetime.now()) + '. ' + text + '\n'
                successFile.write(msgToWrite)
                # close the file
                successFile.close()
            elif logType == WooCommerceUpdater.LOG_TYPE_ERRORS:  # case of not log records for problems
                # create/open the file for appending adata
                errorsFile = open(os.path.join(logFolderName, errorsFileName), 'a+')  #
                # write the info into the file
                msgToWrite = 'Date: ' + str(datetime.datetime.now()) + '. ' + text + '\n'
                errorsFile.write(msgToWrite)
                # close the file
                errorsFile.close()
            elif logType == WooCommerceUpdater.LOG_TYPE_CHECK_SYNC:
                # create/open the file for data
                if isAppendMode:  # open for appending
                    syncLogFile = open(os.path.join(logFolderName, checkSyncFileName), 'a+')
                else:  # open for writing
                    syncLogFile = open(os.path.join(logFolderName, checkSyncFileName), 'w+')
                    # write the info into the file
                msgToWrite = 'Date: ' + str(datetime.datetime.now()) + '. ' + text + '\n'
                syncLogFile.write(msgToWrite)
                # close the file
                syncLogFile.close()
        except Exception, e:
            return 'Problem writing into log files'


