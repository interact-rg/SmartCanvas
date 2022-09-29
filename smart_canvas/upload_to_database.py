import mysql.connector
import datetime

'''
https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/
'''

def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def insert_blob(image_id, image, date_added):
    print("Inserting BLOB into images")
    #maybe add information of database from configuration file for safety.............
    #need checker for if id exists, increment by one until id does not exist etc etc.
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='smartcanvas',
                                             user='root',
                                             password='SmartCanvasV')

        cursor = connection.cursor()

        print(f"image_id is: {image_id}")
        sql_select_query = """SELECT * from images"""
        cursor.execute(sql_select_query)
        myresult = cursor.fetchall()
        #check if id exists in database:
        for row in myresult:
            if row[0] == image_id:
                image_id += 1

        sql_insert_blob_query = """ INSERT INTO images
                          (image_id, image, date_added) VALUES (%s,%s,%s)"""

        picture = convert_to_binary_data(image)

        # Convert data into tuple format
        print(f"image_id is now: {image_id}")
        insert_blob_tuple = (image_id, image, date_added)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Image and file inserted successfully as a BLOB into images table", result)

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

insert_blob(2, r"C:\Users\anssi\Desktop\shellcode.png", datetime.datetime.now())
