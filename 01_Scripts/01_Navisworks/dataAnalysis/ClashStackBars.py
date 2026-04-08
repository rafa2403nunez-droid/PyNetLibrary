#region references
import pandas as pd

import clr
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import re

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
from Autodesk.Navisworks.Api.Clash import DocumentClash, ClashResult
document = Application.ActiveDocument

#endregion

class ClashDataResult():
    """
    Wrapper class used to extract, normalize and store information from
    a Navisworks Clash Test. Computes each clash status count (New, Active,
    Reviewed, Approved, Resolved) and exposes clean read-only properties
    for export or UI consumption.
    """
    def __init__(self, test):
        self.testName: str = test.DisplayName
        self.tolerance: float = test.Tolerance
        self.status: str = test.Status
        self.lastRun: str = test.LastRun
        self.new: int = 0
        self.active: int = 0
        self.reviewed: int = 0
        self.approved: int = 0
        self.resolved: int = 0

        for children in test.Children:
            if str(children.Status).upper() == str(ClashResultStatus.New).upper():
                self.new += 1
            if str(children.Status).upper() == str(ClashResultStatus.Active).upper():
                self.active += 1
            if str(children.Status).upper() == str(ClashResultStatus.Reviewed).upper():
                self.reviewed += 1
            if str(children.Status).upper() == str(ClashResultStatus.Approved).upper():
                self.approved += 1
            if str(children.Status).upper() == str(ClashResultStatus.Resolved).upper():
                self.resolved += 1

    @property
    def Name(self):
        """Returns the Clash Test display name."""
        return self.testName

    @property
    def Tolerance(self):
        """Returns the test clash tolerance."""
        return self.tolerance

    @property
    def Status(self):
        """Returns the overall status of the clash test."""
        return self.status

    @property
    def LastRun(self):
        """Returns the last execution date/time of the clash test."""
        return self.lastRun

    @property
    def NewCount(self):
        """Returns the number of NEW clash results."""
        return self.new

    @property
    def ActiveCount(self):
        """Returns the number of ACTIVE clash results."""
        return self.active

    @property
    def ReviewedCount(self):
        """Returns the number of REVIEWED clash results."""
        return self.reviewed

    @property
    def ApprovedCount(self):
        """Returns the number of APPROVED clash results."""
        return self.approved

    @property
    def ResolvedCount(self):
        """Returns the number of RESOLVED clash results."""
        return self.resolved


def AnalizeStackBars(data):
    df = pd.DataFrame([clash.__dict__ for clash in data])

    df["left"] = df["testName"].str.split("_vs_").str[0]
    df["left"] = df["left"].str.replace(r"^[ABC]_", "", regex=True)
    df["right"] = df["testName"].str.split("_vs_").str[1]

    def extract_subdiscipline(name: str) -> str:
        if pd.isna(name):
            return ""
        name = re.sub(r"^[^_]+_", "", name)
        name = re.sub(r"_[A-Z]+$", "", name)
        return name.strip()

    df["left"] = df["left"].apply(extract_subdiscipline)
    df["right"] = df["right"].apply(extract_subdiscipline)

    types = ["new", "active", "reviewed"]
    stacked_df = pd.DataFrame()

    for t in types:
        temp_df = pd.concat([
            df[["left", t]].rename(columns={"left": "subdiscipline"}),
            df[["right", t]].rename(columns={"right": "subdiscipline"})
        ]).groupby("subdiscipline").sum()
        stacked_df[t] = temp_df[t]

    stacked_df["total"] = stacked_df.sum(axis=1)
    stacked_df = stacked_df.sort_values("total", ascending=False)
    stacked_df = stacked_df.drop(columns="total")

    stacked_df = stacked_df[stacked_df.sum(axis=1) > 0]

    colors = {"new": "#FF1200", "active": "#FFC500", "reviewed": "#00C4FF"}

    plt.figure(figsize=(10, 5), num="Clashes to Resolve")
    bottom = pd.Series([0]*len(stacked_df), index=stacked_df.index)

    for t in types:
        plt.bar(
            stacked_df.index,
            stacked_df[t],
            bottom=bottom,
            color=colors[t],
            label=t.capitalize()
        )
        bottom += stacked_df[t]

    totals = stacked_df.sum(axis=1)
    for i, total in enumerate(totals):
        plt.text(
            i,
            total + 0.5,
            str(total),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    plt.ylabel("Clashes to resolve")
    plt.xlabel("Subdiscipline")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, totals.max() * 1.1) 
    plt.legend()
    plt.tight_layout()
    plt.show()



clashDocument = CastUtils.CastTo[DocumentClash](document.Clash)

tests = clashDocument.TestsData.Tests

data = [ClashDataResult(test) for test in tests]

AnalizeStackBars(data)