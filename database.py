import psycopg2

# this method sends a query to the database and gets the data from the database back.
def postgreSQLConnection(query):
    try:
        connection = psycopg2.connect(user='postgres', password='123', host='10.0.0.11', port='5432', database='postgres')
        # first we need a connection to the database and this connection is saved into the variable connection
        cursor = connection.cursor()  # we need a cursor to execute sql queries
        cursor.execute(query)  # sends the query to the database
        result = cursor.fetchone()  # gets the data from the database back
    except(Exception, psycopg2.Error) as error: # if we can't get a connection to the database for different reasons
        # we catch the exception and print a message in the console.
        print('Error while connecting to PostgreSQL', error)
    finally:  # the finally statement closes the database connection after every session.
        if connection:
            cursor.close()
            connection.close()
            return result

