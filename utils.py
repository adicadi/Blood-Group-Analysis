import pandas as pd
import pycountry_convert as pc
from functools import lru_cache
import logging

# Constants
BLOOD_GROUPS = ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"]
CONTINENTS = ["Europe", "Africa", "Asia", "South America", "North America", "Oceania", "Unknown"]
# Configure logger
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
@lru_cache(maxsize=1)
def load_and_preprocess_data():
    file_path = "Data/processed_blood_type_data_with_continent.csv"  # Adjust path as needed
    df = pd.read_csv(file_path)

    for col in BLOOD_GROUPS:
        df[col] = df[col].astype(float)

    df['Total_Percent'] = df[BLOOD_GROUPS].sum(axis=1)
    df['Percent_Error'] = abs(df['Total_Percent'] - 100)
    if (df['Percent_Error'] > 5).any():
        logger.warning("Some countries have significant percentage discrepancies.")

    def country_to_continent(country_name):
        try:
            country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            return pc.convert_continent_code_to_continent_name(continent_code)
        except:
            return "Unknown"

    df['Continent'] = df['Country'].apply(country_to_continent)

    blood_compatibility = {
        'O+': ['O+', 'A+', 'B+', 'AB+'], 'O-': BLOOD_GROUPS,
        'A+': ['A+', 'AB+'], 'A-': ['A+', 'A-', 'AB+', 'AB-'],
        'B+': ['B+', 'AB+'], 'B-': ['B+', 'B-', 'AB+', 'AB-'],
        'AB+': ['AB+'], 'AB-': ['AB+', 'AB-']
    }
    df['Can_Donate_To'] = df['Rarest_Blood_Type'].map(lambda x: ', '.join(blood_compatibility.get(x, [])))

    for bg in BLOOD_GROUPS:
        df[f'Donor_Pool_{bg}'] = (df['Population'] * df[bg] / 100).round()

    return df