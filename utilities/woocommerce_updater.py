# -*- coding: utf-8 -*-

# Resource for accessing excel data with pandas: https://pythonspot.com/read-excel-with-pandas/

import pandas as pd
import mysql.connector  # install mysql-connector-python

from app_config import DbCredentials
from utilities.excel_reader import ExcelReader


class WooCommerceUpdater:
    """
    class that updates woocommerce data
    """

    @staticmethod
    def importDataInWoocommerce(excelFileName, progressBar, lblStatus):
        """

        :param excelFileName: the file name of the excel file that will be imported
        :param progressBar: the progressbar showing the progress. The function will update it
        :param lblStatus: the label that will contain the status of the update
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
            return False, u'Πρόβλημα με την ανάγνωση του αρχείου-'+validityErrorMessage
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
                    skuIndex[skuData[i]] = i



                # update WooCommerce

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

                # initialize the progress bar
                progressBar['maximum'] = noOfSKUSSqlStatement

                noOfSkuCursor = cnx.cursor()
                noOfSkuCursor.execute(noOfSKUSSqlStatement)
                for a in noOfSkuCursor:
                    noOfSKUSinWoocommerce = a[0]

                # get the product skus that exist in the woocommerce database
                skuSqlStatement = "SELECT meta_value FROM `4mnHYjMa6v_postmeta` " \
                                  "WHERE meta_key = '_sku' and meta_value !=''"
                skuCursor = cnx.cursor()
                skuCursor.execute(skuSqlStatement)

                counter = 0  # counter that will be used for progress bar and status
                updatedCounter = 0  # counter only for the items whose sku was found in the excel file

                # for each product in the Woocommerce database, update the woocommerce product data
                # based on the data from the Excel file
                for productData in skuCursor:
                    sku = productData[0]  # get the product sku
                    counter = counter + 1  # increase the counter

                    # get the index of the product with the specific sku
                    # don't forget to remove z from the beginning
                    productIndex = skuIndex.get(sku.lstrip('z'))

                    # update the woocommerce data of the specific product
                    if productIndex is not None:  # if the product sku exists in the excel file, update product data
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

                    # update the progress bar
                    progressBar['value'] = counter
                    progressBar.update()

                    # update the status
                    lblStatus['text'] = u'Ενημερώνονται ' \
                                            + str(updatedCounter) + u' από ' + str(noOfSKUSinWoocommerce)

                cnx.commit()
                cnx.close()  # close the database connection
                return True, ''
            except Exception, e:
                # if any exception occurs, return False
                return False, u'Πρόβλημα με την ενημέρωση των τιμών. '  # + e.msg


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



