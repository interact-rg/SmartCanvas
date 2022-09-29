# import module
import mysql.connector

'''https://www.geeksforgeeks.org/how-to-read-image-from-sql-using-python/'''

#  function to convert data
def convert_data(data, file_name):
    # Convert binary format to images
    # or files data(with given file_name)
    with open(file_name, 'wb') as file:
        file.write(data)


#download image with given id
def download(image_id):
    try:
        # establish connection
        connection = mysql.connector.connect(host='localhost',
                                            database='smartcanvas',
                                            user='root',
                                            password='SmartCanvasV')
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
            convert_data(image, r"C:\Users\anssi\Pictures\testimages\image.png")
            # Pass path with filename where we want to save our file
    
        print("Successfully Retrieved Values from database")
    
    except mysql.connector.Error as error:
        print(format(error))
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
download(2)