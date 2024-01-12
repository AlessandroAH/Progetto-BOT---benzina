import mysql.connector
from mysql.connector import Error

class DataBase:
    #self è una referenza all'istanza dell'oggetto stesso.
    # Viene passato automaticamente a tutti i metodi di una classe in Python, incluso il metodo init, e viene utilizzato per accedereagli attributi e ai metodi dell'istanza.
    def __init__(self, host, user, password, database):
        self.myDB = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
    def esegui_query(self, query):
        try:
            if self.myDB.is_connected():
                # print("Query:", query)
                cursor = self.myDB.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                # print("Risultato della query:", result)
                self.myDB.commit()
                return result
            else:
                print("Errore durante l'esecuzione della query")
                return None
        except Error as e:
            print("Errore: ", e)
            return None