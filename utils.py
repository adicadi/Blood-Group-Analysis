import pandas as pd
import pycountry_convert as pc
from functools import lru_cache

@lru_cache(maxsize=1)
def load_and_preprocess_data():
    # Load raw data
    file_path = "Data/processed_blood_type_data_with_continent.csv"
    df = pd.read_csv(file_path)

    # Ensure numeric columns
    blood_groups = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']
    for col in blood_groups:
        df[col] = df[col].astype(float)

    # Validate percentages sum to ~100%
    df['Total_Percent'] = df[blood_groups].sum(axis=1)
    df['Percent_Error'] = abs(df['Total_Percent'] - 100)
    if (df['Percent_Error'] > 5).any():
        print("Warning: Some countries have significant percentage discrepancies.")

    # Map continents for missing values (e.g., Bhutan, Pakistan)
    def country_to_continent(country_name):
        try:
            country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            return pc.convert_continent_code_to_continent_name(continent_code)
        except:
            return "Unknown"

    df['Continent'] = df['Country'].apply(country_to_continent)

    # Add blood type compatibility (convert list to string)
    blood_compatibility = {
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'O-': ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'],
        'A+': ['A+', 'AB+'],
        'A-': ['A+', 'A-', 'AB+', 'AB-'],
        'B+': ['B+', 'AB+'],
        'B-': ['B+', 'B-', 'AB+', 'AB-'],
        'AB+': ['AB+'],
        'AB-': ['AB+', 'AB-']
    }
    df['Can_Donate_To'] = df['Rarest_Blood_Type'].map(lambda x: ', '.join(blood_compatibility.get(x, [])))

    # Add estimated donor pool for each blood type
    for bg in blood_groups:
        df[f'Donor_Pool_{bg}'] = (df['Population'] * df[bg] / 100).round()

    return df