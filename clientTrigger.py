import asyncio
import websockets
import json
import dbTrigger
import threading

# this class creates an independent thread because we need to receive messages from the client
# if he wants to get notifications or not. the synchronization with the dbTrigger class is
# implemented with the 'Queue' class. with the queue one can sign up or sign off from the notification
# system
class triggerClient_Thread(threading.Thread):
    def __init__(self): # in the constructor we call the constructor of the inherited class thread and
        # we define the address of the websocket for sending and receiving messages and we also need the
        # event loop for the websocket.
        super().__init__()
        self.addressWebsocket = ('', 9999)
        self.loop = asyncio.new_event_loop()

    def run(self): # the override run method of the thread class is to receive and send messages between
        # the client and the server
        asyncio.set_event_loop(self.loop)
        print('clientTrigger works')

        async def connect(websocket, path):
            queue = Queue()
            consumer_task = asyncio.ensure_future(receivMessages(websocket, queue))
            producer_task = asyncio.ensure_future(sendMessage(websocket, queue))
            done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,)
            for task in pending:
                task.cancel()
        start_server = websockets.serve(connect, self.addressWebsocket[0], self.addressWebsocket[1])
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


async def receivMessages(websocket, queue): # this method is for receiving messages from the client.
    # the client can sign up or sign off from the notification system. every client has a queue
    # which will be either added or removed to the dbTrigger queue list.
    async for message in websocket:
        message = json.loads(message)
        method = message['Method']
        if method == 'add':
            dbTrigger.addQueue(queue)
        elif method == 'remove':
            dbTrigger.removeQueue(queue)


async def sendMessage(websocket, queue): # if the client has signed up to the notification system, this
    # method will send a notification to the client.
    while True:
        await asyncio.sleep(1) # with this expression the loop will wait for one second, so the
        # receiveMessages method can have some time to execute the code for sign up or sign off messages
        # from the client
        message = queue.getElem()
        if message:
            await websocket.send(message)


class Queue: # every client - server websocket connection has a queue to get notifications
    def __init__(self):
        self.queue = list()

    def getElem(self):
        if self.queue:
            return self.queue.pop()

    def insertElem(self, object):
        self.queue.insert(0, object)

    def print(self):
        for elem in self.queue:
            print(elem)