import sys
import hou
import nodesearch


# Custom Classes
import Data_To_List
import Read_And_Write

# You have to load the Class every time.
reload(Data_To_List)
reload(Read_And_Write)

# from Data_To_List import DataToList as DTL
DTL = Data_To_List.DataToList()
RW = Read_And_Write.JsonFileHandler()

class CommonFunctions:    

    # Initilizations
    def __init__(self):
        pass

    # ---------------------------------------------------------------------
    # LOOPS
    # ---------------------------------------------------------------------    

    # cacheNodes
    @staticmethod
    def getNodeNameAndPathFromDict(dictionary = {}, nodeType = ""):
        nodes = {}
        nameAndPathDict = {}

        # Checking if the incoming dictionary is empty
        if dictionary != dict():
            nodes = dictionary
        else:
            if nodeType != "":
                nodes = DTL.getFileTypeDict(nodeType)            
            
        # Running for Loop to return the Name and Path of the Dictionary.
        # instances is used to get each element in the dict.
        for element in nodes.instances():
            path = str(element.path())
            name = str(element.name())

            nameAndPathDict[path] = name
            
        return nameAndPathDict
     
    
    # ---------------------------------------------------------------------
    # COMMON RETURNS
    # --------------------------------------------------------------------- 

    # This finds all nodes with this Type in your scene. --> Returns Dict
    # NOTE: THIS IS ONLY AT SOP LEVEL.
    @staticmethod
    def findAllNodeType(ndType):
        return DTL.getFileTypeDict(ndType)
        #return hou.nodeType(hou.sopNodeTypeCategory(), ndType)
        
    
    # Returns all nodes at the given Directory Path. --> Returns tuple
    @staticmethod
    def getAllNodes(directory):
        # Empty Tuple Type
        lst = list()
        for node in directory.allItems():
            lst.append(node)
        return tuple(lst)

    # Returns the current path of your Hip file with the option to remove the hipFileName.hip so you can work with its directory.
    @staticmethod
    def getHipPath(removeHipName=False):
        hipPath = hou.hipFile.path()
        hipName = hou.hipFile.basename()
        path = hipPath
        
        # This is to check if there will be a split and return on the path and exclude the hipName.
        if(removeHipName == True):
            path = hipPath.split(hipName)[0]    
        
        return path


    # ---------------------------------------------------------------------
    # DATA READ AND WRITE
    # ---------------------------------------------------------------------  
    #JSON

    # Sending the Data through to the Read and Write file to Write the JSON File to Disk.
    @staticmethod
    def saveToJsonFile(dictList, file, path):
        RW.jsonWrite(dictList, file, path)

    # Retriving Data from the JSON File.
    @staticmethod
    def readFromJsonFile(file, path):
        return RW.jsonRead(file, path)

    # ---------------------------------------------------------------------
    # CONVERTS
    # --------------------------------------------------------------------- 

    @staticmethod
    def dictToList(dictionary):
        lst = []
        for key, value in dictionary.iteritems():
            lst.append({"path":key, "name":value})

        return lst

    @staticmethod
    def listToDict(list):
        lst = []
        for key, value in list.iteritems():
            lst.append({"path":key, "name":value})

        return lst