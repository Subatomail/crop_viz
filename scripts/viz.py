import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# === Setup paths ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load data ===
df_soil = pd.read_csv(os.path.join(DATA_DIR, "soil_samples.csv"))
df_crops = pd.read_csv(os.path.join(DATA_DIR, "crop_yields.csv"))

# === 1. Line Forecast Chart: Soil Sustainability Over Time with Projections ===
forecast_df = df_soil.copy()
projection_years = [2026, 2027, 2028]
for region in forecast_df['region'].unique():
    sub = forecast_df[forecast_df['region'] == region]
    slope = np.polyfit(sub['year'], sub['sustainability_score'], 1)[0]
    last_value = sub.iloc[-1]['sustainability_score']
    for i, year in enumerate(projection_years, 1):
        new_row = pd.DataFrame([{
            'region': region,
            'year': year,
            'sustainability_score': last_value + i * slope,
            **{n: np.nan for n in ['N','P','K','Ca','Mg','Fe','Zn','Cu','Mn','B','Mo']}
        }])
        forecast_df = pd.concat([forecast_df, new_row], ignore_index=True)

line_fig = px.line(
    forecast_df,
    x="year",
    y="sustainability_score",
    color="region",
    markers=True,
    title="Soil Sustainability Forecast"
)
line_info = "<i>This chart shows predicted soil sustainability scores based on linear trends for each region from 2015 to 2025, extended to 2028.</i>"

# === 2. Grouped Bar Chart: Crop Yield by Region and Type ===
avg_yields = df_crops.groupby(['region', 'crop_type'])['yield_kg_per_hectare'].mean().reset_index()
bar_fig = px.bar(
    avg_yields,
    x="crop_type",
    y="yield_kg_per_hectare",
    color="region",
    barmode="group",
    title="Average Crop Yields"
)
bar_info = "<i>This chart compares average yields across crop types and regions to identify productivity trends.</i>"

# === 3. Correlation Heatmap: Nutrients vs. Sustainability ===
nutrient_cols = ['N','P','K','Ca','Mg','Fe','Zn','Cu','Mn','B','Mo']
corr_df = df_soil[nutrient_cols + ['sustainability_score']].corr().round(2)
heatmap_fig = go.Figure(data=go.Heatmap(
    z=corr_df.values,
    x=corr_df.columns,
    y=corr_df.index,
    colorscale='RdBu',
    zmid=0,
    text=corr_df.values,
    texttemplate="%{text}",
    colorbar=dict(title="Correlation")
))
heatmap_fig.update_layout(title="<b>Correlation: Nutrients & Sustainability</b>")
heatmap_info = "<i>Darker colors indicate stronger correlation between soil nutrient levels and sustainability score.</i>"

# === 4. Geo Scatter (USA-Focused) ===
region_coords = {
    'North': (45.0, -100.0),
    'South': (30.0, -95.0),
    'East': (40.0, -75.0),
    'West': (40.0, -120.0),
    'Central': (39.0, -90.0)
}
geo_df = df_soil[df_soil['year'] == 2025].copy()
geo_df['lat'] = geo_df['region'].map(lambda r: region_coords[r][0])
geo_df['lon'] = geo_df['region'].map(lambda r: region_coords[r][1])

geo_fig = px.scatter_geo(
    geo_df,
    lat="lat",
    lon="lon",
    color="sustainability_score",
    size="sustainability_score",
    title="US Soil Sustainability Map (2025)",
    color_continuous_scale="Viridis",
    projection="albers usa",
    scope="usa"
)
geo_info = "<i>Bubble size and color represent the soil sustainability score of each region in 2025.</i>"

# === 5. Detailed Sankey Diagram ===
sankey_data = {
    "source": ["N", "P", "K", "Mg", "Ca",  # nutrients
               "Sustainability", "Sustainability", "Sustainability",  # to health classes
               "Low", "Medium", "High"],  # to crops
    "target": ["Sustainability"] * 5 +
              ["Low", "Medium", "High"] +
              ["Corn", "Wheat", "Soybean"],
    "value":  [8, 7, 6, 5, 4,  # nutrient ➝ sustainability
               5, 8, 12,       # sustainability ➝ levels
               3, 4, 6]        # levels ➝ crops
}
labels = list(set(sankey_data["source"] + sankey_data["target"]))
label_index = {label: i for i, label in enumerate(labels)}

sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(label=labels, pad=15, thickness=20),
    link=dict(
        source=[label_index[s] for s in sankey_data['source']],
        target=[label_index[t] for t in sankey_data['target']],
        value=sankey_data['value']
    )
)])
sankey_fig.update_layout(title_text="<b>Nutrient Flow to Crops via Soil Health</b>", font_size=12)
sankey_info = "<i>This flow shows how key nutrients influence sustainability, which is grouped into soil health classes (Low, Medium, High), then linked to crop outcomes.</i>"

# === Export to Combined HTML Dashboard ===
charts = [
    ("Soil Sustainability Forecast", line_info, pio.to_html(line_fig, include_plotlyjs='cdn', full_html=False)),
    ("Average Crop Yields", bar_info, pio.to_html(bar_fig, include_plotlyjs=False, full_html=False)),
    ("Nutrient Correlation", heatmap_info, pio.to_html(heatmap_fig, include_plotlyjs=False, full_html=False)),
    ("Map: Soil Scores (USA)", geo_info, pio.to_html(geo_fig, include_plotlyjs=False, full_html=False)),
    ("Nutrient Flow Diagram", sankey_info, pio.to_html(sankey_fig, include_plotlyjs=False, full_html=False)),
]

with open(os.path.join(OUTPUT_DIR, "golden_image.html"), "w", encoding="utf-8") as f:
    f.write("""
    <html>
    <head>
        <title>Soil & Crop Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .chart { margin-bottom: 70px; }
            h1 { text-align: center; }
            .info { color: #666; font-size: 0.9em; margin-top: -10px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1><b>Soil & Crop Sustainability Dashboard</b></h1>
    """)

    for title, info, chart_html in charts:
        f.write(f"""
        <div class="chart">
            <h2>{title}</h2>
            <div class="info">{info}</div>
            {chart_html}
        </div>
        """)

    f.write("""
        <footer style="text-align:center; color:#555; font-size:0.85em;">
            Generated with Plotly · Data is synthetic · &copy; Crop Sustainability Insights
        </footer>
    </body>
    </html>
    """)

print("Dashboard saved to /outputs/golden_image.html")
