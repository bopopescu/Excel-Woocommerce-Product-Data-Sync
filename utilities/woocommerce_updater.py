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
        df = pd.read_excel(excelFileName)  # read the file with pandas

        # put the column names in a list
        columns = []
        for col in df.columns:
            columns.append(col)
        # check the validity of the filename and columns
        fileValidityResult, validityErrorMessage = ExcelReader.isValid(excelFileName, columns)
        if fileValidityResult is False:  # if not valid, return False
            return False, u'Πρόβλημα με την ανάγνωση του αρχείου-'+validityErrorMessage
        else:  # if valid, then load data from the excel file and update WooCommerce

            # get data from the file into lists
            skuData = df[ExcelReader.FILE_COLUMN_NAMES[0]]
            unitData = df[ExcelReader.FILE_COLUMN_NAMES[1]]
            retailPrice1 = df[ExcelReader.FILE_COLUMN_NAMES[2]]
            retailPrice2 = df[ExcelReader.FILE_COLUMN_NAMES[3]]
            quantity = df[ExcelReader.FILE_COLUMN_NAMES[4]]

            # initialize the progress bar
            progressBar['maximum'] = len(skuData)

            # update WooCommerce
            try:
                cnx = mysql.connector.connect(  # open a mysql connection - for now it's the test database
                    user=DbCredentials.MYSQL_USER,  # new user created via plesk, with update permissions
                    password=DbCredentials.MYSQL_PASSWORD,
                    host=DbCredentials.MYSQL_HOST,
                    database=DbCredentials.MYSQL_DATABASE
                )

                # create the sql statement and execute
                for i in range(0, skuData.size):  # for each element that needs to be updated, update it

                    # update the e-shop price
                    if retailPrice2[i] > 0:  # if the e-shop price is a positive number
                        if retailPrice2[i] < retailPrice1[i]:
                            # update this price only if it is lower than the one of the shop
                            WooCommerceUpdater.updateElementData(skuData[i], '_sale_price', str(retailPrice2[i]), cnx)
                        elif retailPrice2[i] == retailPrice1[i]:
                            # update the _price field. Else, you won't see the price of the product
                            WooCommerceUpdater.updateElementData(skuData[i], '_price', str(retailPrice2[i]), cnx)
                            WooCommerceUpdater.updateElementData(skuData[i], '_sale_price', str(retailPrice2[i]), cnx)

                    # update the shop price
                    if retailPrice1[i] > 0:  # if the shop price is a positive number
                        WooCommerceUpdater.updateElementData(skuData[i], '_regular_price', str(retailPrice1[i]), cnx)

                    # update the stock
                    stock = quantity[i]
                    if stock < 0 or quantity.isna()[i]:
                        # if the stock is less than zero or contains the NaN value (pandas), then make it zero
                        stock = 0
                    WooCommerceUpdater.updateElementData(skuData[i], '_stock', str(stock), cnx)
                    WooCommerceUpdater.updateElementData(skuData[i], '_manage_stock', "'yes'", cnx)

                    # update the progress bar
                    progressBar['value'] = i
                    progressBar.update()

                    # update the status
                    lblStatus['text'] = str(i) + u' από ' +str(skuData.size)

                cnx.commit()
                cnx.close()  # close the database connection
            except Exception, e:
                # if any exception occurs, return False
                return False, u'Πρόβλημα με την ενημέρωση των τιμών'


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



