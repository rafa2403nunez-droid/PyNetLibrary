"""
Export Clash Dashboard Data & Launch Viewer
Extracts clash test results, exports clashes.json,
launches a Dash server and opens the BIM Coordination Dashboard.
"""

import clr
import sys
import json
import re
import threading
import webbrowser
from pathlib import Path

clr.AddReference("Autodesk.Navisworks.Api")
from Autodesk.Navisworks.Api import *

clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api.Clash import *

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import *
from System.Drawing import *

bundlePath = (Path.home() / "AppData" / "Roaming" / "Autodesk" / "ApplicationPlugins" / "RAEN.Navisworks.PyNET.bundle" / "Contents" / "2024")
NavisworksIconPath = (Path.home() / "AppData" / "Roaming" / "Autodesk" / "ApplicationPlugins" / "RAEN.Navisworks.PyNET.bundle" / "Contents" / "2024" / "Images" / "manage.ico")
sys.path.append(str(bundlePath))
clr.AddReference("Raen.Core.Pynet.Resources")
from Raen.Core.Pynet.Resources import CastUtils #type:ignore

from Autodesk.Navisworks.Api import Application
doc = Application.ActiveDocument

user_home = Path.home()
repo_base = user_home / "source" / "repos" / "GithubRNM" / "PyNetLibrary" / "03_Viewer"
VIEWER_DIR = repo_base / "dist"
DASHBOARD_DIR = repo_base / "dashboard"
PORT = 8095

class ClashExtractor:
    """Extracts clash data from the active document."""

    @staticmethod
    def GetElementId(item):
        if item is None:
            return None
        try:
            for cat in item.PropertyCategories:
                if "Element" in cat.DisplayName:
                    for prop in cat.Properties:
                        if prop.DisplayName in ("Value", "Id") or "id" in prop.DisplayName.lower():
                            return str(prop.Value.ToDisplayString())
            for cat in item.PropertyCategories:
                for prop in cat.Properties:
                    if prop.DisplayName.lower() in ("id", "guid", "ifcguid"):
                        return str(prop.Value.ToDisplayString())
        except:
            pass
        return str(item.InstanceGuid)

    @staticmethod
    def GetProperty(item, catName, propName):
        if item is None:
            return None
        try:
            for cat in item.PropertyCategories:
                if cat.DisplayName == catName:
                    for prop in cat.Properties:
                        if prop.DisplayName == propName:
                            return str(prop.Value.ToDisplayString())
        except:
            pass
        return None

    @staticmethod
    def ExtractDiscipline(testName):
        m = re.search(r'Instalaciones_([^_]+)', testName)
        return m.group(1) if m else "Estructura"

    @staticmethod
    def Run(document):
        models = []
        for i in range(document.Models.Count):
            model = document.Models[i]
            fname = model.FileName.replace("\\", "/")
            models.append({
                "name": model.RootItem.DisplayName.replace(".ifc", ""),
                "fileName": fname.split("/")[-1],
                "fullPath": fname
            })

        clashDocument = CastUtils.CastTo[DocumentClash](document.Clash)
        tests = clashDocument.TestsData.Tests

        for i in range(tests.Count):
            clashDocument.TestsData.TestsRunTest(tests[i])

        allClashes = []
        testsSummary = []

        for i in range(tests.Count):
            test = tests[i]
            count = test.Children.Count if test.Children else 0
            testsSummary.append({"name": test.DisplayName, "clashes": count, "status": str(test.Status)})
            if count == 0:
                continue
            testName = test.DisplayName
            discipline = ClashExtractor.ExtractDiscipline(testName)
            for j in range(test.Children.Count):
                result = CastUtils.CastTo[ClashResult](test.Children[j])
                if result is None:
                    continue
                itemA = result.CompositeItem1
                itemB = result.CompositeItem2
                point = result.Center
                allClashes.append({
                    "Test": testName, "Discipline": discipline,
                    "Clash": result.DisplayName, "Status": str(result.Status),
                    "Distance (m)": round(result.Distance, 4) if result.Distance else 0,
                    "X": round(point.X, 3) if point else None,
                    "Y": round(point.Y, 3) if point else None,
                    "Z": round(point.Z, 3) if point else None,
                    "Element A": itemA.DisplayName if itemA else "",
                    "ID A": ClashExtractor.GetElementId(itemA),
                    "Source A": ClashExtractor.GetProperty(itemA, "Item", "Source File") or "",
                    "Type A": ClashExtractor.GetProperty(itemA, "Item", "Type") or "",
                    "Element B": itemB.DisplayName if itemB else "",
                    "ID B": ClashExtractor.GetElementId(itemB),
                    "Source B": ClashExtractor.GetProperty(itemB, "Item", "Source File") or "",
                    "Type B": ClashExtractor.GetProperty(itemB, "Item", "Type") or "",
                    "GUID": str(result.Guid)
                })

        return models, testsSummary, allClashes

class DataExporter:
    """Exports clash data to JSON."""

    @staticmethod
    def Export(models, testsSummary, allClashes):
        ifc_dir = Path(models[0]["fullPath"]).parent if models else Path.home() / "Desktop"
        export_data = {
            "models": models, "tests": testsSummary, "clashes": allClashes,
            "summary": {
                "totalClashes": len(allClashes),
                "activeTests": sum(1 for t in testsSummary if t["clashes"] > 0),
                "totalModels": len(models)
            }
        }
        output_path = ifc_dir / "clashes.json"
        output_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return output_path, ifc_dir

class DashboardServer:
    """Launches a Dash/Flask server to serve the viewer and dashboard."""

    @staticmethod
    def Run(ifc_dir):
        from dash import Dash, html

        app = Dash("pynet_dashboard", url_base_pathname="/_app/")
        fk = sys.modules.get("flask")
        app.layout = html.Div("OK")

        @app.server.route("/")
        def idx():
            return fk.send_file(str(DASHBOARD_DIR / "index.html"), mimetype="text/html")

        @app.server.route("/dashboard.css")
        def css():
            return fk.send_file(str(DASHBOARD_DIR / "dashboard.css"), mimetype="text/css")

        @app.server.route("/dashboard.js")
        def js():
            return fk.send_file(str(DASHBOARD_DIR / "dashboard.js"), mimetype="application/javascript")

        @app.server.route("/viewer/")
        def vi():
            return fk.send_file(str(VIEWER_DIR / "index.html"), mimetype="text/html")

        @app.server.route("/viewer/<path:fp>")
        def vf(fp):
            f = VIEWER_DIR / fp
            if f.exists() and f.is_file():
                mt = {"css": "text/css", "js": "application/javascript", "mjs": "application/javascript",
                      "wasm": "application/wasm", "json": "application/json", "html": "text/html"}
                return fk.send_file(str(f), mimetype=mt.get(f.suffix.lstrip("."), "application/octet-stream"))
            return "Not found", 404

        @app.server.route("/models/<fn>")
        def mi(fn):
            f = ifc_dir / fn
            if f.exists():
                return fk.send_file(str(f), mimetype="application/octet-stream")
            return "Not found", 404

        @app.server.route("/data/<fn>")
        def di(fn):
            f = ifc_dir / fn
            if f.exists():
                return fk.send_file(str(f), mimetype="application/json")
            return "Not found", 404

        app.run(port=PORT, debug=False, use_reloader=False)

class DashboardForm(Form):
    """Main form for the Clash Dashboard workflow."""

    def __init__(self):
        Form.__init__(self)
        self.ExportResult = None
        self.IFCDir = None
        self.ServerRunning = False
        self.ConfigureForm()     

    def ConfigureForm(self):
        self.Text = "BIM Coordination Dashboard"
        if Path(str(NavisworksIconPath)).exists():
            self.Icon = Icon(str(NavisworksIconPath))
        self.Width = 990
        self.Height = 700
        self.MinimumSize = Size(480, 340)
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.MaximizeBox = False
        self.StartPosition = FormStartPosition.CenterScreen
        self.TopMost = True       
        self.GenerateUI()
        self.GenerateFormGroups()
        self.GenerateFormSelectionList()
        self.ExportData()

    def GenerateUI(self):
        self.LaunchBtn = Button()
        self.LaunchBtn.Text = "Launch"
        self.LaunchBtn.Width = 120
        self.LaunchBtn.Location = Point(710, 590)
        self.LaunchBtn.Enabled = False
        self.LaunchBtn.Click += self.OnLaunch
        self.Controls.Add(self.LaunchBtn)

        closeBtn = Button()
        closeBtn.Text = "Cancel"
        closeBtn.Width = 120
        closeBtn.Location = Point(840, 590)
        closeBtn.Click += self.OnClose
        self.Controls.Add(closeBtn)

    def GenerateFormGroups(self):
        groupBoxViews = GroupBox()
        groupBoxViews.Text = "Clash Detection Results generated"
        groupBoxViews.Size = Size(940, 550)
        groupBoxViews.Location = Point(20, 20)
        groupBoxViews.Anchor = AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Top
        groupBoxViews.Parent = self

    def GenerateFormSelectionList(self):
        self.dataGrid = DataGridView()
        self.dataGrid.Name = "ModelsList"
        self.dataGrid.BackgroundColor = Color.White
        self.dataGrid.Location = Point(40, 60)
        self.dataGrid.Size = Size(900, 480)
        self.dataGrid.Anchor = AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Top
        
        self.dataGrid.ColumnCount = 3
        self.dataGrid.Columns[0].Name = "ClashTest Name"
        self.dataGrid.Columns[1].Name = "Clashes Count"
        self.dataGrid.Columns[2].Name = "Clashtest Status"
        
        for i in range(3):
            self.dataGrid.Columns[i].AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill

        self.dataGrid.AllowUserToAddRows = False
        self.dataGrid.AllowUserToDeleteRows = False
        self.dataGrid.RowHeadersVisible = False
        self.dataGrid.ReadOnly = True
        self.dataGrid.AllowUserToResizeRows = False
        self.dataGrid.SelectionMode = DataGridViewSelectionMode.FullRowSelect
        self.dataGrid.ColumnHeadersHeight = 40
        self.dataGrid.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing
        
        self.Controls.Add(self.dataGrid)
        self.dataGrid.BringToFront()

    def ExportData(self):
        print("Running clash tests")
        self.Refresh()

        try:
            models, testsSummary, allClashes = ClashExtractor.Run(doc)
            print("Exporting data and updating UI")
            
            self.dataGrid.Rows.Clear()
            for test in testsSummary:
                self.dataGrid.Rows.Add(test["name"], test["clashes"], test["status"])

            output_path, ifc_dir = DataExporter.Export(models, testsSummary, allClashes)
            self.IFCDir = ifc_dir

            total = len(allClashes)
            active = sum(1 for t in testsSummary if t["clashes"] > 0)
            print(f"Exported: {total} clashes from {active} tests.")

            self.LaunchBtn.Enabled = True
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def CheckPort(port):
        """Returns (owner_pid, is_own_process) for a port, or (None, False) if free."""
        import psutil
        my_pid = psutil.Process().pid
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return conn.pid, conn.pid == my_pid
        return None, False

    @staticmethod
    def KillPort(port):
        """Kill process on port ONLY if it's external (never kill Navisworks)."""
        import psutil
        my_pid = psutil.Process().pid
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                if conn.pid == my_pid:
                    return False
                try:
                    proc = psutil.Process(conn.pid)
                    proc.terminate()
                    proc.wait(timeout=3)
                    return True
                except:
                    pass
        return False

    def OnLaunch(self, sender, args):
        import time

        owner_pid, is_self = DashboardForm.CheckPort(PORT)

        # Server already running inside Navisworks — just open browser
        if owner_pid is not None and is_self:
            webbrowser.open(f"http://localhost:{PORT}")
            self.ServerRunning = True
            return

        self.LaunchBtn.Enabled = False
        self.Refresh()

        # Port occupied by external process — kill it safely
        if owner_pid is not None:
            print(f"Port {PORT} busy (external PID {owner_pid}) — stopping...")
            DashboardForm.KillPort(PORT)
            time.sleep(1)

        print("Starting dashboard server...")
        self.Refresh()

        dash_thread = threading.Thread(
            target=DashboardServer.Run,
            args=(self.IFCDir,),
            daemon=False
        )
        dash_thread.start()
        self.ServerRunning = True

        time.sleep(2)
        webbrowser.open(f"http://localhost:{PORT}")

        self.LaunchBtn.Enabled = True

    def OnClose(self, sender, args):
        self.Close()

DashboardForm().ShowDialog()