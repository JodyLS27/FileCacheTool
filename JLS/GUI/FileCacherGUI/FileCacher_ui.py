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
        self.jsonDictCheck(firstLoad=True)

    # Creating the UI for the File cache System.
    def init_ui(self):
        
        # ---------------------------------------------------------------------
        # Sets the Locations of the loaded tool on screen.
        # Setting Max Height and width.
        # Setting window titile
        # ---------------------------------------------------------------------
        # self.setGeometry(Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter)
        self.setGeometry(200, 200, 720, 600)
        self.setWindowTitle("File Cacher")

        # ---------------------------------------------------------------------
        # LAYOUTS
        # ---------------------------------------------------------------------
        # <<< ------ LAYOUT HIRACHY ------ >>>
        # VBOX-MAIN
        #   HBOX-1 [ Button Layout at the top ]
        #   HBOX-2 [ Holds the List and read out ]
        #       VBOX-1 [ List view ]
        #       VBOX-2 [ Selected Listtime Cache Data ]
        # ---------------------------------------------------------------------        
        vBox = QVBoxLayout()
        hBox1 = QHBoxLayout()
        hBox2 = QHBoxLayout()
        
        vBox.addLayout(hBox1)
        vBox.addLayout(hBox2)        

        # ---------------------------------------------------------------------
        # WIDGETS
        # ---------------------------------------------------------------------
        # Widgets - Horizontal 1 - Buttons
        self.btn_findAllCacheNds = QPushButton("Find All File Cache Nodes")
        self.btn_findAllCacheNds.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_findAllCacheNds.setToolTip("This is going to find all File Cache nodes and save them to a JSON File as well as update the existings JSON file if it exists.")

        self.btn_updateListOrder = QPushButton("Update List Order")
        self.btn_updateListOrder.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_updateListOrder.setToolTip("This Updates the JSON file with the current list order below.")
        
        self.btn_cacheAll = QPushButton("Cache All")
        self.btn_cacheAll.setCursor(QCursor(Qt.PointingHandCursor))

        self.btn_cacheSelected = QPushButton("Cache Selected")
        self.btn_cacheSelected.setCursor(QCursor(Qt.PointingHandCursor))

        self.chk_bkgrdCache = QCheckBox("Background Cache")
        self.chk_hqeueuCache = QCheckBox("Send To HQeueu")

        # List Widget setup.
        self.fileCacheListWidget = QListWidget()
        self.fileCacheListWidget.setAlternatingRowColors(True)
        self.fileCacheListWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.fileCacheListWidget.setAcceptDrops(True)
        self.fileCacheListWidget.setDefaultDropAction(Qt.MoveAction)
        self.fileCacheListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Add Widgets to their Correnct Box Sections.
        hBox1.addWidget(self.btn_findAllCacheNds)
        hBox1.addWidget(self.btn_updateListOrder)
        hBox1.addWidget(self.btn_cacheAll)
        hBox1.addWidget(self.btn_cacheSelected)
        # hBox1.addWidget(self.chk_bkgrdCache)
        # hBox1.addWidget(self.chk_hqeueuCache)
        hBox2.addWidget(self.fileCacheListWidget)
        
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
        self.setLayout(vBox)

        # ---------------------------------------------------------------------
        # EVENTS
        # ---------------------------------------------------------------------
        # Button Clicks
        self.btn_findAllCacheNds.clicked.connect(self.findAllFilecacheNodes_Clicked)
        self.btn_updateListOrder.clicked.connect(self.updateListOrder_Clicked)
        self.btn_cacheAll.clicked.connect(self.cachAll_Clicked)
        self.btn_cacheSelected.clicked.connect(self.cacheSelected_Clicked)


        # Drop Events
        # self.fileCacheListWidget.connect(self.itemDropped)
        
    # ---------------------------------------------------------------------
    # BUTTON CLICK EVENTS
    # ---------------------------------------------------------------------

    # Find All Cache Nodes, Read back from Disk, Call QT List set Function
    def findAllFilecacheNodes_Clicked(self):        
        # This is returning a Dictionary of names and node Paths as well as reading in the JSON file and both are Dictionaries.
        dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))

        # Checking the Dictionary and JSON Files.
        self.jsonDictCheck(dictFoundNodes=dictFoundNodes)

    def updateListOrder_Clicked(self):
        
        try:
            # Calling the Update Method.
            dictListValues = self.listWidgetItemsToDict()
            lst = CF.dictToList(dictListValues)

            # Save the List Dict to a JSON File.
            # Update the QTList with the list items.
            self.saveListOrder(lst)
            self.setListText(lst)

            hou.ui.displayMessage("The update has completed successfully.")

        except Exception as e:
            hou.ui.displayMessage("An error has ocured, Check details below", 
            title="ERROR", severity=hou.severityType.Error, details="{}".format(e.message), details_label="Error Details")
        

    
    def cachAll_Clicked(self):
        dictListValues = self.listWidgetItemsToDict()
        self.cacheItems(dictListValues)

    def cacheSelected_Clicked(self):
        listText = []
        for item in self.fileCacheListWidget.selectedItems():
            listText.append(item.text())

        if listText == []:
            hou.ui.displayMessage("Select an object in the list.")
        else:
            dictListValues = self.listWidgetItemsToDict(listTextList=listText)
            self.cacheItems(dictListValues)

            

    # ---------------------------------------------------------------------
    # METHODS
    # ---------------------------------------------------------------------

    # Updates and dose a check for any New File Cache nodes and any deleted File Cache Nodes and updates the JSON File Acordingly.
    def jsonDictCheck(self, dictFoundNodes = {}, firstLoad = False):
        # Creating empty list for saving to the JSON File to keep order.
        # Creating an empty ordered dict for the returned JSON List Dict items.
        # Fetching the JSON Data and Add it to a new List.
        lst = []
        dictJson = collections.OrderedDict()
        dictListJson = self.readListOrder()

        # Getting all Found nodes if non are provided.
        if dictFoundNodes == {}:
            dictFoundNodes = CF.getNodeNameAndPathFromDict(CF.findAllNodeType("filecache"))
        
        # Adding to the created ordered DICT From the list of Dict Items based on their Key[path] and value[name].
        for item in dictListJson:
                dictJson[item["path"]] = item["name"]

        # Checking to see if there are any file cache nodes that are new and have not been added to the JSON File.
        # Checking to see if there are any file cache nodes in the JSON File which have been deleted from the Netwrok view.
        fileCacheNotStored = { k : dictFoundNodes[k] for k in set(dictFoundNodes) - set(dictJson) }
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

            # Enabling the button here if the JSON file exists and has Data.
            self.btn_updateListOrder.setEnabled(True)


        # If there is no JSON File, Then its the first time and we need to use all currently found nodes.
        elif dictFoundNodes != {}:
            # Converting the Found Nodes Dict to a list to store its order.
            lst = CF.dictToList(dictFoundNodes)
            hou.ui.displayMessage("This is your First Load.", 
                    title="First JSON Save", severity=hou.severityType.Message, help="All currently found FileCache Nodes have been saved to a JSON file on disk. The file loacation is: $HIP/JSON/ListOrder.")

        # Save the List Dict to a JSON File.
        # Update the QTList with the list items.
        self.saveListOrder(lst)
        self.setListText(lst)

    # This Method populates the QList using a List of Dictionaris.
    def setListText(self, dictList):
        self.fileCacheListWidget.clear()

        # Looping through the incoming dictionary and adding it the the listQT List
        for item in dictList:
            item = "Node: {}    |   Path: {} \n".format(item["name"], item["path"])
            QListWidgetItem(item, self.fileCacheListWidget)     

    # This Method Saves a Dictionary to a JSON File.
    def saveListOrder(self, dictList):        
        path = "{}JSON/".format(CF.getHipPath(True))
        CF.saveToJsonFile(dictList, "ListOrder", path)

    #  This Method reads a JSON file and returns a Dictionary.
    def readListOrder(self):        
        path = "{}JSON/".format(CF.getHipPath(True))
        return CF.readFromJsonFile("ListOrder", path)  

    def listWidgetItemsToDict(self, listTextList=[]):
        # Creating an empty list item.
        # Creating an empty Dictionary.
        listSplitLst = []
        dictListOrd = collections.OrderedDict()

        # Check to see we are already reciving a list of items or not.
        if listTextList == []:
            # Getting each QTListItems Text Value and doing a split to then store in a list.
            # The split returns this per list index: [node]. This is for each line in the QListWidget.
            for index in range(self.fileCacheListWidget.count()):
                itemText = self.fileCacheListWidget.item(index).text()
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