""" database.py """

import mysql.connector
import datetime



class Database:
    def convert_image_to_binary(self, filename):
        # Convert digital data to binary format
        with open(filename, "rb") as file:
            binaryData = file.read()
        return binaryData

    def insert_blob(self, image_id, image, date_added):
        print("Inserting BLOB into images table")
        # maybe add information of database from configuration file for safety.............
        # need checker for if id exists, increment by one until id does not exist etc etc.
        try:
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="root",
                password="SmartCanvasV",
            )

            cursor = connection.cursor()

            sql_select_query = """SELECT * from images"""
            cursor.execute(sql_select_query)
            myresult = cursor.fetchall()
            # check if id exists in database:
            for row in myresult:
                if row[0] == image_id:
                    image_id += 1

            sql_insert_blob_query = """ INSERT INTO images
                            (image_id, image, date_added) VALUES (%s,%s,%s)"""

            image = self.convert_image_to_binary(image)

            # Convert data into tuple format
            print(f"image_id is: {image_id}")
            insert_blob_tuple = (image_id, image, date_added)
            result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
            connection.commit()
            print("Image and file inserted successfully as a BLOB into images table")

        except mysql.connector.Error as error:
            print("Failed inserting BLOB data into MySQL table {}".format(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    #  function to convert binary to image
    def convert_binary_to_image(self, data, file_name):
        # Convert binary format to images
        # or files data(with given file_name)
        with open(file_name, "wb") as file:
            file.write(data)

    # download image with given id
    def download(self, image_id):
        try:
            # establish connection
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="root",
                password="SmartCanvasV",
            )
            cursor = connection.cursor()
            # getting data by id value
            query = """ SELECT * from images where image_id = %s """

            cursor.execute(query, (image_id,))
            result = cursor.fetchall()
            for row in result:
                print("image Id = ", row[0])
                image = row[1]
                print("date  = ", row[2])
                # Pass path with filename where we want to save our file
            self.convert_binary_to_image(
                image, r"C:\Users\anssi\Pictures\testimages\image.png"
            )
            # Pass path with filename where we want to save our file

            print("Successfully Retrieved Values from database")

        except mysql.connector.Error as error:
            print(format(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def access(self, image_id):
        # function to delete image when its accessed in the database
        # work in prog
        try:
            # establish connection
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="root",
                password="SmartCanvasV",
            )
            cursor = connection.cursor()
            # getting data by id value
            sql_delete_query = f""" DELETE FROM images WHERE image_id = {image_id}"""

            cursor.execute(sql_delete_query, (image_id,))
            result = cursor.fetchall()
            for row in result:
                print("image Id = ", row[0])
                image = row[1]
                print("date  = ", row[2])

            self.convert_binary_to_image(
                image, r"C:\Users\anssi\Pictures\testimages\image.png"
            )
            print("Successfully Retrieved Values from database")

        except mysql.connector.Error as error:
            print(format(error))
        pass


base = Database()

base.insert_blob(2, r"tests\test_assets\small_image\image.png", datetime.datetime.now())
base.download(17)
