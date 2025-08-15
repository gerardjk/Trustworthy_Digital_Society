#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrape_bond_data.py - Comprehensive scraper for World Government Bonds data

This script scrapes:
1. Current world credit ratings
2. Government bond spreads
3. Historical credit rating data (optional)

Output files:
- government_bond_spreads.csv
- world_credit_ratings_with_numeric.csv
- credit_ratings_and_spreads.csv (merged data)
"""

import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import re
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'scraping_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)

# Rating conversion dictionaries
SP_RATINGS = {
    'AAA': 22, 'AA+': 21, 'AA': 20, 'AA-': 19,
    'A+': 18, 'A': 17, 'A-': 16,
    'BBB+': 15, 'BBB': 14, 'BBB-': 13,
    'BB+': 12, 'BB': 11, 'BB-': 10,
    'B+': 9, 'B': 8, 'B-': 7,
    'CCC+': 6, 'CCC': 5, 'CCC-': 4,
    'CC': 3, 'C': 2, 'D': 1
}

MOODYS_RATINGS = {
    'Aaa': 22, 'Aa1': 21, 'Aa2': 20, 'Aa3': 19,
    'A1': 18, 'A2': 17, 'A3': 16,
    'Baa1': 15, 'Baa2': 14, 'Baa3': 13,
    'Ba1': 12, 'Ba2': 11, 'Ba3': 10,
    'B1': 9, 'B2': 8, 'B3': 7,
    'Caa1': 6, 'Caa2': 5, 'Caa3': 4,
    'Ca': 3, 'C': 1
}

FITCH_RATINGS = {
    'AAA': 22, 'AA+': 21, 'AA': 20, 'AA-': 19,
    'A+': 18, 'A': 17, 'A-': 16,
    'BBB+': 15, 'BBB': 14, 'BBB-': 13,
    'BB+': 12, 'BB': 11, 'BB-': 10,
    'B+': 9, 'B': 8, 'B-': 7,
    'CCC+': 6, 'CCC': 5, 'CCC-': 4,
    'CC': 3, 'C': 2, 'D': 1
}

def setup_driver(headless=True):
    """Set up Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise

def extract_base_rating(rating_text):
    """Extract base rating without outlook indicators."""
    if not rating_text or rating_text in ['N/A', '-', '', 'NR']:
        return 'N/A'
    
    # Clean the rating text (now with extra spaces in the indicators)
    clean_rating = rating_text.replace('    [upgrade]', '').replace('    [downgrade]', '').strip()
    
    # Handle special cases
    if clean_rating in ['SD', 'RD']:
        return 'D'
    
    # Extract rating code
    match = re.search(r'([A-Za-z]{1,3}[\+\-]?[123]?)', clean_rating)
    if match:
        return match.group(1)
    return clean_rating

def convert_rating_to_numeric(rating_text, rating_dict):
    """Convert rating text to numeric value."""
    if not rating_text:
        return None
    
    # Check for upgrade/downgrade indicators (with extra spaces)
    upgrade_modifier = 0
    if isinstance(rating_text, str):
        if '    [upgrade]' in rating_text or '[upgrade]' in rating_text:
            upgrade_modifier = 1/3
        elif '    [downgrade]' in rating_text or '[downgrade]' in rating_text:
            upgrade_modifier = -1/3
    
    # Get base rating
    base_rating = extract_base_rating(rating_text)
    if base_rating == 'N/A':
        return None
    
    # Get numeric value
    base_numeric = rating_dict.get(base_rating, None)
    if base_numeric is None:
        return None
    
    return base_numeric + upgrade_modifier

def scrape_bond_spreads(driver):
    """Scrape government bond spreads data."""
    logger.info("Starting bond spreads scraping...")
    
    try:
        url = "https://www.worldgovernmentbonds.com/spread-historical-data/"
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Find tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        if not tables:
            logger.error("No tables found on bond spreads page")
            return None
        
        # Get the largest table
        target_table = max(tables, key=lambda t: len(t.find_elements(By.TAG_NAME, "tr")))
        all_rows = target_table.find_elements(By.TAG_NAME, "tr")
        
        # Extract data with correct column indices
        country_column_index = 1  # Country column
        usa_column_index = 4      # USA spread column
        
        data_rows = []
        for row in all_rows[2:]:  # Skip header rows
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > max(country_column_index, usa_column_index):
                country = cells[country_column_index].text.strip()
                usa_value = cells[usa_column_index].text.strip()
                
                if country and usa_value:
                    data_rows.append([country, usa_value])
        
        if data_rows:
            df = pd.DataFrame(data_rows, columns=["Country", "Spread"])
            
            # Clean spread values
            df["Spread"] = df["Spread"].str.replace(',', '').str.replace('%', '').str.replace('bp', '').str.strip()
            df["Spread"] = pd.to_numeric(df["Spread"], errors='coerce')
            df = df.dropna(subset=['Spread'])
            
            # Save to CSV
            df.to_csv("government_bond_spreads.csv", index=False)
            logger.info(f"Saved {len(df)} bond spread records")
            return df
        
    except Exception as e:
        logger.error(f"Error scraping bond spreads: {e}")
        return None

def scrape_credit_ratings(driver):
    """Scrape credit ratings data with numeric conversion."""
    logger.info("Starting credit ratings scraping...")
    
    try:
        url = "https://www.worldgovernmentbonds.com/world-credit-ratings/"
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Wait for tables
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        tables = driver.find_elements(By.TAG_NAME, "table")
        if not tables:
            logger.error("No tables found on credit ratings page")
            return None
        
        # Get the largest table
        target_table = max(tables, key=lambda t: len(t.find_elements(By.TAG_NAME, "tr")))
        rows = target_table.find_elements(By.TAG_NAME, "tr")
        
        # Extract headers
        header_row = rows[0]
        headers = [header.text.strip() for header in header_row.find_elements(By.TAG_NAME, "th")]
        
        # Find rating column indices (excluding DBRS)
        rating_columns = {}
        dbrs_index = None
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if "s&p" in header_lower:
                rating_columns["S&P"] = i
            elif "moody" in header_lower:
                rating_columns["Moody's"] = i
            elif "fitch" in header_lower:
                rating_columns["Fitch"] = i
            elif "dbrs" in header_lower:
                dbrs_index = i
        
        # Look for indicators
        red_selector = "i.w3-text-red.fa.fa-circle.w3-tiny"
        teal_selector = "i.w3-text-teal.fa.fa-circle.w3-tiny"
        
        # Extract data
        data_rows = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                row_data = []
                
                for i, cell in enumerate(cells):
                    # Skip DBRS column
                    if i == dbrs_index:
                        continue
                    
                    cell_text = cell.text.strip()
                    
                    # Check for indicators in rating columns
                    if i in rating_columns.values():
                        red_icons = cell.find_elements(By.CSS_SELECTOR, red_selector)
                        teal_icons = cell.find_elements(By.CSS_SELECTOR, teal_selector)
                        
                        if red_icons:
                            cell_text = f"{cell_text}    [downgrade]"
                        elif teal_icons:
                            cell_text = f"{cell_text}    [upgrade]"
                    
                    row_data.append(cell_text)
                
                if row_data:
                    data_rows.append(row_data)
        
        # Create headers without DBRS
        new_headers = [h for i, h in enumerate(headers) if i != dbrs_index]
        
        # Create DataFrame
        if data_rows:
            df = pd.DataFrame(data_rows, columns=new_headers)
            
            # Add numeric conversions
            rating_mappings = {
                "S&P": ("S&P_Numeric", SP_RATINGS),
                "Moody's": ("Moody's_Numeric", MOODYS_RATINGS),
                "Fitch": ("Fitch_Numeric", FITCH_RATINGS)
            }
            
            for agency, (numeric_col, rating_dict) in rating_mappings.items():
                # Find the column for this agency
                agency_col = None
                for col in df.columns:
                    if agency.lower() in col.lower():
                        agency_col = col
                        break
                
                if agency_col:
                    df[numeric_col] = df[agency_col].apply(
                        lambda x: convert_rating_to_numeric(x, rating_dict)
                    )
            
            # Add average rating and count
            numeric_cols = ['S&P_Numeric', "Moody's_Numeric", 'Fitch_Numeric']
            df['Average_Rating'] = df[numeric_cols].mean(axis=1, skipna=True).round(2)
            df['Ratings_Count'] = df[numeric_cols].count(axis=1)
            
            # Save to CSV
            df.to_csv("world_credit_ratings_with_numeric.csv", index=False)
            logger.info(f"Saved {len(df)} credit rating records")
            return df
        
    except Exception as e:
        logger.error(f"Error scraping credit ratings: {e}")
        return None

def clean_country_name(name):
    """Clean country name by removing asterisks and parentheses."""
    if not isinstance(name, str):
        return name
    
    # Remove (*) and any parenthetical expressions
    name = re.sub(r'\s*\([^)]*\)\s*', '', name)
    return name.strip()

# Country name corrections for merging
COUNTRY_NAME_MAPPING = {
    "UK": "Ukraine",  # UK in this dataset means Ukraine, not United Kingdom
}

def merge_datasets(spread_df, ratings_df):
    """Merge bond spreads and credit ratings datasets."""
    logger.info("Merging datasets...")
    
    # Find the country column in ratings dataframe
    country_column = None
    for col in ratings_df.columns:
        if 'country' in col.lower():
            country_column = col
            break
    
    if not country_column:
        logger.error("Could not find country column in ratings dataframe")
        return None
    
    # Clean country names
    spread_df['Country_Clean'] = spread_df['Country'].apply(clean_country_name)
    ratings_df['Country_Clean'] = ratings_df[country_column].apply(clean_country_name)
    
    # Merge datasets
    merged_df = pd.merge(
        spread_df,
        ratings_df,
        left_on='Country_Clean',
        right_on='Country_Clean',
        how='inner'
    )
    
    # Keep relevant columns
    cols_to_keep = ['Country', 'Spread']
    for col in ratings_df.columns:
        if col != country_column and col != 'Country_Clean' and col in merged_df.columns:
            cols_to_keep.append(col)
    
    # Filter and reorder columns
    cols_to_keep = [col for col in cols_to_keep if col in merged_df.columns]
    merged_df = merged_df[cols_to_keep]
    
    # Sort by average rating if available
    if 'Average_Rating' in merged_df.columns:
        merged_df = merged_df.sort_values(by='Average_Rating', ascending=False)
    else:
        merged_df = merged_df.sort_values(by='Country')
    
    # Save merged data
    merged_df.to_csv("credit_ratings_and_spreads.csv", index=False)
    logger.info(f"Saved merged dataset with {len(merged_df)} countries")
    
    return merged_df

def main():
    """Main execution function."""
    logger.info("Starting World Government Bonds data scraping...")
    
    driver = None
    try:
        # Initialize driver
        driver = setup_driver(headless=True)
        
        # Scrape bond spreads
        spread_df = scrape_bond_spreads(driver)
        if spread_df is None:
            logger.error("Failed to scrape bond spreads")
            return
        
        # Scrape credit ratings
        ratings_df = scrape_credit_ratings(driver)
        if ratings_df is None:
            logger.error("Failed to scrape credit ratings")
            return
        
        # Merge datasets
        merged_df = merge_datasets(spread_df, ratings_df)
        
        if merged_df is not None:
            logger.info("Scraping completed successfully!")
            logger.info("Output files:")
            logger.info("  - government_bond_spreads.csv")
            logger.info("  - world_credit_ratings_with_numeric.csv")
            logger.info("  - credit_ratings_and_spreads.csv (merged data)")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver closed")

if __name__ == "__main__":
    main()