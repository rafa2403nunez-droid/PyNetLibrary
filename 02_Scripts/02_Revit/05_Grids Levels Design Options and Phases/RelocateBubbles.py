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


grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()

floorPlans = [view for view in views if view.ViewType == ViewType.FloorPlan]

with Transaction(doc) as tx:
	tx.Start("Relocate Bubbles")
	try:
		for view in floorPlans:
			for grid in grids:
				if grid.Curve.Direction.IsAlmostEqualTo(XYZ.BasisY):
					grid.HideBubbleInView(DatumEnds.End1, view)
					grid.ShowBubbleInView(DatumEnds.End0, view)
				if grid.Curve.Direction.IsAlmostEqualTo(-XYZ.BasisY):
					grid.HideBubbleInView(DatumEnds.End0, view)
					grid.ShowBubbleInView(DatumEnds.End1, view)
				if grid.Curve.Direction.IsAlmostEqualTo(-XYZ.BasisX):
					grid.HideBubbleInView(DatumEnds.End0, view)
					grid.ShowBubbleInView(DatumEnds.End1, view)
				if grid.Curve.Direction.IsAlmostEqualTo(XYZ.BasisX):
					grid.HideBubbleInView(DatumEnds.End1, view)
					grid.ShowBubbleInView(DatumEnds.End0, view)
	except:
		pass
		
	tx.Commit()

print("Bubbles Relocated correctly")