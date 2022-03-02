import mysql.connector
from datetime import datetime
from chat import sentence
from chat import reply

try:
    mydb = mysql.connector.connect(host="localhost", user="root", password="", database="face_rec")

    cursor = mydb.cursor()
    cursor.execute("CREATE TABLE chat(Convo_ID int AUTO_INCREMENT, Question varchar(1000), Answer varchar(1000))")
    cursor.execute("INSERT INTO chat (Questions, Answers) VALUES (%s,%s);" % (sentence, reply))

    mydb.commit()
    mydb.close

except:
    print("Database connection exception!")

