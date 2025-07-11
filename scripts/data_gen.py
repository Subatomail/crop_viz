import pandas as pd
import numpy as np
import os

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Nutrients list
nutrients = ['N', 'P', 'K', 'Ca', 'Mg', 'Fe', 'Zn', 'Cu', 'Mn', 'B', 'Mo']

# Region metadata
regions = ['North', 'South', 'East', 'West', 'Central']
region_climate = {
    'North': 'Cold',
    'South': 'Hot',
    'East': 'Temperate',
    'West': 'Dry',
    'Central': 'Temperate'
}

# 1. Nutrient Interaction Data
interactions = []
np.random.seed(42)
for source in nutrients:
    for target in nutrients:
        if source != target:
            effect = np.random.choice(['antagonism', 'stimulation', 'none'], p=[0.3, 0.3, 0.4])
            if effect != 'none':
                weight = round(np.random.uniform(0.1, 1.0), 2)
                interactions.append([source, target, effect, weight])
df_interactions = pd.DataFrame(interactions, columns=['source_nutrient', 'target_nutrient', 'effect_type', 'weight'])
df_interactions.to_csv(os.path.join(DATA_DIR, "nutrient_interactions.csv"), index=False)

# 2. Soil Samples Over Time
years = np.arange(2015, 2026)
soil_data = []

for year in years:
    for region in regions:
        nutrients_conc = np.random.uniform(10, 100, size=len(nutrients))
        sustainability_score = round(np.clip(np.random.normal(loc=70, scale=10), 0, 100), 2)
        if sustainability_score < 60:
            quality = "Low"
        elif sustainability_score < 80:
            quality = "Medium"
        else:
            quality = "High"
        row = [region, region_climate[region], year] + nutrients_conc.tolist() + [sustainability_score, quality]
        soil_data.append(row)

soil_columns = ['region', 'climate_zone', 'year'] + nutrients + ['sustainability_score', 'soil_quality']
df_soil = pd.DataFrame(soil_data, columns=soil_columns)
df_soil.to_csv(os.path.join(DATA_DIR, "soil_samples.csv"), index=False)

# 3. Crop Yield per Region
crops = ['Wheat', 'Corn', 'Soybean', 'Rice', 'Barley']
crop_data = []

for year in years:
    for region in regions:
        soil_score = df_soil[(df_soil['region'] == region) & (df_soil['year'] == year)]['sustainability_score'].values[0]
        for crop in crops:
            yield_kg = round(np.random.uniform(2000, 8000), 2)
            if yield_kg < 3500:
                health = "Poor"
            elif yield_kg < 6000:
                health = "Moderate"
            else:
                health = "Excellent"
            crop_data.append([
                region, region_climate[region], year, crop,
                yield_kg, soil_score, health
            ])

crop_columns = ['region', 'climate_zone', 'year', 'crop_type', 'yield_kg_per_hectare',
                'soil_sustainability_score', 'crop_health']
df_crops = pd.DataFrame(crop_data, columns=crop_columns)
df_crops.to_csv(os.path.join(DATA_DIR, "crop_yields.csv"), index=False)

print("Data saved to /data")
print(df_soil.head())
print(df_crops.head())
print(df_interactions.head())
