import mysql.connector
from mysql.connector import Error

###################################################################################       CONNECT TO THE DATABASE         ###########################################################################################################




def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host = 'cims.mysql.pythonanywhere-services.com',
            user = 'cims',
            password = '5498603Ma.',
            database = 'cims$default'
            )

        return connection
    except Error as e:
        print(f"The error '{e}' occured")
        return None

def create_db_connection_moment_logistics():
    try:
        connection = mysql.connector.connect(
            host = 'tuya.mysql.pythonanywhere-services.com',
            user = 'tuya',
            password = 'tuyadatabases',
            database = 'tuya$moment-logistics'
            )

        return connection
    except Error as e:
        print(f"The error '{e}' occured")
        return None