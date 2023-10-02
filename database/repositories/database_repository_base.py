import MySQLdb as sqlclient
from keyring import get_password


class BaseDatabaseRepository:
    __username = "t07913wn"

    def __init__(self):
        """Connects to DB and sets up objects for other methods"""

        try:
            self.db = sqlclient.connect(
                host="dbhost.cs.man.ac.uk",
                user=self.__username,
                password=get_password(
                    "database",
                    self.__username), database="2020_comp10120_y11")

            self.cursor = self.db.cursor()

        except BaseException:  # If connection fails
            print("SQL connection failed.")
            raise Exception

    def __del__(self):
        """Closes DB connection when object is destroyed"""
        self.db.close()

    def close(self):
        """Close the DB connection manually"""
        self.__del__()
