from http.server import HTTPServer
import requestHandler
from socketserver import ThreadingMixIn
import clientTrigger
import dbTrigger
import sys

sys.setrecursionlimit(10000)


address = ('', 80) # address and port of the server
handler = requestHandler.MyRequestHandler

triggerClient_Thread = clientTrigger.triggerClient_Thread() # triggerClient_Thread is for the websocket
# connection to the client for sending messages if the database get an update
triggerClient_Thread.setDaemon(True) # with setDaemon the triggerClient_Thread stops if the main thread stops
triggerClient_Thread.start()

triggerDB_Thread = dbTrigger.triggerDB_Thread() # triggerDB_Thread is for the notification system with the
# postgresql Database.
triggerDB_Thread.setDaemon(True) # with setDaemon the triggerDB_Thread stops if the main thread stops
triggerDB_Thread.start()



class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass
server = ThreadingHTTPServer(address, handler)
print('server works')
try:
    server.serve_forever()
except (KeyboardInterrupt, SystemExit):
    print('shutdown Server')



