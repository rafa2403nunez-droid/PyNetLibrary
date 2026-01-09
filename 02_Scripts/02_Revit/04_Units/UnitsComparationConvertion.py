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

#endregion

#region Convert Units

value = 32

# Convert to internal revit 2021 and next versions
convertToInternal = UnitUtils.ConvertToInternalUnits(value, UnitTypeId.Meters)
# Convert to internal revit before 2021
convertToInternal = UnitUtils.ConvertToInternalUnits(value, DisplayUnitType.DUT_Meters) #type: ignore

# Convert from internal 2021 and next versions
convertFromInternal = UnitUtils.ConvertFromInternalUnits(value, UnitTypeId.Meters) 
# Convert from internal revit before 2021
convertToInternal = UnitUtils.ConvertFromInternalUnits(value, DisplayUnitType.DUT_Meters) #type: ignore

OUT = convertFromInternal, convertToInternal

#endregion