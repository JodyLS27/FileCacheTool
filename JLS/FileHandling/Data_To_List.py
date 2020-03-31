import hou
import Read_And_Write

# You have to load the Class every time.
reload(Read_And_Write)
# from Data_To_List import DataToList as DTL
RW = Read_And_Write.JsonFileHandler()

class DataToList:

    def __init__(self):
        pass

    # This Method is used to create a Dictionary entry for each node of a specified Type.
    @staticmethod
    def getFileTypeDict(ndType):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), ndType)
        return nodeType

    @staticmethod
    def appendToDict(dictionary, dictKey, dictValue):
        a_dict = dictionary[dictKey] = dictValue
        return a_dict