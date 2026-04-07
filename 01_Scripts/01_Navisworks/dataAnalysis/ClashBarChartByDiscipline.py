
import plotly.graph_objects as go
import plotly.io as pio
import clr
import sys
import re
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

discipline_map = {
    "EM": "Estructura Metálica",
    "EH": "Hormigón in Situ",
    "EP": "H. Prefabricado",
    "IC": "Climatización",
    "II": "P. Incendios",
    "IF": "Fontanería",
    "IS": "Saneamiento",
    "IO": "Frío Industrial"
}

discipline_counts = {}

for test in clashDoc.TestsData.Tests:
    name = test.DisplayName
    match = re.search(r'_([A-Z]{2})_vs_', name)
    code = match.group(1) if match else "??"
    label = discipline_map.get(code, code)

    new_count = sum(1 for child in test.Children
                    if str(CastUtils.CastTo[ClashResult](child).Status) == "New"
                    if CastUtils.CastTo[ClashResult](child) is not None)

    discipline_counts[label] = discipline_counts.get(label, 0) + new_count

sorted_items = sorted(discipline_counts.items(), key=lambda x: x[1], reverse=True)
labels = [i[0] for i in sorted_items]
values = [i[1] for i in sorted_items]
total = sum(values)

colors = ["#d32f2f" if v > 0 else "#90a4ae" for v in values]

fig = go.Figure(data=[go.Bar(
    x=labels,
    y=values,
    marker_color=colors,
    text=values,
    textposition="outside"
)])

fig.update_layout(
    title=dict(
        text=f"Interferencias Nuevas por Disciplina — Total: {total}",
        font=dict(size=16),
        x=0.5
    ),
    xaxis_title="Disciplina",
    yaxis_title="Nº Interferencias Nuevas",
    yaxis=dict(rangemode="tozero"),
    plot_bgcolor="white",
    bargap=0.3
)

pio.show(fig)
ia_Result = {"status": "Gráfico mostrado", "total_new": total, "por_disciplina": discipline_counts}
