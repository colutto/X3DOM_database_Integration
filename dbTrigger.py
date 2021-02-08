import psycopg2
import json
import threading

queueSet = list()

# this class creates an independent thread because for the trigger Server we have to create a while
# loop which can react to a database notification and save this notification in a queue.
class triggerDB_Thread(threading.Thread):
    def run(self): # the override run method of the thread class includes the complete while loop for the
        # notification system between the server and the database
        print('dbTrigger works')
        connection = psycopg2.connect(user='postgres', password='123', host='10.0.0.11', port='5432', database='postgres')
        # first we need a connection to the database and this connection is saved into the variable connection
        cur = connection.cursor() # we need a cursor to execute sql queries
        cur.execute('LISTEN events;') # to connect to the notification system of the database, and we
        # listen to the event called 'events'.
        while True: # this is the actual while loop to get a notification if the
            # function public.notify_event() in the database is called with a trigger in the database.
            connection.poll()
            connection.commit()
            while connection.notifies:
                notify = connection.notifies.pop() # this is the method where we get the notification from the
                # database
                message = json.loads(notify.payload) # the notification is a json type message and has to be
                # transformed to a python dictionary
                tableName = message['table'] # we need the table name from the notification because we send
                # the name to the client. with the name the client can find the form which needs an update.
                for queues in queueSet: # in this loop every queue which is signed up gets the notification
                    queues.insertElem(tableName)



def addQueue(queue): # in this method we add a queue from the clientTrigger class to the list of queues
    # which will get a notification
    if queue not in queueSet:
        queueSet.append(queue)



def removeQueue(queue): # in this method we remove a queue from the clientTrigger class from the list of
    # queues, after that the queue won't get notifications
    if queue in queueSet:
        queueSet.remove(queue)


