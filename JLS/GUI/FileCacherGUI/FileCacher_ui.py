import os
import sys
import hou
import collections

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from JLS.FileHandling import CommonFunctions as CommonFunctions
reload(CommonFunctions)
CF = CommonFunctions.CommonFunctions()

# ---------------------------------------------------------------------
    # CUSTOM DRAG AND DROP - QListWidget
# ---------------------------------------------------------------------    

class MainWindow(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.WindowStaysOnTopHint)
        
        # Call initialize UI function.
        # Just doing a load of the current JSON File with no checks.
        self.init_ui()
        self.jsonDictUpdate(firstLoad=True)
        self.jsonDictCheck()

    # ---------------------------------------------------------------------
    # CUSTOM EVENTS
    # ---------------------------------------------------------------------
    # CLOSE
    def closeEvent(self, event):

        # Get the Latest List and store in a Lictionary.
        dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))

        # Create an Ordered Dictionary.
        # Getting the Dictionary from the JSON File.
        dictJson = collections.OrderedDict()
        dictListJson = self.readListOrder()
        
        # Taking the [ Key ] / [ Value ] pair from the JSON File and storing it in the Ordered Dictionary.
        for item in dictListJson:
                dictJson[item["path"]] = item["name"]

        # Checking to see if there are any file cache nodes that are new and have not been added to the JSON File.
        # Checking to see if there are any file cache nodes in the JSON File which have been deleted from the Netwrok view.
        fileCacheNotStored = { k : dictFoundNodes[k] for k in set(dictFoundNodes) - set(dictJson) }
        deletedNodes = { k : dictJson[k] for k in set(dictJson) - set(dictFoundNodes) }

        if fileCacheNotStored != {} or deletedNodes != {}:
            dialog = False # hou.ui.displayConfirmation(text="You have Unsaved Changes, do you want to exit with out saving ?", buttons=("YES", "NO"))
            message = hou.ui.displayMessage(text="You have Unsaved Changes, do you want to save before exiting ?", buttons=("Yes", "No", "Cancel"))

            if message == 0:
                
                # Check to see if the fileCachNotFound Dict have any values, If it dose, then update the Dictionary with those values.
                # if fileCacheNotStored != {}:
                #     dictJson.update(fileCacheNotStored)                    

                # # Check if the deletedNodes Dict has any values, if it dose, then go into the Json Dict and remove that item.
                # if deletedNodes != {}:
                #     for key, value in deletedNodes.iteritems():
                #         dictJson.pop(key)

                # # Converting the Updated Orderd JSON Dict to a list to store its order.
                # lst = CF.dictToList(dictJson)

                # # Save the List Dict to a JSON File.
                # # Update the QTList with the list items.
                # self.saveListOrder(lst)
                # self.setJsonListText(lst)
                jsonDictUpdate()
                event.accept()
                
            elif message == 1:
                # This will close the window without Saving.
                event.accept()

            elif message == 2:
                # This will cause the Exit event to Stop working.
                event.ignore()
        else:
            # This will close the window as there is no Unsaved Changes.
            event.accept()

    # Creating the UI for the File cache System.
    def init_ui(self):
        
        # ---------------------------------------------------------------------
        # Sets the Locations of the loaded tool on screen.
        # Setting Max Height and width.
        # Setting window titile
        # ---------------------------------------------------------------------
        # self.setGeometry(Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter)
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowTitle("File Cacher")

        # ---------------------------------------------------------------------
        # LAYOUTS
        # ---------------------------------------------------------------------
        # <<< ------ LAYOUT HIRACHY ------ >>>
        # vBox-MAIN
        #   hBox-Buttons [ Button Layout at the top ]
        #   hBox-Main [ Holds the List and read out ]
        #       vBox-List [ List view ]
        #       vBox-Data [ Display Data ]
        #           hBox-NotSaved [ Nodes Not Saved ]
        #           hBox-Deleted [ Nodes Deleted ]

        # ---------------------------------------------------------------------        
        vBoxMain = QVBoxLayout()
        hBoxButtons = QHBoxLayout()
        hBoxMain = QHBoxLayout()
        vBoxList = QVBoxLayout()
        vBoxData = QVBoxLayout()
        vBoxNotSaved = QVBoxLayout()
        vBoxDeleted = QVBoxLayout()
        
        # Add To [ vBoxMain ]
        vBoxMain.addLayout(hBoxButtons)
        vBoxMain.addLayout(hBoxMain)

        # Add to [ hBoxMain ]
        hBoxMain.addLayout(vBoxList)
        hBoxMain.addLayout(vBoxData)

        # Add to [ vBoxData ]
        vBoxData.addLayout(vBoxNotSaved)
        vBoxData.addLayout(vBoxDeleted)

        # ---------------------------------------------------------------------
        # WIDGETS -  Creation
        # ---------------------------------------------------------------------
        # Widgets - [ hBoxButtons ] - Buttons
        self.btn_updateListOrder = QPushButton("Update List Order")
        self.btn_updateListOrder.setObjectName("btn_updateListOrder")
        self.btn_updateListOrder.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_updateListOrder.setToolTip("This Updates the JSON file with the current list order below.")

        self.btn_findChanges = QPushButton("Find Changes")
        self.btn_findChanges.setObjectName("btn_findChanges")
        self.btn_findChanges.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_findChanges.setToolTip("This is going to find all File Cache nodes and save them to a JSON File as well as update the existings JSON file if it exists.")
        
        self.btn_cacheAll = QPushButton("Cache All")
        self.btn_cacheAll.setObjectName("btn_cacheAll")
        self.btn_cacheAll.setCursor(QCursor(Qt.PointingHandCursor))

        self.btn_cacheSelected = QPushButton("Cache Selected")
        self.btn_cacheSelected.setObjectName("btn_cacheSelected")
        self.btn_cacheSelected.setCursor(QCursor(Qt.PointingHandCursor))

        self.chk_bkgrdCache = QCheckBox("Background Cache")
        self.chk_hqeueuCache = QCheckBox("Send To HQeueu")

        # Widgets - [ hBoxMain ]_[ vBoxList ] - List
        self.lblJsonHeader = QLabel()
        self.lblJsonHeader.setObjectName("lblJson")
        self.lblJsonHeader.setText("JSON File")
        self.lblJsonHeader.setAlignment(Qt.AlignCenter)

        self.jsonFileCacheListWidget = QListWidget()
        
        self.jsonFileCacheListWidget.setObjectName("lstJson")
        
        # self.jsonFileCacheListWidget.setAlternatingRowColors(True)
        
        self.jsonFileCacheListWidget.setDragDropMode(QAbstractItemView.InternalMove)
        
        self.jsonFileCacheListWidget.setAcceptDrops(True)
        
        self.jsonFileCacheListWidget.setDefaultDropAction(Qt.MoveAction)
        
        self.jsonFileCacheListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        

        # [ hBoxMain ]_[ vBoxData ]_[ vBoxNotSaved ] - List
        self.lblNodesNotSavedHeader = QLabel()
        self.lblNodesNotSavedHeader.setObjectName("lblNodesNotSaved")
        self.lblNodesNotSavedHeader.setText("Nodes Not Saved")
        self.lblNodesNotSavedHeader.setAlignment(Qt.AlignCenter)

        self.notSavedNodesListWidget = QListWidget()
        self.notSavedNodesListWidget.setObjectName("lstNodesNotSaved")
        # self.notSavedNodesListWidget.setAlternatingRowColors(True)

        # [ hBoxMain ]_[ vBoxData ]_[ vBoxDeleted ] - List
        self.lblDeletedNodesHeader = QLabel()
        self.lblDeletedNodesHeader.setObjectName("lblNodesDeleted")
        self.lblDeletedNodesHeader.setText("Nodes Deleted")
        self.lblDeletedNodesHeader.setAlignment(Qt.AlignCenter)

        self.deletedNodesListWidget = QListWidget()
        self.deletedNodesListWidget.setObjectName("lstDeletedNodes")
        # self.deletedNodesListWidget.setAlternatingRowColors(True)


        # ---------------------------------------------------------------------
        # WIDGETS - Add Widgets to their Correnct Box Sections.
        # ---------------------------------------------------------------------
        # [ hBoxButtons ]
        hBoxButtons.addWidget(self.btn_updateListOrder)
        hBoxButtons.addWidget(self.btn_findChanges)        
        hBoxButtons.addWidget(self.btn_cacheAll)
        hBoxButtons.addWidget(self.btn_cacheSelected)
        # hBoxButtons.addWidget(self.chk_bkgrdCache)
        # hBoxButtons.addWidget(self.chk_hqeueuCache)

        # [ hBoxMain ]_[ vBoxList ]
        vBoxList.addWidget(self.lblJsonHeader)
        vBoxList.addWidget(self.jsonFileCacheListWidget)
        

        # [ hBoxMain ]_[ vBoxData ]_[ vBoxNotSaved ]
        vBoxNotSaved.addWidget(self.lblNodesNotSavedHeader)
        vBoxNotSaved.addWidget(self.notSavedNodesListWidget)

        # [ hBoxMain ]_[ vBoxData ]_[ vBoxDeleted ]
        vBoxDeleted.addWidget(self.lblDeletedNodesHeader)
        vBoxDeleted.addWidget(self.deletedNodesListWidget)
        
        # ---------------------------------------------------------------------
        # STYLESHEETS
        # ---------------------------------------------------------------------
        stylesheet_path = "{}/CSS/main.css".format(os.path.dirname(__file__))

        # Check if style sheet exists
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as file:
                self.setStyleSheet(file.read())
        
        # ---------------------------------------------------------------------
        # SET LAYOUT
        # ---------------------------------------------------------------------
        self.setLayout(vBoxMain)

        # ---------------------------------------------------------------------
        # EVENTS
        # ---------------------------------------------------------------------
        # Button Clicks
        self.btn_updateListOrder.clicked.connect(self.updateListOrder_Clicked)
        self.btn_findChanges.clicked.connect(self.findChanges_Clicked)        
        self.btn_cacheAll.clicked.connect(self.cachAll_Clicked)
        self.btn_cacheSelected.clicked.connect(self.cacheSelected_Clicked)

        # Drop Events
        # self.jsonFileCacheListWidget.connect(self.itemDropped)
        
    # ---------------------------------------------------------------------
    # BUTTON CLICK EVENTS
    # ---------------------------------------------------------------------    
    # Find All Cache Nodes, Read back from Disk, Call QT List set Function
    def findChanges_Clicked(self):
        # This is returning a Dictionary of names and node Paths as well as reading in the JSON file and both are Dictionaries.
        dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))

        # Checking the Dictionary and JSON Files.
        self.jsonDictCheck(dictFoundNodes=dictFoundNodes)

    def updateListOrder_Clicked(self):
        
        try:
            # Calling the Update Method.
            dictListValues = self.listWidgetItemsToDict(self.jsonFileCacheListWidget)
            dictNotSavedValues = self.listWidgetItemsToDict(self.notSavedNodesListWidget)
            dictDeletedValues = self.listWidgetItemsToDict(self.deletedNodesListWidget)

            # Updating the JSON File based on the Deleted and Not Saved Nodes.
            self.jsonDictUpdate(dictJson=dictListValues, dictNotSavedNodes=dictNotSavedValues, dictDeletedNodes=dictDeletedValues)

            self.notSavedNodesListWidget.clear()
            self.deletedNodesListWidget.clear()

            hou.ui.displayMessage("The update has completed successfully.")

        except Exception as e:
            hou.ui.displayMessage("An error has ocured, Check details below", 
            title="ERROR", severity=hou.severityType.Error, details="{}".format(e.message), details_label="Error Details")
        
    def cachAll_Clicked(self):
        dictListValues = self.listWidgetItemsToDict(self.jsonFileCacheListWidget)
        self.cacheItems(dictListValues)

    def cacheSelected_Clicked(self):
        listText = []
        for item in self.jsonFileCacheListWidget.selectedItems():
            
            listText.append(item.text())

        if listText == []:
            hou.ui.displayMessage("Select an object in the list.")
        else:
            dictListValues = self.listWidgetItemsToDict(listTextList=listText)
            self.cacheItems(dictListValues)

    # ---------------------------------------------------------------------
    # METHODS
    # ---------------------------------------------------------------------
    # Loading and updating the List order
    def jsonDictUpdate(self, dictFoundNodes = {}, dictJson = collections.OrderedDict(), dictNotSavedNodes = {}, dictDeletedNodes = [], firstLoad = False):
        # Creating empty list for saving to the JSON File to keep order, Nodes Not Saved and Nodes Deleted.
        lst = []

        if dictJson == collections.OrderedDict():
            # Creating an empty ordered dict for the returned JSON List Dict items.
            # Fetching the JSON Data and Add it to a new List.
            dictListJson = self.readListOrder()

            # Adding to the created ordered DICT From the list of Dict Items based on their Key[path] and value[name].
            for item in dictListJson:
                    dictJson[item["path"]] = item["name"]

        # Getting all Found File Cachce nodes if non are provided.
        if dictFoundNodes == {}:
            dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))

        # Checking to see if there are any file cache nodes that are new and have not been added to the JSON File.        
        if dictNotSavedNodes != {}:
            fileCacheNotStored = dictNotSavedNodes
        else:
            fileCacheNotStored = { k : dictFoundNodes[k] for k in set(dictFoundNodes) - set(dictJson) }
        
        # Checking to see if there are any file cache nodes in the JSON File which have been deleted from the Netwrok view.
        if dictDeletedNodes != {}:
            deletedNodes = dictDeletedNodes
        else:
            deletedNodes = { k : dictJson[k] for k in set(dictJson) - set(dictFoundNodes) }

         # Checking to see if the JSON Dict Data is not Empty.
        if dictJson != {}:
            # Checking to see if we are going to just load the JSON File or not.
            if firstLoad != True:
                # Check to see if the fileCachNotFound Dict have any values, If it dose, then update the Dictionary with those values.
                if fileCacheNotStored != {}:
                    dictJson.update(fileCacheNotStored)                    

                # Check if the deletedNodes Dict has any values, if it dose, then go into the Json Dict and remove that item.
                if deletedNodes != {}:
                    for key, value in deletedNodes.iteritems():
                        dictJson.pop(key)

            # Converting the Updated Orderd JSON Dict to a list to store its order.
            lst = CF.dictToList(dictJson)

         # If there is no JSON File, Then its the first time and we need to use all currently found nodes.
        elif dictFoundNodes != {}:
            # Converting the Found Nodes Dict to a list to store its order.
            lst = CF.dictToList(dictFoundNodes)

            # This message is for first time Loads and creation of the JSON File.
            hou.ui.displayMessage("This is your First Load.", 
                    title="First JSON Save", severity=hou.severityType.Message, help="All currently found File Cache Nodes have been saved to a JSON file on disk. The file loacation is: $HIP/JSON/ListOrder.")

        # Saving the Dictionary to the QTList and to the JSON File.
        self.saveListOrder(lst)
        self.setJsonListText(lst)

    # Dose a check for any New File Cache nodes and any deleted File Cache Nodes and updates the Not Stored and Deleted Nodes List's.
    def jsonDictCheck(self, dictFoundNodes = {}):
        # Creating empty list for saving to the JSON File to keep order, Nodes Not Saved and Nodes Deleted.
        lstNtSvd = []
        lstDlt = []

        # Creating an empty ordered dict for the returned JSON List Dict items.
        # Fetching the JSON Data and Add it to a new List.
        dictJson = collections.OrderedDict()
        dictListJson = self.readListOrder()

        # Adding to the created ordered DICT From the list of Dict Items based on their Key[path] and value[name].
        for item in dictListJson:
                dictJson[item["path"]] = item["name"]

        # Getting all Found File Cachce nodes if non are provided.
        if dictFoundNodes == {}:
            dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))        
        

        # Checking to see if there are any file cache nodes that are new and have not been added to the JSON File.
        # Checking to see if there are any file cache nodes in the JSON File which have been deleted from the Netwrok view.
        fileCacheNotStored = { k : dictFoundNodes[k] for k in set(dictFoundNodes) - set(dictJson) }
        deletedNodes = { k : dictJson[k] for k in set(dictJson) - set(dictFoundNodes) }

       
        lstNtSvd = CF.dictToList(fileCacheNotStored)
        lstDlt = CF.dictToList(deletedNodes)

            # Enabling the button here if the JSON file exists and has Data.
        self.btn_updateListOrder.setEnabled(True)

        # Updating the Not Saved and Deleted QTList's with the correct Data.
        self.setNotSavedListText(lstNtSvd)
        self.setDeletedListText(lstDlt)

    # This Method populates the QList using a List of Dictionaris.
    def setJsonListText(self, dictList):
        self.jsonFileCacheListWidget.clear()
        

        # Looping through the incoming dictionary and adding it the the listQT List
        for item in dictList:
            item = "Node: {}    |   Path: {}".format(item["name"], item["path"])
            QListWidgetItem(item, self.jsonFileCacheListWidget)    
            
    # This Method populates the NotSaved Nodes ListWidget using a List of Dictionaris.
    def setNotSavedListText(self, dictList):
        self.notSavedNodesListWidget.clear()

        # Looping through the incoming dictionary and adding it the the listQT List
        for item in dictList:
            item = "Node: {}    |   Path: {}".format(item["name"], item["path"])
            QListWidgetItem(item, self.notSavedNodesListWidget)

    # This Method populates the Deleted Nodes ListWidget using a List of Dictionaris.
    def setDeletedListText(self, dictList):
        self.deletedNodesListWidget.clear()

        # Looping through the incoming dictionary and adding it the the listQT List
        for item in dictList:
            item = "Node: {}    |   Path: {}".format(item["name"], item["path"])
            QListWidgetItem(item, self.deletedNodesListWidget)

    # This Method Saves a Dictionary to a JSON File.
    def saveListOrder(self, dictList):
        path = "{}JSON/".format(CF.getHipPath(True))
        CF.saveToJsonFile(dictList, "ListOrder", path)

    #  This Method reads a JSON file and returns a Dictionary.
    def readListOrder(self):
        path = "{}JSON/".format(CF.getHipPath(True))
        return CF.readFromJsonFile("ListOrder", path)  

    # Convert QTList Text List to Dict.
    def listWidgetItemsToDict(self, QListObject, listTextList=[] ):
        # Creating an empty list item.
        # Creating an empty Dictionary.
        listSplitLst = []
        dictListOrd = collections.OrderedDict()
        
        # Check to see we are already reciving a list of items or not.
        if listTextList == []:
            # Getting each QTListItems Text Value and doing a split to then store in a list.
            # The split returns this per list index: [node]. This is for each line in the QListWidget.
            for index in range(QListObject.count()):

                itemText = QListObject.item(index).text()

                listSplitLst.append(itemText.split("    |   "))
        else:
            # This only runs if the Method recives a list of ListWidget Items.
            for itemText in listTextList:
                listSplitLst.append(itemText.split("    |   "))
         
        # Looping through the list to get each item[Row], then doing another loop to go through each items sub Item[node: and Path:]
        # value (There are two from the split function on one list item line) and then I am removing the first
        # 6 Values of each sub item (i.e: nade: and path: ) need to be removed as well as stripping out "\n" from the list.
        for i in range(len(listSplitLst)):
            for j in range(len(listSplitLst[i])):
                listSplitLst[i][j] = listSplitLst[i][j][6:].strip(" \n")

            dictListOrd[listSplitLst[i][1]] = listSplitLst[i][0]

        # Returning the Dictionary.
        return dictListOrd
                        
    @staticmethod
    def cacheItems(dictNodesToCache):
        # Getting the Path selector from the dict and then running the "Save To Disk"[execute] Button.
        # This runs foreach item in the Dictionary.
        for path in dictNodesToCache:
            hou.parm("{}/{}".format(path, "execute")).pressButton()

# ---------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------

# Run Function to Load the UI
def run():
    dialog = MainWindow()
    dialog.setParent(hou.qt.floatingPanelWindow(None), Qt.Window)
    dialog.show()
   