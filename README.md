<p align="center">
  <img src="https://github.com/rafa2403nunez-droid/PyNetLibrary/blob/main/Assets/PyNetLibrary.png" width="300"/>
</p>

# 📚 PyNet Library — Autodesk Apps API Context

**API context and reference scripts for Autodesk Navisworks**, designed for the **[PyNet Platform](https://github.com/rafa2403nunez-droid/PyNet)**. This repo provides Python-style **stubs** of the Navisworks .NET API and example scripts, so that AI models (and developers) have the context they need to generate and understand Navisworks automation code that runs through PyNet's embedded **Python.NET** engine.

> **AI Users:** This README and the stub files under `01_Scripts/01_Navisworks/00_Stubs/` are the primary context sources for generating Navisworks scripts. Read the execution environment and boilerplate sections before writing any code.

---

## ⚡ Quick Start

If you are an AI model or developer, you can quickly verify the environment with a minimal script:

```python
import clr
from Autodesk.Navisworks.Api import Application

doc = Application.ActiveDocument
print(doc.Title)
```

If this executes successfully inside PyNet, the environment is correctly configured.

This confirms:
- Python.NET is working
- Navisworks API is accessible
- Active document context is available

---

## ⚙️ Execution Environment

Scripts run via **Python.NET** (CPython 3.10+ + `pythonnet` — not IronPython). This means standard Python 3 syntax is fully supported, along with the `clr` bridge to access .NET and Autodesk APIs.

| Property | Value |
| :--- | :--- |
| **CLR bridge** | `import clr` |
| **Standard Python** | ✅ Full Python 3.10+ |
| **pip packages** | ✅ Available |

**Key rules:**
- Always call `clr.AddReference(...)` before importing any Autodesk or System namespace.
- Use `List[T]` from `System.Collections.Generic` when passing collections to .NET methods.
- All UI dialogs use `System.Windows.Forms.MessageBox`.  


## 🧠 AI Usage Guidelines

When generating scripts for PyNet / Navisworks, follow these rules:

### Structure
- Always use a class-based architecture
- Separate logic, UI, and orchestration
- Provide a single entry point (e.g. FeatureManager.Run(doc))

### Imports
- Always include required clr.AddReference(...) calls before importing .NET namespaces
- Only include imports that are required for the script to function

### API Usage
- Use Application.ActiveDocument as the entry point to the model
- Prefer strongly typed Navisworks API classes over dynamic access

### UI interaction
- Use System.Windows.Forms for dialogs
- Avoid blocking UI threads unnecessarily

### Output
- Scripts should be self-contained and executable
- Avoid external dependencies unless explicitly allowed

### Safety
- Do not use restricted Python modules
- Do not attempt file system or system-level operations

### Deterministic Behavior
- Generate predictable and repeatable scripts
- Avoid ambiguous or dynamic runtime decisions
- Prefer explicit API calls over reflection or introspection

### Consistency
- Maintain consistent naming conventions across classes
- Follow the same structure across all generated scripts

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

## 🧪 Minimal Working Example

This example verifies that the Navisworks API and PyNet execution environment are correctly configured:

```python
import clr

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import Application

from System.Windows.Forms import MessageBox

doc = Application.ActiveDocument

class FeatureManager:
    @staticmethod
    def Run(document):
        MessageBox.Show("Document loaded: " + document.Title)

FeatureManager.Run(doc)
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

## 🔍 Stub Usage

The files located in 01_Scripts/01_Navisworks/00_Stubs/ provide a Python-style representation of the Navisworks .NET API.

### Purpose
- Provide type hints and method signatures
- Help AI models understand available API surfaces
- Improve code generation accuracy
- Assist developers in navigating the API

### How to Use
- Use stubs as a reference when writing scripts manually
- Use them as context for AI-generated code
- Explore them in an IDE for navigation and API understanding
- They are not required at runtime and should not be executed directly

### Notes
- Stubs mirror the structure of the Autodesk Navisworks .NET assemblies
- They are purely informational and not executed at runtime

---

## 📂 Repository Structure

This repository contains two main types of resources:

- API stubs for Navisworks .NET
- Example scripts demonstrating real-world usage patterns

### Example Scripts — 01_Scripts/01_Navisworks/

Working scripts organized into three areas:

- **Model Management** (`01_ModelManagement/`) — open, append, list and publish NWD files using the core Document API.
- **Search Sets** (`02_SearchSets/`) — create Search Sets from property conditions (`SearchCondition`, `VariantData`, `SearchLocations`).
- **Clash Detection** (`03_ClashDetection/`) — export, import and rename clash test results, working with `doc.Clash.TestsData.Tests`.
- **Data Analysis** (`dataAnalysis/`) — chart generation from clash data (bar charts, pie charts, stacked bars).

Example — `SearchSetsManager.CreateSet` from 02_SearchSets/GenerateSearchSets.py:

```python
import clr

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import *

clr.AddReference("Autodesk.Navisworks.ComApi")
from Autodesk.Navisworks.Api.ComApi import *

clr.AddReference("Autodesk.Navisworks.Interop.ComApi")
from Autodesk.Navisworks.Api.Interop.ComApi import *

clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api.Clash import *

from System.Collections.Generic import List

from Autodesk.Navisworks.Api import Application 
doc = Application.ActiveDocument

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

## 🗒️ Common Patterns

Below are frequently used patterns when working with the Navisworks API:

```python
### Access Active Document

doc = Application.ActiveDocument

### Iterate Model Items

for item in doc.Models[0].RootItem.DescendantsAndSelf:
    print(item.DisplayName)

### Access Properties

props = item.PropertyCategories

### Working with Selection Sets

selection_sets = doc.SelectionSets

### Run a Search

search = Search()
search.Selection.SelectAll()
```

---

## 🔗 How This Library Fits Into the Ecosystem

This library is part of a modular system designed to enable AI-driven BIM automation across Autodesk tools.

This repository is designed to work alongside:

- PyNet Platform → Executes scripts inside Navisworks via Python.NET  
- PyNet Bridge (MCP) → Connects AI models to PyNet using IPC  

Together, these components enable:

Natural Language → AI → Python Script → PyNet → Navisworks → BIM Action

| Component | Repository | Purpose |
| :--- | :--- | :--- |
| **PyNet Platform** | [rafa2403nunez-droid/PyNet](https://github.com/rafa2403nunez-droid/PyNet) | Navisworks/Revit plugin — hosts the Python.NET engine |
| **PyNet Bridge (MCP)** | [rafa2403nunez-droid/PyNetBridge](https://github.com/rafa2403nunez-droid/PyNetBridge) | MCP server - connects AI models to PyNET with including secure scripts validation|
| **PyNet Library** | This repo | Script reference library and AI context |

To have AI generate and execute scripts live against Navisworks or Revit, install the MCP server:

```powershell
irm https://raw.githubusercontent.com/rafa2403nunez-droid/PyNetBridge/main/install.ps1 | iex
```

---

## ⚠️ Notes and Limitations

### Runtime Limitations
- Scripts run inside Navisworks context only
- File system and OS-level operations are restricted
- Certain Python standard libraries are not available due to security constraints

### Compatibility
- Requires Autodesk Navisworks with Python.NET support
- Compatible with Python 3.10+
- Behavior may vary depending on Navisworks version
- Some API features differ between Manage and Simulate editions
- API access depends on Autodesk Navisworks version compatibility

---

<p align="center">
  Developed by <b>RAEN Digital Tools</b>
  <br/><br/>
  <img src="https://github.com/rafa2403nunez-droid/PyNetLibrary/blob/main/Assets/RAENDigitalTools.png" alt="RAEN Digital Tools" width="200">
</p>
