import database


MAX_HEIGHT = 7 # maximum cupoid size in the diagram
# the protoDeclare class represents one whole protoDeclare tag in the html file
# the class saves the field nodes, appearance, form and the shape of the protoDeclare node.
class ProtoDeclare:
    def __init__(self, interface, body, soup):
        # in the constructor we are going through the complete protoDeclare tag and drag
        # out the important variables
        # self.soup = soup
        self.fieldDict = {} # the Dictonary for the field nodes
        for item in interface.find_all('field'):
            # in this for loop we get the field nodes from the protoInterface
            if item.appearance:
                # with the if statement we are checking the type of the item element because
                # we have to save not just a value for the type appearance
                self.fieldDict[item['name']] = Field(item.appearance)
            else:
                # for every other type then appearance we can save only a simple string
                self.fieldDict[item['name']] = Field(item)

        self.shape = body.shape # looking for the shape tag in the protoBody
        self.form = self.shape.find_next() # save the form of the x3dom object

    def setShapeAttrs(self, shape):
        # gets the shape of the protoInstance and add the attributes to the protoDeclare shape
        for key, value in shape.attrs.items():
            self.shape[key] = value


    def setFieldValue(self, instance):
        # adds the attributes from the protoDeclare and protoInstance fieldValue together and executes
        # an sql query if necessary
        protoFieldNode = self.fieldDict[instance['name']] # looking for the same fieldValue in the
        # protoDeclare class
        if 'sql' in instance.attrs.keys(): # if the fieldValue has an sql attribute it has to
            # execute an sql que ry to get the necessary data
            name, value = self.__getValueFromDB(instance)
            del instance.attrs['sql'] # after the database connection the sql attribute must be deleted
            protoFieldNode.putValueInField(name, value) # adds the name of the attribute and the value
            # to the fieldValue
        if protoFieldNode.getTag().name=='appearance':
            if instance.appearance:
                # if both the protoDeclare and the protoInstance fieldValue has an appearance tag,
                # the appearance and the material attributes from the protoDeclare and protoInstance
                # must be put together. First we get the attributes from protoDeclare and protoInstance
                # and save them into variables, then we loop through the instance Appearance or the
                # instance material attributes and add them to the declare Appearance or declare material
                # attributes
                instanceAppearanceDict = instance.appearance.attrs
                instanceMaterialDict = instance.appearance.material.attrs
                protoAppearanceDict = protoFieldNode.getTag().appearance.attrs
                protoMaterialDict = protoFieldNode.getTag().appearance.material.attrs
                for key, value in instanceAppearanceDict:
                    protoAppearanceDict[key] = value
                for key, value in instanceMaterialDict:
                    protoMaterialDict[key] = value
                protoFieldNode.getTag().appearance.attrs = protoAppearanceDict # finally we put the
                # joined attributes to the proto fieldValue
                protoFieldNode.getTag().appearance.material.attrs = protoMaterialDict
                # finally we put the joined attributes to the proto fieldValue
        else:
            # this block does almost the same as in the if clause before, but the difference is
            # there is only one tag in this fieldValue because the appearance tag includes an
            # additional material tag to define the look of the x3dom object
            protoDict = protoFieldNode.getTag().attrs
            instanceDict = instance.attrs
            for key, value in instanceDict.items():
                protoDict[key] = value
            protoFieldNode.getTag().attrs = protoDict



    def __getValueFromDB(self,instance):
        # this method executes the server side include, it gets an sql instance and mold them to a
        # sql query for the database and it gets the name of the attribute in which we will save
        # the return data from the database
        query = instance['sql']
        query = query.split()
        posInto = query.index('INTO') # looking for the position of the 'Into' statement to get the
        # name of the attribute
        nameIndex = posInto+1 # the position of the actual attribute
        name = query[nameIndex] # get the name of the actual attribute
        query.pop(posInto) # delete the 'INTO' statement from the query
        query.pop(posInto) # delete the name of the attribute from the query
        queryString = ''
        for string in query: # put together the query string for the database
            queryString += string + ' '
        value = database.postgreSQLConnection(queryString)
        # get the data from the database and prepare the data because we get a python set back from the
        # database but we only need one value
        value = value[0]
        value = value.replace(',',' ')
        if 'Resultat' in queryString:
            one_percent = MAX_HEIGHT / 100  # the size of one percent of the MAX_HEIGHT value
            value = float(value) * one_percent  # calculate the height of the cupoid
            value = round(value, 2)  # format the float value
            value = str(value)  # parse the value to string
            value = '1 '+value+' 1' # change the attribute value to the necessary form for X3DOM
        return (name, value)


    def getX3DomNode(self):
        # this method puts together the final x3dom node for the client
        for key, value in self.fieldDict.items(): # going through all the field Values of the protoDeclare
            # class
            if value.getTag().name=='appearance': # first we look for the appearance fieldValue in the
                # protoDeclare class because we need the whole appearance tag for the x3dom node
                appeaerance = value
                self.fieldDict.pop(key) # after we found the appearance tag we can delete the tag
                # in the field Dictionary and we can stop the loop
                break
        self.shape.append(appeaerance.getTag()) # adding the appearance tag to the shape tag from the
        # protoDeclare class
        for value in self.fieldDict.values(): # going through the values of the field value dictionary
            # to get all the attributes for the form of the x3dom object.
            del value.getTag().attrs['name'] # we don't want to add the attribute 'name' from every
            # fieldValue to the form so we must delete that attribute beforehand
            for key, value in value.getTag().attrs.items(): # now we can add all of the attributes
                # to the form of the protoDeclare class
                self.form.attrs[key] = value
        self.shape.append(self.form) # at the end we add the form filled with all the attributes to the
        # shape tag of the protoDeclare class
        return self.shape


# the class represents the field values in the protoDeclare class
class Field:
    def __init__(self, fieldTag): # in the constructor we save the fieldValue tag from the html file
        self.fieldTag = fieldTag

    def getTag(self):
        return self.fieldTag

    def putValueInField(self, name, value): # saves attributes represented by the variable value into the
        # fieldValue tag with the given name
        if "." in name: # the sql attribute has an 'INTO' statement which sometimes has names separated
            # by dot and we must distinguish between these names.
            name = name.split('.')
            if name[0]=='appearance':
                self.fieldTag.attrs[name[1]] = value
            else:
                self.fieldTag.material.attrs[name[1]] = value
        else:
            self.fieldTag.attrs[name] = value

    def name(self):
        return self.fieldTag