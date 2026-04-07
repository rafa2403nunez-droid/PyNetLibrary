
import plotly.graph_objects as go
import plotly.io as pio
import clr
import sys
from pathlib import Path

bundlePath = (Path.home()/ "AppData"/ "Roaming"/ "Autodesk"/ "ApplicationPlugins"/ "RAEN.Navisworks.PyNET.bundle"/ "Contents"/ "2024")
sys.path.append(str(bundlePath))
clr.AddReference("Raen.Navisworks.Pynet.2024")
from Raen.Navisworks.Pynet.Utils import CastUtils #type:ignore

clr.AddReference("Autodesk.Navisworks.Api")
clr.AddReference("Autodesk.Navisworks.Clash")
from Autodesk.Navisworks.Api import Application
from Autodesk.Navisworks.Api.Clash import DocumentClash, ClashResult

doc = Application.ActiveDocument
clashDoc = CastUtils.CastTo[DocumentClash](doc.Clash)

data = []
for test in clashDoc.TestsData.Tests:
    new_count = 0
    for child in test.Children:
        result = CastUtils.CastTo[ClashResult](child)
        if result is not None and str(result.Status) == "New":
            new_count += 1
    if new_count > 0:
        data.append({"name": test.DisplayName, "new": new_count})

if data:
    labels = [d["name"] for d in data]
    values = [d["new"] for d in data]
    total = sum(values)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0,
        textinfo='label+percent+value',
        pull=[0.05] * len(values)
    )])

    fig.update_layout(
        title=dict(
            text=f"Interferencias Nuevas por Test de Clash — Total: {total}",
            font=dict(size=16),
            x=0.5
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )

    pio.show(fig)
    ia_Result = {"status": "Gráfico mostrado", "total_new": total}
else:
    ia_Result = {"status": "No hay interferencias nuevas"}
