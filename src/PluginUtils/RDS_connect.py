import mysql.connector
from mysql.connector import Error

class RDSClient:
    def __init__(self):
        self.host = "plugin-db.c3aqee64crhq.us-east-1.rds.amazonaws.com"
        self.user = "admin"
        self.password = 'hilab12#'
        self.database = "gailbot"
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            # if self.connection.is_connected():
            #     print("Connected to RDS database")

        except Error as e:
            print(f"Error connecting to RDS: {e}")
            self.connection = None
    
    def fetch_plugin_s3_url(self, plugin_id):
        if self.connection is None:
            print("No database connection.")
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT s3_url FROM Plugins WHERE id = %s"
            cursor.execute(query, (plugin_id,))
            result = cursor.fetchone()

            if result:
                return result["s3_url"]
            else:
                print(f"No S3 URL found for plugin ID {plugin_id}")
                return None
        except Error as e:
            print(f"Error fetching S3 URL: {e}")
            return None
        finally:
            cursor.close()

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            # print("RDS connection closed")
