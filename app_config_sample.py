"""
Sample File that stores some configuration
Steps:
a) Replace ... with your configuration data
b) Rename file to app_config.py
"""


class LoginCredentials:
    # credentials for logging in the application
    USERNAME = '...'
    PASSWORD_HASH = '...'  # password hash using sha224


class DbCredentials:
    """
    Class storing some db credentials
    """

    # operational database
    MYSQL_USER = '...'
    MYSQL_PASSWORD = '...'
    MYSQL_DATABASE = '...'
    MYSQL_HOST = '...'


    # test database
    TEST_MYSQL_USER = '...'
    TEST_MYSQL_PASSWORD = '...'
    TEST_MYSQL_DATABASE = '...'
    TEST_MYSQL_HOST = '...'