import os
import json

# The object passed through here will be the JSON File.
class JsonFileHandler:

    # Initialize Method.
    def __init__(self):
        pass

    # ---------------------------------------------------------------------
    # READ AND WRITE
    # ---------------------------------------------------------------------  
    @staticmethod
    def jsonWrite(data, file, path):
        # Checking to see if the path and Directories exists, If not, Create the Directories.
        # We do not need to create the file as the dump function dose that for us if it dose not exist.
        if not os.path.exists(path):
            os.makedirs(path)

        # Combining the File and Path together as the JSON Write formate needs a file to write to.
        # This fill must be its path and filename.json.
        filePath = "{0}{1}.json".format(path, file)

        with open(filePath, 'w') as jsonFile:
            json.dump(data, jsonFile)


    # Returning a Dictionary from the JSON file.
    @staticmethod
    def jsonRead(file, path):
        # Creating the Full Path here because we want to make sure the Directories and JSON File Exists before reading it in.
        # Creating an empty dictionary to return.
        path = "{0}{1}.json".format(path, file)
        data = {}
        
        if not os.path.exists(path):
            # If the path and file dose not exist, we want to return an empty dictionary.
            pass
        else:            
            with open(path, 'r') as jsonFile:
                data = json.load(jsonFile)
        return data