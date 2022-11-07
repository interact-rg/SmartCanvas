""" database.py """
import sqlite3
import datetime
import typing
from PIL import Image as im
import os


class Database:

    def create_database(self):
        print("Creating database...")
        connection = sqlite3.connect('database.db')
        with open('smart_canvas\schema.sql') as f:
            connection.executescript(f.read())
        cursor = connection.cursor()

        #check if database exists
        cursor.execute("SHOW DATABASES")
        for x in cursor:
            #error if database doesn't exist
            print(x)
        cursor.execute("CREATE DATABASE smartcanvas")


        cursor.execute('''CREATE TABLE images (
        image_id int,
        image mediumblob,
        date_added date
        );''')

        sql_select_query = """SELECT * from images"""
        cursor.execute(sql_select_query)
        myresult = cursor.fetchall()


        if connection.is_connected():
            cursor.close()
            connection.close()
            print("SQLite connection is closed")


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
        connection = sqlite3.connect('database.db')

        cursor = connection.cursor()

        sql_select_query = """SELECT * from images"""
        cursor.execute(sql_select_query)
        myresult = cursor.fetchall()
        # check if id exists in database:
        for row in myresult:
            if row[0] == image_id:
                image_id += 1

        sql_insert_blob_query = """ INSERT INTO images
                                (image_id, image, date_added) VALUES (?, ?, ?)"""

        image = self.convert_image_to_binary(r"assets\picwithcanvas.png")

        image = r"test_assets/finger_pictures"
        # Convert data into tuple format
        data_tuple = (image_id, image, date_added)
        cursor.execute(sql_insert_blob_query, data_tuple)

        connection.commit()
        print("Image inserted successfully as a BLOB into images table")
        #delete image that was sent to database<
        if os.path.exists(r"assets\picwithcanvas.png"): 
            os.remove(r"assets\picwithcanvas.png")
        else:
            print("The file does not exist")


        if connection.is_connected():
            cursor.close()
            connection.close()
            print("SQLITE connection is closed")

    #  function to convert binary to image
    def convert_binary_to_image(self, data: bytes, file_name: str):
        # Convert binary format to images
        # or files data(with given file_name)
        with open(file_name, "wb") as file:
            file.write(data)

    # download image with given id
    def download(self, image_id: int):
        # establish connection
        connection = sqlite3.connect('database.db')
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
        self.convert_binary_to_image(image, r"assets\downloadedimage.png")
        print("Successfully Retrieved Values from database")

        if connection.is_connected():
            cursor.close()
            connection.close()
            print("SQLite connection is closed")

    def delete(self):
        # function to check if database has items older than a week.
        # establish connection
        print("Deleting values older than week ")
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        sql_delete_query = f""" DELETE FROM images WHERE date_added <= date('now', '-10 day');"""


        cursor.execute(sql_delete_query)
        result = cursor.fetchall()
        #check if something was actually deleted:
        for x in result:
            print(x)

        print("Successfully deleted Values from database")


base = Database()
#base.download(38)
