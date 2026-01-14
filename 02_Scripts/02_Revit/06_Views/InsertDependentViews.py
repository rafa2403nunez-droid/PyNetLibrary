#region References

# Load the Python Standard and DesignScript Libraries
import string
import sys
import clr

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

# Import Windows form
clr.AddReference("System.Windows.Forms")
# Import System Drawing
clr.AddReference("System.Drawing")

import System
from System.Windows.Forms import*
from System.Drawing import*

clr.AddReference('System')
from System.Collections.Generic import List

#endregion

class SheetManager:
    @staticmethod
    def InsertLegend(document, legend, sheet, viewportTypeId):
        views = sheet.GetAllPlacedViews()
        names = [document.GetElement(view).Name for view in views]
        if legend.Name not in names:
            viewPort = Viewport.Create(document, sheet.Id, legend.Id, XYZ(1.9586, 1.1088, 0))
            if viewportTypeId != None:
                viewPort.ChangeTypeId(viewportTypeId)
    @staticmethod
    def GetViewPortType(document):
        try:
            viewportsId = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Viewports).WhereElementIsNotElementType().ToElements()[0].GetValidTypes()
            return [viewportId for viewportId in viewportsId if Element.Name.__get__(doc.GetElement(viewportId)) == "ACM_BM_ANO_viewport_keyplans"][0]
        except:
            return None


code = IN[0] #type:ignore

views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

filterView = [view for view in views if code in view.Name][0]

filterSheets = [sheet for sheet in sheets if code in sheet.Title]

if filterView != None:
	dependentViews = [doc.GetElement(id) for id in filterView.GetDependentViewIds()]


TransactionManager.Instance.EnsureInTransaction(doc)

if len(filterSheets) == len(dependentViews):
	for sheet, view in zip(filterSheets, dependentViews):
		SheetManager.InsertLegend(doc, view, sheet, SheetManager.GetViewPortType(doc))
	
	OUT = "Process finished"
else:
	OUT = "Number of sheets and dependent views is not the same"

TransactionManager.Instance.TransactionTaskDone()