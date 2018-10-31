# -*- coding: utf-8 -*-

class ExcelFile:
    """
    Class responsible for handling some things related to excel files
    """

    FILE_COLUMN_NAMES = (u'Κωδικός', u'Μ.Μ', u'Λιανικής', u'Λιαν.τιμή 05', u'Υπόλ.1')  # list of the file column names

    @staticmethod
    def isValid(fileName, columns=None):
        """
        Checks if the file is valid (meaning it can be imported to WooCommerce)
        :return:
        """

        if fileName.endswith(('.xls', '.xlsx')) and (columns == ExcelFile.FILE_COLUMN_NAMES or columns is None):
            # if the filename is valid and the column names and number is ok, then return true
            return True
        else:
            # not valid filename
            return False


