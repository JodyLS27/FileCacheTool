# FileCacheTool V0.3

#### First Step: 
In houdini, Create a new shelf tool.
Now add the following code to your new shelf tool.
```python
from JLS.GUI.FileCacherGUI import FileCacher_ui
reload(FileCacher_ui)

FileCacher_ui.run()
```

#### Second Step:
Now go into the following Directorys and past the JLS Folder.
***Windows:*** *C:\Users\"Your_User_name"\Documents\houdini"Your_Version_Here"\scripts\python\Past_JLS_Here*

#### Third Step:
Now the Tool Should run when Clicking the tool.

