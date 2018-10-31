# -*- coding: utf-8 -*-
import unittest

from utilities.excel_reader import ExcelReader


class TestExcelFile(unittest.TestCase):

    def test_isValid(self):
        """
        tests the isValid method
        :return:
        """
        # Check if the filename corresponds to a valid Excel 97-2003 document (.xls) or a valid Excel document (.xlsx)
        fileName1 = 'c:/test.xlsx'  # Excel Document
        assert ExcelReader.isValid(fileName1) == True
        fileName2 = 'c:/test.xls'  # Excel 97-2003 Document
        assert ExcelReader.isValid(fileName2) == True
        fileName3 = 'c:/test.doc'  # another type of document, not valid for our application
        assert ExcelReader.isValid(fileName3) == False

        # Check if the number and names of the columns are the ones that are supposed to be
        fileColumnNames1 = (u'Κωδικς', u'Μ.Μ', u'Λιανικής', u'Λιαν.τιμή 05', u'Υπόλ.1')  # wrong names
        assert ExcelReader.isValid(fileName1, fileColumnNames1) == False
        fileColumnNames2 = (u'Κωδικός', u'Μ.Μ', u'Λιανικής', u'Λιαν.τιμή 05')  # wrong number of columns
        assert ExcelReader.isValid(fileName1, fileColumnNames2) == False
        fileColumnNames3 = (u'Κωδικός', u'Μ.Μ', u'Λιανικής', u'Λιαν.τιμή 05', u'Υπόλ.1')  # everything ok
        assert ExcelReader.isValid(fileName1, fileColumnNames3) == True
