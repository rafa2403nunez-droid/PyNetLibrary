
import clr

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument
uidoc=DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

#Preparing input from dynamo to revit

tolerance = UnitUtils.ConvertToInternalUnits(IN[0],UnitTypeId.Meters) #type:ignore

ceilings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()

rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

options = Options()

options.DetailLevel= ViewDetailLevel.Fine

#Do some action in a Transaction
TransactionManager.Instance.EnsureInTransaction(doc)

result = []

for ceiling in ceilings:
	elementGeometry = ceiling.get_Geometry(options)
	for geoCeiling in elementGeometry:
		if geoCeiling.__class__== Solid and geoCeiling.Volume > 0:
			ceilingSolid = geoCeiling
			break
	for room in rooms:
		if room.LookupParameter("Name").AsString() not in ["STAIRS","SHAFT"]:
			elementGeometry = room.get_Geometry(options)
			for geoRoom in elementGeometry:
				if geoRoom.__class__==Solid and geoRoom.Volume > 0:
					roomSolid = geoRoom
					break
			translatedRoomSolid = SolidUtils.CreateTransformed(roomSolid, Transform.CreateTranslation(XYZ(0, 0, tolerance)))
			innerSolid = BooleanOperationsUtils.ExecuteBooleanOperation(ceilingSolid, translatedRoomSolid, BooleanOperationsType.Intersect)
			if innerSolid.Volume != 0:			
				result.append([room, room.Number, ceiling])
					
				room.LookupParameter("AR_ROO_min_required_ceiling_height").Set(ceiling.LookupParameter("Height Offset From Level").AsValueString())
			
		else:
			room.LookupParameter("AR_ROO_min_required_ceiling_height").Set("-")
		
TransactionManager.Instance.TransactionTaskDone()

OUT = result