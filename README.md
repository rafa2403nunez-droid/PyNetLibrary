<p align="center">
  <img src="https://github.com/rafa2403nunez-droid/PyNetLibrary/blob/main/Assets/PyNetLibrary.png" width="300"/>
</p>

# 📚 PyNet Library — Navisworks API Context

**API context and reference scripts for Autodesk Navisworks**, designed for the **[PyNet Platform](https://github.com/rafa2403nunez-droid/PyNet)**. This repo provides Python-style **stubs** of the Navisworks .NET API and example scripts, so that AI models (and developers) have the context they need to generate and understand Navisworks automation code that runs through PyNet's embedded **Python.NET** engine.

> **AI Users:** This README and the stub files under `01_Scripts/01_Navisworks/00_Stubs/` are the primary context sources for generating Navisworks scripts. Read the execution environment and boilerplate sections before writing any code.

---

## ⚙️ Execution Environment

Scripts run via **Python.NET** (CPython 3.10+ + `pythonnet` — not IronPython). This means standard Python 3 syntax is fully supported, along with the `clr` bridge to access .NET and Autodesk APIs.

| Property | Value |
| :--- | :--- |
| **Active document** | `doc = Application.ActiveDocument` (from `Autodesk.Navisworks.Api`) |
| **CLR bridge** | `import clr` |
| **Standard Python** | ✅ Full Python 3.10+ |
| **pip packages** | ✅ Available |

**Key rules:**
- Always call `clr.AddReference(...)` before importing any Autodesk or System namespace.
- Use `List[T]` from `System.Collections.Generic` when passing collections to .NET methods.
- All UI dialogs use `System.Windows.Forms.MessageBox`.  

---

## 📋 Standard Boilerplate

```python
import clr
import sys
from pathlib import Path

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import *

clr.AddReference("Autodesk.Navisworks.ComApi")
from Autodesk.Navisworks.Api.ComApi import *

clr.AddReference("Autodesk.Navisworks.Interop.ComApi")
from Autodesk.Navisworks.Api.Interop.ComApi import *

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import *
from System.Drawing import *

from System.Collections.Generic import List

from Autodesk.Navisworks.Api import Application
doc = Application.ActiveDocument
```

For clash detection, add:
```python
clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api.Clash import *
```

---

## 🏗️ Code Structure Convention

All scripts follow a class-based pattern with a single entry-point call at the bottom:

```python
class FeatureManager:
    '''
    Main orchestrator class — coordinates the workflow
    by calling helper classes and presenting results to the user.
    Each public method represents a complete user action.
    '''
    @staticmethod
    def Run(document):
        data = DataProcessor.Process(document)
        DialogManager.ShowResult(data)

class DataProcessor:
    '''
    Business logic class — reads and transforms data from
    the Navisworks document. Returns plain Python objects
    that the rest of the script can consume.
    '''
    @staticmethod
    def Process(document):
        # business logic
        return result

class DialogManager:
    '''
    UI helper class — displays results or collects user input
    via System.Windows.Forms dialogs (MessageBox, OpenFileDialog, etc.).
    '''
    @staticmethod
    def ShowResult(data):
        MessageBox.Show(str(data), "PyNet", MessageBoxButtons.OK, MessageBoxIcon.Information)

# Entry point
FeatureManager.Run(doc)
```

---

## 📂 Repository Structure

### API Stubs — `01_Scripts/01_Navisworks/00_Stubs/`

Python-style **stub files** that mirror the Navisworks .NET API surface. These stubs give AI models and IDEs the type information and method signatures needed to generate correct Navisworks code. Covers: `ApplicationParts`, `Automation`, `Bim360`, `Clash`, `ComApi`, `Controls`, `Data`, `DocumentParts`, `Interop`, `Plugins`, `Schema`.

### Example Scripts — `01_Scripts/01_Navisworks/`

Working scripts organized into three areas:

- **Model Management** (`01_ModelManagement/`) — open, append, list and publish NWD files using the core Document API.
- **Search Sets** (`02_SearchSets/`) — create Search Sets from property conditions (`SearchCondition`, `VariantData`, `SearchLocations`).
- **Clash Detection** (`03_ClashDetection/`) — export, import and rename clash test results, working with `doc.Clash.TestsData.Tests`.
- **Data Analysis** (`dataAnalysis/`) — chart generation from clash data (bar charts, pie charts, stacked bars).

Example — `SearchSetsManager.CreateSet` from `02_SearchSets/GenerateSearchSets.py`:
```python
class SearchSetsManager():
    @staticmethod
    def CreateSet(value, selectionSets):
        '''
        Creates a new Search Set filtered by a property value.
        Searches "Clash Test Code" under both "Revit Type" and "Element"
        categories (OR logic via separate groups), then registers the
        resulting set in the document's SelectionSets collection.
        '''
        searchSet = Search()
        searchSet.Locations = SearchLocations.DescendantsAndSelf
        searchSet.Selection.SelectAll()

        # First condition group — match by "Revit Type" category
        condition = SearchCondition.HasPropertyByDisplayName("Revit Type", "Clash Test Code")
        conditionValue = condition.EqualValue(VariantData.FromDisplayString(value))
        searchSet.SearchConditions.AddGroup(List[SearchCondition]([conditionValue]))

        # Second condition group (OR) — match by "Element" category
        conditionOr = SearchCondition.HasPropertyByDisplayName("Element", "Clash Test Code")
        conditionValueOr = conditionOr.EqualValue(VariantData.FromDisplayString(value))
        searchSet.SearchConditions.AddGroup(List[SearchCondition]([conditionValueOr]))

        # Create the SelectionSet and add it to the document
        instance = SelectionSet(searchSet)
        instance.DisplayName = value
        selectionSets.AddCopy(instance)
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
  <img src="https://github.com/rafa2403nunez-droid/PyNetLibrary/blob/main/Assets/RAENDigitalTools.png" alt="RAEN Digital Tools" width="200">
</p>
