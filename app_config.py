"""
File that stores some configuration
"""


class LoginCredentials:
    """
    Class for storing the credentials used when logging in the application
    """
    USERNAME = 'captain'
    PASSWORD_HASH = '64610dc7f1d1b871a5c048fae4c86d8f710791fd25b8cd1de07bca35'  # password hash using sha224

class DbCredentials:
    """
    Class storing some db credentials
    """

    # operational database
    MYSQL_USER = 'infoe_wcupdater'
    MYSQL_PASSWORD = 'x7C1kt5!'
    MYSQL_DATABASE = 'infoeraw758582_captain_eshop'
    MYSQL_HOST = '185.138.42.30'


    """
    MYSQL_USER = 'wooCommerceUser'
    MYSQL_PASSWORD = '95$Syva2'
    MYSQL_DATABASE = 'infoeraw192677_wordpress_q'
    MYSQL_HOST = '185.138.42.24'
    """

    # test database
    TEST_MYSQL_USER = 'wooCommerceUser'
    TEST_MYSQL_PASSWORD = '95$Syva2'
    TEST_MYSQL_DATABASE = 'infoeraw192677_wordpress_q'
    TEST_MYSQL_HOST = '185.138.42.24'