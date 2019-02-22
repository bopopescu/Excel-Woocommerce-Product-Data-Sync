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


    """
    MYSQL_USER = '...'
    MYSQL_PASSWORD = '...'
    MYSQL_DATABASE = '...'
    MYSQL_HOST = '...'
    """

    # test database
    TEST_MYSQL_USER = 'wooCommerceUser'
    TEST_MYSQL_PASSWORD = '95$Syva2'
    TEST_MYSQL_DATABASE = 'infoeraw192677_wordpress_q'
    TEST_MYSQL_HOST = '185.138.42.24'