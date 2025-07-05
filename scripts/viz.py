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

nutrient_cols = ['N','P','K','Ca','Mg','Fe','Zn','Cu','Mn','B','Mo']

# === 1. Line Forecast Chart ===
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
            **{n: np.nan for n in nutrient_cols},
            'climate_zone': sub.iloc[-1]['climate_zone'],
            'soil_quality': None
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

# === 2. Grouped Bar Chart ===
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

# === 3. Correlation Heatmap ===
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

# === 4. Geo Scatter (USA-focused) ===
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

# === 5. Detailed Sankey ===
sankey_data = {
    "source": ["N", "P", "K", "Mg", "Ca",
               "Sustainability", "Sustainability", "Sustainability",
               "Low", "Medium", "High"],
    "target": ["Sustainability"] * 5 +
              ["Low", "Medium", "High"] +
              ["Corn", "Wheat", "Soybean"],
    "value":  [8, 7, 6, 5, 4,
               5, 8, 12,
               3, 4, 6]
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
sankey_info = "<i>This flow shows how nutrients influence soil sustainability, grouped into health levels, and connected to crop outcomes.</i>"

# === 6. Violin Plot ===
violin_fig = px.violin(
    df_soil,
    x="climate_zone",
    y="sustainability_score",
    box=True,
    points="all",
    color="climate_zone",
    title="Distribution of Soil Sustainability by Climate Zone"
)
violin_info = "<i>This violin plot shows the spread of sustainability scores across different climate zones.</i>"

# === 7. Stacked Nutrient Bar by Soil Quality ===
nutrient_avg = df_soil.groupby("soil_quality")[nutrient_cols].mean().reset_index()

nutrient_avg['soil_quality'] = pd.Categorical(
    nutrient_avg['soil_quality'], categories=['Low', 'Medium', 'High'], ordered=True
)
nutrient_avg = nutrient_avg.sort_values('soil_quality')

nutrient_colors = {
    'N': 'royalblue',
    'P': 'orangered',
    'K': 'mediumseagreen',
    'Ca': 'mediumslateblue',
    'Mg': 'darkorange',
    'Fe': 'deepskyblue',
    'Zn': 'hotpink',
    'Cu': 'yellowgreen',
    'Mn': 'violet',
    'B': 'gold',
    'Mo': 'slateblue'
}

nutrient_stacked_fig = go.Figure()
for nutrient in nutrient_cols:
    nutrient_stacked_fig.add_trace(go.Bar(
        y=nutrient_avg["soil_quality"],
        x=nutrient_avg[nutrient],
        name=nutrient,
        orientation='h',
        marker_color=nutrient_colors.get(nutrient)
    ))

nutrient_stacked_fig.update_layout(
    barmode='stack',
    title="<b>Average Nutrient Concentrations by Soil Quality Class</b>",
    yaxis_title="Soil Quality",
    xaxis_title="Nutrient Concentration (ppm)",
    height=500
)

nutrient_stacked_info = "<i>This horizontal stacked bar chart compares average nutrient concentrations for different soil quality classes. The wider the segment, the higher the concentration.</i>"


# === 8. Pie Chart: Crop Health ===
crop_health_counts = df_crops["crop_health"].value_counts().reset_index()
crop_health_counts.columns = ["crop_health", "count"]
pie_fig = px.pie(
    crop_health_counts,
    names="crop_health",
    values="count",
    title="Crop Health Distribution"
)
pie_info = "<i>This pie chart displays the proportion of crops categorized by health outcome based on yield.</i>"

# === 9. Animated Line: Crop Yield by Climate Zone ===
avg_yield_zone = df_crops.groupby(['year', 'climate_zone'])['yield_kg_per_hectare'].mean().reset_index()
animated_fig = px.line(
    avg_yield_zone,
    x="year",
    y="yield_kg_per_hectare",
    color="climate_zone",
    markers=True,
    title="Crop Yield Trends by Climate Zone"
)
animated_info = "<i>This line chart tracks average crop yield per climate zone from 2015 to 2025.</i>"

# === List of all charts ===
charts = [
    ("Soil Sustainability Forecast", line_info, pio.to_html(line_fig, include_plotlyjs='cdn', full_html=False)),
    ("Average Crop Yields", bar_info, pio.to_html(bar_fig, include_plotlyjs=False, full_html=False)),
    ("Nutrient Correlation", heatmap_info, pio.to_html(heatmap_fig, include_plotlyjs=False, full_html=False)),
    ("Map: Soil Scores (USA)", geo_info, pio.to_html(geo_fig, include_plotlyjs=False, full_html=False)),
    ("Nutrient Flow Diagram", sankey_info, pio.to_html(sankey_fig, include_plotlyjs=False, full_html=False)),
    ("Soil Sustainability by Climate", violin_info, pio.to_html(violin_fig, include_plotlyjs=False, full_html=False)),
    ("Nutrient Stacks by Soil Quality", nutrient_stacked_info, pio.to_html(nutrient_stacked_fig, include_plotlyjs=False, full_html=False)),
    ("Crop Health Proportions", pie_info, pio.to_html(pie_fig, include_plotlyjs=False, full_html=False)),
    ("Yield Trends by Climate Zone", animated_info, pio.to_html(animated_fig, include_plotlyjs=False, full_html=False))
]

# === Export Dashboard with custom layout ===
with open(os.path.join(OUTPUT_DIR, "dashboard.html"), "w", encoding="utf-8") as f:
    f.write("""
    <html>
    <head>
        <title>Soil & Crop Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .chart {
                margin-bottom: 60px;
                width: 100%;
            }
            .row {
                display: flex;
                flex-wrap: wrap;
                gap: 30px;
                margin-bottom: 60px;
            }
            .column {
                flex: 1;
                min-width: 45%;
                max-width: 49%;
            }
            @media (max-width: 768px) {
                .column {
                    min-width: 100%;
                    max-width: 100%;
                }
            }
            h1 {
                text-align: center;
            }
            .info {
                color: #666;
                font-size: 0.9em;
                margin-top: -10px;
                margin-bottom: 20px;
            }
            .chart {
    margin-bottom: 60px;
    width: 100%;
    min-height: 500px; /* Ensures room for each graph */
}

.column {
    flex: 1;
    min-width: 45%;
    max-width: 49%;
    display: flex;
    flex-direction: column;
}
        </style>
    </head>
    <body>
        <h1><b>Soil & Crop Sustainability Dashboard</b></h1>
    """)

    layout_sequence = [
        [0],           # Line forecast
        [1, 5],        # Bar + Violin
        [2],           # Correlation Heatmap
        [3],           # Geo Map
        [6, 8],        # Nutrient Stacked + Animated Line
        [4],           # Sankey
        [7],           # Pie chart
    ]

    for layout in layout_sequence:
        if len(layout) == 1:
            idx = layout[0]
            title, info, html = charts[idx]
            f.write(f"""
                <div class="chart">
                    <h2>{title}</h2>
                    <div class="info">{info}</div>
                    {html}
                </div>
            """)
        else:
            f.write('<div class="row">')
            for idx in layout:
                title, info, html = charts[idx]
                f.write(f"""
                    <div class="column chart">
                        <h2>{title}</h2>
                        <div class="info">{info}</div>
                        {html}
                    </div>
                """)
            f.write('</div>')

    f.write("""
        <footer style="text-align:center; color:#555; font-size:0.85em; margin-top: 40px;">
            Generated with Plotly · Data is synthetic · &copy; Crop Sustainability Insights
        </footer>
    </body>
    </html>
    """)

print("Dashboard saved to /outputs/dashboard.html")
