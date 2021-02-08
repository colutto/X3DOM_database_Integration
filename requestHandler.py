from __future__ import division, unicode_literals
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from ProtoDeclare import ProtoDeclare
import json
import database
from copy import deepcopy
import os
import sys
MAX_HEIGHT = 7 # maximum cupoid size in the diagram
# this class puts together the response for the client request and sends the response back
# to the client
class MyRequestHandler(BaseHTTPRequestHandler):
    # the do_GET method is for the normal client http request and it does the server side include for
    # the x3dom scene
    def do_GET(self):
        # put together the response header for the client
        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.end_headers()
        # open the html file to check if there are nodes which needs a server side include support
        print('dir' + os.getcwd())
        script_dir = os.path.dirname(__file__)
        rel_path = 'index.html'
        abs_path = os.path.join(script_dir, rel_path)
        with open(abs_path, 'r+b') as f:
            contents = f.read()
            soup = BeautifulSoup(contents, 'lxml')
            protoNodes = soup.find_all('protodeclare')
            # searching for all protoDeclare nodes because we have to define those nodes
            # and put them in the right place in the html body.
            protoDict = {} # includes all the generated protoDeclare classes
            for protoNode in protoNodes:
                # in this loop we are going through every protoDeclare node, create for
                # every one a protoDeclare class and save this class in the dictionary under the given name
                # in the html file
                protoDict[protoNode['name']] = ProtoDeclare(protoNode.protointerface, protoNode.protobody, soup)
            protoInstances = soup.find_all('protoinstance')
            # searching for all protoInstances because they give us the exact place and amount of x3dom shapes
            # in the html file and they give us additional features.
            for item in protoInstances: # going through every protoInstance tag
                protoDeclareNode = deepcopy(protoDict[item['name']]) # get a copy of a protoDeclare object
                # with the same name as the protoInstance. we have to create a copy of the protoDeclare
                # object because we have only one protoDeclare object for several protoInstances.
                fieldValues = item.find_all('fieldvalue') # find all fieldValue tags in the protoInstance
                for fieldValue in fieldValues: # going through every fieldValues in the protoInstance
                    protoDeclareNode.setFieldValue(fieldValue) # adds the field tag from the protoDeclare class
                    # and the fieldValue from the protoInstance together, if necessary it executes a server
                    # side include.
                result = protoDeclareNode.getX3DomNode() # puts together the final x3dom object for the html
                # file which the client will get as a response
                parent = item.parent # get the parent tag from the protoInstance
                if parent.name=='shape': # if the parent is a shape tag then we must save the attributes of
                    # this parent in the protoDeclare class because in the protoDeclare class there is
                    # already a shape tag
                    protoDeclareNode.setShapeAttrs(parent) # the parent attributes are saved in the
                    # protoDeclare class
                    shape = parent
                    parent = parent.parent # parent variable get the enclosing tag from the shape
                    shape.decompose() # deletes the shape
                item.decompose() # deletes the protoInstance tag
                parent.append(result) # the parent variable adds the x3dom object which was build in the
                # getX3DomNode() method
            for protoNode in protoNodes:
                protoNode.decompose() # delete all the protoDeclare Nodes from the html file because the client
                # doesn't need them
            self.wfile.write(soup.encode()) # the resulting html file will be send to the client
            del protoDict

    def do_POST(self):
        # the do_Post method is only there for the runtimeNodes which is implemented with java script on the
        # client side and this method on the server side
        content_len = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_len) # read the message from the client
        body = json.loads(body) # transform the json dictionary in a python dictionary
        query = '' # the query for the database is at the beginning empty
        for key, value in body.items(): # going through all the values and keys in the
            # dictionary from the client
            if key=='WHERE': # the where part of the database query needs special treatment
                value = body[key]
                value = value.split('=')
                query += key + ' ' + value[0] + '=\'' + value[1] + '\' '
                # the value part of the where key has most of the time an equal sign in it
                # one must separate this two parts right and left from the equal sign and put them
                # together in a different way to get the query right.
            else: # if it's not the where part of the query you can add them to the query variable
                query += key+' '+value+' '
        value = database.postgreSQLConnection(query) # send the query to the database and get the answer
        value = value[0]
        value = value.replace(',', ' ')
        one_percent = MAX_HEIGHT / 100  # the size of one percent of the MAX_HEIGHT value
        value = float(value) * one_percent # calculate the height of the cupoid
        value = round(value,2) # format the float value
        value = str(value) # parse the value to string
        value = '1 ' + value + ' 1'  # change the attribute value to the necessary form for X3DOM
        json_response = json.dumps(value) # prepare the answer with json for the client
        self.send_response(200)
        self.send_header('Content-type', 'json-Object')
        self.end_headers()
        self.wfile.write(json_response.encode()) # send the response to the client


