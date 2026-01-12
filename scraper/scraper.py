import wbgapi as wb
import pandas as pd
import json

def update_data():
    # 1. Define Indicators and Country scope
    indicators = {
        'FS.AST.CGOV.GD.ZS': 'Debt_GDP_Proxy',
        'FI.RES.TOTL.CD': 'Reserves',
        'TM.VAL.MRCH.CD.WT': 'Imports'
    }
    
    # Using 'all' for countries, or you can provide a list like ['USA', 'CHN', 'BRA']
    countries = 'all'

    # 1. Fetch Data
    # Using mrnev=5 to look back up to 5 years for the most recent data point
    df = wb.data.DataFrame(indicators.keys(), mrnev=1, columns='series')
    df.columns = [indicators[c] for c in df.columns]

    names = wb.economy.Series()
    df['Country_Name'] = names
    # 2. Math & Logic
    # Fill missing Proxy Debt with 0 or a median if you prefer, 
    # but here we'll keep it as N/A for transparency
    df['Import_Cover'] = df['Reserves'] / (df['Imports'] / 12)
    
    # Risk Score calculation (Handling NaNs so the math doesn't break)
    # We use .fill_na(0) only for the math, not the final display
    temp_debt = df['Debt_GDP_Proxy'].fillna(df['Debt_GDP_Proxy'].median())
    temp_cover = df['Import_Cover'].fillna(6) # Assume average cover if missing

    # Calculate Risk Score    
    df['Risk_Score'] = (temp_debt / 15) + (12 - temp_cover)
    print(df)
    # 4. Clean up for JSON
    # Reset index to move Country Codes into a column
    df = df.reset_index()
    df.rename(columns={'economy': 'country_code'}, inplace=True)
    print(df)
    # Filter out aggregates (like "World" or "High Income") to keep only countries
    # wbgapi metadata helps identify if an economy is an aggregate
    economies = wb.economy.list()
    iso_list = [e['id'] for e in economies if e['aggregate'] == False]
    df = df[df['country_code'].isin(iso_list)]
    # Round numbers for a cleaner UI
    df = df.round(2)
    
    # Handle NaN values (GitHub Pages/JSON doesn't like 'NaN')
    df = df.fillna("N/A")

    # 5. Save to JSON
    result = df.to_dict(orient='records')
    with open('JaysAnalystPortfolio/scraper/data.json', 'w') as f:
        json.dump(result, f, indent=4)
    
    print(f"Successfully updated data for {len(df)} economies.")

if __name__ == "__main__":
    update_data()