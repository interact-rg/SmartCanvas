""" database.py """

import mysql.connector
import datetime
import typing
from PIL import Image as im
import os


class Database:
    def convert_image_to_binary(self, filename) -> bytes:
        # Convert digital data to binary format
        with open(filename, "rb") as file:
            binaryData = file.read()
        return binaryData

    def insert_blob(self, image):

        print("Inserting BLOB into images table")
        # create image object of numpy array
        data = im.fromarray(image)
        data.save(
            "assets\picwithcanvas.png"
        )  # remove this later, no need to save locally.
        image_id = 1
        date_added = datetime.datetime.now()
        # maybe add information of database from configuration file for safety.............
        try:
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="canvas",
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

            image = self.convert_image_to_binary(r"assets\picwithcanvas.png")

            # Convert data into tuple format
            print(f"image_id is: {image_id}")
            insert_blob_tuple = (image_id, image, date_added)
            result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
            connection.commit()
            print("Image and file inserted successfully as a BLOB into images table")
            if os.path.exists(r"assets\picwithcanvas.png"):
                os.remove(r"assets\picwithcanvas.png")
            else:
                print("The file does not exist")

        except mysql.connector.Error as error:
            print("Failed inserting BLOB data into MySQL table {}".format(error))
            image_id = None

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

        return image_id

    #  function to convert binary to image
    def convert_binary_to_image(self, data: bytes, file_name: str):
        # Convert binary format to images
        # or files data(with given file_name)
        with open(file_name, "wb") as file:
            file.write(data)

    # download image with given id
    def download(self, image_id: int):
        image, date = None, None
        try:
            # establish connection
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="canvas",
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
                date = row[2]
                print("date  =", date)

            if image:
                # Pass path with filename where we want to save our file
                self.convert_binary_to_image(image, r"assets\downloadedimage.png")
                print("Successfully Retrieved Values from database")

        except mysql.connector.Error as error:
            print(format(error))
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
            return image, date

    def delete(self):
        # function to check if database has items older than a week.
        print("accessed through thread, lets try")
        try:
            # establish connection
            connection = mysql.connector.connect(
                host="localhost",
                database="smartcanvas",
                user="canvas",
                password="SmartCanvasV",
            )
            cursor = connection.cursor()
            
            sql_delete_query = f""" Delete from images where date_added < now() - interval 1 week;"""


            cursor.execute(sql_delete_query)
            result = cursor.fetchall()

            print("Successfully deleted Values from database")

        except mysql.connector.Error as error:
            print(format(error))
        pass


base = Database()
#base.download(38)
