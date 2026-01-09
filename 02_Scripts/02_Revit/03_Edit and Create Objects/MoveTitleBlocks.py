#region References

# Load the Python Standard and DesignScript Libraries
import clr
import sys

sys.path.append("C:\\Program Files (x86)\\IronPython 2.7\\Lib")
import os

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *
import Autodesk

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

#Import Windows form
clr.AddReference("System.Windows.Forms")
# Import System Drawing
clr.AddReference("System.Drawing")

from System.Windows.Forms import*
from System.Drawing import*
from System.Collections.Generic import List
from datetime import date

uidoc = __revit__.ActiveUIDocument #type:ignore
doc = uidoc.Document

#endregion


def GetTitleblock(view, document):
	element = None
	for elementId in view.GetDependentElements(None):
		if doc.GetElement(elementId).__class__ == FamilyInstance and document.GetElement(elementId).Category.Name == "Title Blocks":
			element = document.GetElement(elementId)
			break

	return element
	
# Get Current Selection
selection = uidoc.Selection.GetElementIds()[0]
titleblock = None

if selection != None:
	if doc.GetElement(selection).__class__ == ViewSheet:
		view = doc.GetElement(selection)
		titleblock = GetTitleblock(view, doc)

collector = FilteredElementCollector(doc).OfClass(ViewSheet).WhereElementIsNotElementType().ToElements()

result = []

with Transaction(doc) as tx:

	tx.Start("Move Titleblocks")

	for sheet in collector:
		if sheet.Id == selection:
			pass
		else:
			titleblockCompare = GetTitleblock(sheet, doc)
			if titleblockCompare != None and not titleblock.Location.Point.IsAlmostEqualTo(titleblockCompare.Location.Point):
				x = titleblockCompare.Location.Point.X - titleblock.Location.Point.X
				y = titleblockCompare.Location.Point.Y - titleblock.Location.Point.Y
				z = titleblockCompare.Location.Point.Z - titleblock.Location.Point.Z
				ElementTransformUtils.MoveElement(doc, titleblockCompare.Id, XYZ(-x, -y, -z))
				result.append(titleblockCompare)

	tx.Commit()
	
TaskDialog.Show("Revit API", "TitleBlocks translated: " + str(len(result)))
