<p align="center">
  <img src="https://github.com/rafa2403nunez-droid/PyNet/blob/main/Assets/PyNetLogo.png" width="150"/>
</p>

# 📚 PyNet Script Library

**Reference library of Python .NET scripts** for BIM automation via the **[PyNet Platform](https://github.com/rafa2403nunez-droid/PyNet)**. These scripts run inside Autodesk Navisworks and Revit through PyNet's embedded **Python.NET** engine.

> **AI Users:** This README is the primary context source for generating new scripts. Read the execution environment and boilerplate sections before writing any code.

---

## ⚙️ Execution Environment

Scripts run via **Python.NET** (CPython 3.10+ + `pythonnet` — not IronPython). This means standard Python 3 syntax is fully supported, along with the `clr` bridge to access .NET and Autodesk APIs.

| Property | Navisworks | Revit |
| :--- | :--- | :--- |
| **Active document** | `doc = __navisworks__` | `doc = DocumentManager.Instance.CurrentDBDocument` |
| **CLR bridge** | `import clr` | `import clr` |
| **Standard Python** | ✅ Full Python 3.10+ | ✅ Full Python 3.10+ |
| **pip packages** | ✅ Available | ✅ Available |

**Key rules:**
- Always call `clr.AddReference(...)` before importing any Autodesk or System namespace.
- Use `List[T]` from `System.Collections.Generic` when passing collections to .NET methods.
- All UI dialogs use `System.Windows.Forms.MessageBox`.
- Wrap Revit write operations in a `Transaction` or `TransactionManager`.

---

## 📋 Standard Boilerplate

### Navisworks

```python
import clr
import sys
import os

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import *

clr.AddReference("Autodesk.Navisworks.ComApi")
from Autodesk.Navisworks.Api.ComApi import *

from System.Collections.Generic import List

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

doc = __navisworks__  # type: ignore
```

For clash detection, add:
```python
clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api.Clash import *
```

### Revit

```python
import clr

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.Exceptions import OperationCanceledException

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

from System.Collections.Generic import List

clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument
```

---

## 🏗️ Code Structure Convention

All scripts follow a class-based pattern with a single entry-point call at the bottom:

```python
class FeatureManager:
    @staticmethod
    def Run(document):
        data = DataProcessor.Process(document)
        DialogManager.ShowResult(data)

class DataProcessor:
    @staticmethod
    def Process(document):
        # business logic
        return result

class DialogManager:
    @staticmethod
    def ShowResult(data):
        MessageBox.Show(str(data), "PyNet", MessageBoxButtons.OK, MessageBoxIcon.Information)

# Entry point
FeatureManager.Run(doc)
```

---

## 📂 Scripts

### 🔵 Navisworks — `02_Scripts/01_Navisworks/`

Scripts organized into three areas:

- **Model Management** — open, append, list and publish NWD files using the core Document API.
- **Search Sets** — create Search Sets from property conditions (`SearchCondition`, `VariantData`, `SearchLocations`).
- **Clash Detection** — export and import clash test results (CSV), working with `doc.Clash.TestsData.Tests`.

Example — creating a Search Set by property value:
```python
searchSet = Search()  # type: ignore
searchSet.Locations = SearchLocations.DescendantsAndSelf
searchSet.Selection.SelectAll()
condition = SearchCondition.HasPropertyByDisplayName("Revit Type", "Clash Test Code")
conditionValue = condition.EqualValue(VariantData.FromDisplayString(value))
searchSet.SearchConditions.AddGroup(List[SearchCondition]([conditionValue]))
```

---

### 🟠 Revit — `02_Scripts/02_Revit/`

Scripts organized by API area:

- **User Selection** — interactive picks (`PickObject`, `PickObjects`, rectangle region, custom `ISelectionFilter`).
- **Selection Filters** — full coverage of Quick Filters (category, class, bounding box, element type, design option…), Slow Filters (parameter filter, solid intersection) and Logical combinators (AND/OR). Also includes special cases like getting doors/windows of a room.
- **Edit & Create Objects** — walls, floors, family instances, transforms, move/rotate with `ElementTransformUtils`, title block repositioning.
- **Units** — conversion utilities using `UnitUtils.ConvertToInternalUnits`.
- **Grids, Levels & Phases** — create and position grids, levels, and relocate annotation bubbles.
- **Views** — activate views, insert dependent views.
- **TaskDialog** — chained multi-step dialogs.
- **Geometry** — solid intersection utilities.

Example — collecting all walls in the document:
```python
walls = FilteredElementCollector(doc)\
    .OfCategory(BuiltInCategory.OST_Walls)\
    .WhereElementIsNotElementType()\
    .ToElements()
```

---

## 🔗 Ecosystem

| Component | Repository | Purpose |
| :--- | :--- | :--- |
| **PyNet Platform** | [rafa2403nunez-droid/PyNet](https://github.com/rafa2403nunez-droid/PyNet) | Navisworks/Revit plugin — hosts the Python.NET engine |
| **PyNet Bridge (MCP)** | [rafa2403nunez-droid/PyNetBridge](https://github.com/rafa2403nunez-droid/PyNetBridge) | MCP server — connects AI models to PyNet via Named Pipes |
| **PyNet Library** | This repo | Script reference library and AI context |

To have AI generate and execute scripts live against Navisworks or Revit, install the MCP server:

```powershell
irm https://raw.githubusercontent.com/rafa2403nunez-droid/PyNetBridge/main/install.ps1 | iex
```

---

<p align="center">
  Developed by <b>RAEN Digital Tools</b>
  <br/><br/>
  <img src="https://github.com/rafa2403nunez-droid/PyNet/blob/main/Assets/RAENDigitalTools.png" alt="RAEN Digital Tools" width="200">
</p>
