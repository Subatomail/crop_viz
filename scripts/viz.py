import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
df_soil = pd.read_csv(os.path.join(DATA_DIR, "soil_samples.csv"))
df_crops = pd.read_csv(os.path.join(DATA_DIR, "crop_yields.csv"))

# Line chart: Soil Sustainability Score over Time by Region
line_fig = px.line(
    df_soil,
    x="year",
    y="sustainability_score",
    color="region",
    title="Soil Sustainability Over Time by Region",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Dark24
)
line_fig.update_layout(
    title=dict(text="<b>Soil Sustainability Over Time by Region</b>", font_size=20),
    legend=dict(title_text="Region", bordercolor="black", borderwidth=1),
    margin=dict(l=40, r=20, t=60, b=40)
)

# Bar chart: Average Yield per Crop Type
avg_crop = df_crops.groupby("crop_type")["yield_kg_per_hectare"].mean().reset_index()
bar_fig = px.bar(
    avg_crop,
    x="crop_type",
    y="yield_kg_per_hectare",
    color="crop_type",
    title="Average Crop Yield by Type",
    color_discrete_sequence=px.colors.sequential.Teal
)
bar_fig.update_layout(
    title=dict(text="<b>Average Crop Yield by Type</b>", font_size=20),
    xaxis_title="Crop Type",
    yaxis_title="Yield (kg/ha)",
    showlegend=False,
    margin=dict(l=40, r=20, t=60, b=40)
)

# Heatmap: Average nutrient concentrations by region
nutrients = ['N', 'P', 'K', 'Ca', 'Mg', 'Fe', 'Zn', 'Cu', 'Mn', 'B', 'Mo']
avg_nutrients = df_soil.groupby("region")[nutrients].mean()
heatmap_fig = go.Figure(data=go.Heatmap(
    z=avg_nutrients.values,
    x=avg_nutrients.columns,
    y=avg_nutrients.index,
    colorscale='Viridis',
    colorbar=dict(title="Concentration (ppm)")
))
heatmap_fig.update_layout(
    title="<b>Average Soil Nutrient Concentration by Region</b>",
    xaxis_title="Nutrient",
    yaxis_title="Region",
    margin=dict(l=60, r=20, t=60, b=40)
)

# Export individual plot HTML segments
line_html = pio.to_html(line_fig, include_plotlyjs='cdn', full_html=False)
bar_html = pio.to_html(bar_fig, include_plotlyjs=False, full_html=False)
heatmap_html = pio.to_html(heatmap_fig, include_plotlyjs=False, full_html=False)

# Combine into single dashboard
with open(os.path.join(OUTPUT_DIR, "golden_image.html"), "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
    <head>
        <title>Soil & Crop Sustainability Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ text-align: center; }}
            .chart {{ margin-bottom: 60px; }}
        </style>
    </head>
    <body>
        <h1><b>Soil & Crop Sustainability Dashboard</b></h1>
        <div class="chart">{line_html}</div>
        <div class="chart">{bar_html}</div>
        <div class="chart">{heatmap_html}</div>
        <footer style="text-align:center; color:#555;">
            Generated with Plotly · Data is synthetic · &copy; Crop Sustainability Insights
        </footer>
    </body>
    </html>
    """)

print("Combined dashboard saved to /outputs/golden_image.html")
