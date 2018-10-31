# -*- coding: utf-8 -*-
import unittest

import mysql.connector

from app_config import DbCredentials


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
