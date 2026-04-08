#region references

import clr
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import *

clr.AddReference("Autodesk.Navisworks.ComApi")
from Autodesk.Navisworks.Api.ComApi import *

clr.AddReference("Autodesk.Navisworks.Interop.ComApi")
from Autodesk.Navisworks.Api.Interop.ComApi import *

clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api.Clash import *

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import*
from System.Drawing import*

bundlePath = (Path.home()/ "AppData"/ "Roaming"/ "Autodesk"/ "ApplicationPlugins"/ "RAEN.Navisworks.PyNET.bundle"/ "Contents"/ "2024")
NavisworksinconPath = (Path.home()/ "AppData"/ "Roaming"/ "Autodesk"/ "ApplicationPlugins"/ "RAEN.Navisworks.PyNET.bundle"/ "Contents"/ "2024" / "Images" / "manage.ico")

sys.path.append(str(bundlePath))

clr.AddReference("Raen.Navisworks.Pynet.2024")

from Raen.Navisworks.Pynet.Utils import CastUtils  # type: ignore

from Autodesk.Navisworks.Api import Application 
doc = Application.ActiveDocument

#endregion


class ClashResultData:
    def __init__(self, testName, guid, status, comment):
        self.testName = testName
        self.guid = guid
        self.status = status
        self.comment = comment

    @property
    def TestName(self):
        return self.testName

    @property
    def Guid(self):
        return self.guid

    @property
    def Status(self):
        return self.status

    @property
    def Comment(self):
        return self.comment


class DialogManager:
    @staticmethod
    def ShowOpenFileDialog():
        openDialog = OpenFileDialog()
        openDialog.InitialDirectory = str(Path.home() / "Desktop")
        openDialog.Filter = "xml files (*.xml)|*.xml|All files (*.*)|*.*"

        if openDialog.ShowDialog() == DialogResult.OK:
            return openDialog.FileName
        return None

    @staticmethod
    def DataImportedDialog():
        MessageBox.Show(
            "Clash results updated, status changed to approved or reviewed",
            "Update Clash Results",
            MessageBoxButtons.OK,
            MessageBoxIcon.Information
        )


class DataManager:
    @staticmethod
    def GetClashesData():
        xmlPath = DialogManager.ShowOpenFileDialog()
        if not xmlPath:
            raise Exception("No XML file selected")

        tree = ET.parse(xmlPath)
        root = tree.getroot()

        dataResults = []

        for clashTest in root.iter("clashtest"):
            clashTestName = clashTest.get("name")
            for clashResult in clashTest.iter("clashresult"):
                status = (clashResult.get("status") or "").lower()
                if status not in ("approved", "reviewed"):
                    continue
                guid = clashResult.get("guid")
                comment_nodes = clashResult.findall("./comments/comment/body")
                comments = None
                if comment_nodes:
                    comments = CommentCollection()

                    for node in comment_nodes:
                        comments.Add(Comment(node.text, CommentStatus.New))
                dataResults.append(
                    ClashResultData(
                        clashTestName,
                        guid,
                        status,
                        comments
                    )
                )

        return dataResults

class ClashManager:
    @staticmethod
    def ImportClashResults(dataResults):

        documentClashTests = CastUtils.CastTo[DocumentClash](doc.Clash).TestsData
        tests = documentClashTests.Tests

        for test in tests:
            for data in dataResults:
                if data.TestName == test.DisplayName:
                    for children in test.Children:

                        if str(children.Guid) == data.Guid and str(children.Status).upper() != data.Status.upper():

                            # Add comments if present
                            if data.Comment != None:
                                documentClashTests.TestsEditResultComments(children, data.Comment)

                            # Apply new status
                            if data.Status.upper() == str(ClashResultStatus.Approved).upper():
                                documentClashTests.TestsEditResultStatus(children, ClashResultStatus.Approved)

                            elif data.Status.upper() == str(ClashResultStatus.Reviewed).upper():
                                documentClashTests.TestsEditResultStatus(children, ClashResultStatus.Reviewed)


        DialogManager.DataImportedDialog()



ClashManager.ImportClashResults(DataManager.GetClashesData())