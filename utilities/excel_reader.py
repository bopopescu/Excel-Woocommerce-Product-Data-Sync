# -*- coding: utf-8 -*-

class ExcelReader:
    """
    Class responsible for handling some things related to excel files
    """

    FILE_COLUMN_NAMES = [u'Κωδικός', u'Μ.Μ', u'Λιανικής', u'Λιαν.τιμή 05', u'Υπολ.1']  # list of the file column names

    @staticmethod
    def isValid(fileName, columns=None):
        """
        Checks if the file is valid (meaning it can be imported to WooCommerce)
        :return:
        """

        if not fileName.endswith(('.xls', '.xlsx')):
            # not valid file type
            return False, u'Λάθος τύπος αρχείου'

        if not (columns == ExcelReader.FILE_COLUMN_NAMES or columns is None):
            # if the column names are not ok
            return False, u'Πρόβλημα με τις στήλες του αρχείου'

        return True, ''


