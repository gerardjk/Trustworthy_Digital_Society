#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wgi_correlation_complete.py - Complete WGI Correlation Analysis Tool

This single script handles everything:
1. Downloads WGI data automatically from World Bank API
2. Allows you to specify year range
3. Calculates correlation matrix
4. Compares with document values
5. Saves results

Usage: python wgi_correlation_complete.py
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
import time

# ========================================
# CONFIGURATION - MODIFY THESE SETTINGS
# ========================================
START_YEAR = 2010  # Starting year for analysis (minimum: 1996)
END_YEAR = 2023    # Ending year for analysis (maximum: 2023)

# Set to True to save intermediate files
SAVE_RAW_DATA = True

# ========================================

def download_wgi_data(start_year=1996, end_year=2023):
    """
    Download WGI data from World Bank API for specified years.
    """
    print(f"\nDownloading WGI data for {start_year}-{end_year}...")
    print("-" * 50)
    
    # WGI indicator codes
    indicators = {
        'VA.EST': 'Voice and Accountability',
        'PV.EST': 'Political Stability',
        'GE.EST': 'Government Effectiveness',
        'RQ.EST': 'Regulatory Quality',
        'RL.EST': 'Rule of Law',
        'CC.EST': 'Control of Corruption'
    }
    
    all_data = []
    
    for code, name in indicators.items():
        print(f"Downloading {name}...", end="")
        
        # World Bank API endpoint
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}"
        params = {
            'format': 'json',
            'per_page': '20000',
            'date': f'{start_year}:{end_year}'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1 and isinstance(data[1], list):
                    for record in data[1]:
                        if record.get('value') is not None:
                            all_data.append({
                                'Country': record.get('country', {}).get('value', ''),
                                'Country_Code': record.get('countryiso3code', ''),
                                'Year': int(record.get('date', 0)),
                                'Indicator': code,
                                'Indicator_Name': name,
                                'Value': float(record.get('value', 0))
                            })
                    print(f" ✓ ({len(data[1])} records)")
                else:
                    print(" ✗ (no data)")
            else:
                print(f" ✗ (HTTP {response.status_code})")
                
            # Small delay to be nice to the API
            time.sleep(0.5)
            
        except Exception as e:
            print(f" ✗ (Error: {str(e)[:30]})")
    
    if not all_data:
        print("\n⚠ No data downloaded. Using fallback method...")
        return create_sample_data(start_year, end_year)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Pivot to wide format
    df_pivot = df.pivot_table(
        index=['Country', 'Country_Code', 'Year'],
        columns='Indicator',
        values='Value',
        aggfunc='first'
    ).reset_index()
    
    # Rename columns to short names
    df_pivot.columns.name = None
    column_mapping = {
        'VA.EST': 'VA',
        'PV.EST': 'PSV',
        'GE.EST': 'GE',
        'RQ.EST': 'RQ',
        'RL.EST': 'RL',
        'CC.EST': 'CC'
    }
    df_pivot.rename(columns=column_mapping, inplace=True)
    
    print(f"\n✓ Downloaded data for {df_pivot['Country'].nunique()} countries")
    print(f"✓ Years: {df_pivot['Year'].min()}-{df_pivot['Year'].max()}")
    print(f"✓ Total observations: {len(df_pivot)}")
    
    if SAVE_RAW_DATA:
        filename = f'wgi_raw_data_{start_year}_{end_year}.csv'
        df_pivot.to_csv(filename, index=False)
        print(f"✓ Raw data saved to {filename}")
    
    return df_pivot

def create_sample_data(start_year, end_year):
    """
    Create sample data if download fails.
    """
    print("\nGenerating sample data for demonstration...")
    
    np.random.seed(42)
    
    countries = ['United States', 'United Kingdom', 'Germany', 'France', 'Japan',
                 'Canada', 'Australia', 'Brazil', 'India', 'China']
    
    data = []
    for year in range(start_year, end_year + 1):
        for country in countries:
            base = np.random.randn() * 0.5
            data.append({
                'Country': country,
                'Country_Code': country[:3].upper(),
                'Year': year,
                'VA': base + np.random.randn() * 0.3,
                'PSV': base + np.random.randn() * 0.3,
                'GE': base + np.random.randn() * 0.2,
                'RQ': base + np.random.randn() * 0.2,
                'RL': base + np.random.randn() * 0.2,
                'CC': base + np.random.randn() * 0.2
            })
    
    df = pd.DataFrame(data)
    
    # Clip to WGI range
    for col in ['VA', 'PSV', 'GE', 'RQ', 'RL', 'CC']:
        df[col] = df[col].clip(-2.5, 2.5)
    
    return df

def calculate_correlation_matrix(df, method='pooled'):
    """
    Calculate correlation matrix using specified method.
    
    Methods:
    - 'pooled': All observations together
    - 'yearly_avg': Average of yearly correlations
    - 'latest': Most recent year only
    """
    # Remove rows with missing values
    indicator_cols = ['VA', 'PSV', 'GE', 'RQ', 'RL', 'CC']
    df_clean = df[['Year', 'Country'] + indicator_cols].dropna()
    
    if method == 'pooled':
        # Use all observations
        corr_matrix = df_clean[indicator_cols].corr()
        
    elif method == 'yearly_avg':
        # Calculate correlation for each year, then average
        yearly_corrs = []
        for year in df_clean['Year'].unique():
            year_data = df_clean[df_clean['Year'] == year][indicator_cols]
            if len(year_data) > 10:
                yearly_corrs.append(year_data.corr())
        
        if yearly_corrs:
            # Average across years
            corr_matrix = pd.concat(yearly_corrs).groupby(level=0).mean()
        else:
            corr_matrix = df_clean[indicator_cols].corr()
            
    elif method == 'latest':
        # Use only the most recent year
        latest_year = df_clean['Year'].max()
        latest_data = df_clean[df_clean['Year'] == latest_year][indicator_cols]
        corr_matrix = latest_data.corr()
    
    else:
        corr_matrix = df_clean[indicator_cols].corr()
    
    return corr_matrix, len(df_clean)

def display_correlation_matrix(corr_matrix, title="Correlation Matrix"):
    """
    Display correlation matrix in formatted table.
    """
    print("\n" + "="*60)
    print(title)
    print("="*60)
    
    indicators = corr_matrix.columns.tolist()
    
    # Header
    print("      ", end="")
    for ind in indicators:
        print(f"{ind:>7}", end="")
    print("\n" + "-"*50)
    
    # Lower triangular display
    for i, row_ind in enumerate(indicators):
        print(f"{row_ind:5} ", end="")
        for j, col_ind in enumerate(indicators):
            if i == j:
                print(f"{'1.00':>7}", end="")
            elif i > j:
                value = corr_matrix.loc[row_ind, col_ind]
                print(f"{value:7.2f}", end="")
            else:
                print(f"{'':>7}", end="")
        print()

def compare_with_document(corr_matrix):
    """
    Compare calculated correlations with Table 6 from the document.
    """
    print("\n" + "="*60)
    print("COMPARISON WITH DOCUMENT (Table 6)")
    print("="*60)
    
    # Values from the GTI document Table 6
    doc_values = {
        ('VA', 'PSV'): 0.51,
        ('VA', 'GE'): 0.46,
        ('VA', 'RQ'): 0.66,
        ('VA', 'RL'): 0.63,
        ('VA', 'CC'): 0.52,
        ('PSV', 'GE'): 0.81,
        ('PSV', 'RQ'): 0.80,
        ('PSV', 'RL'): 0.82,
        ('PSV', 'CC'): 0.79,
        ('GE', 'RQ'): 0.87,
        ('GE', 'RL'): 0.89,
        ('GE', 'CC'): 0.86,
        ('RQ', 'RL'): 0.87,
        ('RQ', 'CC'): 0.87,
        ('RL', 'CC'): 0.88
    }
    
    print("\n{:<10} {:>10} {:>10} {:>12}".format(
        "Pair", "Document", "Calculated", "Difference"))
    print("-"*45)
    
    differences = []
    for (ind1, ind2), doc_val in doc_values.items():
        calc_val = corr_matrix.loc[ind1, ind2]
        diff = calc_val - doc_val
        differences.append(abs(diff))
        
        # Mark large differences
        mark = "*" if abs(diff) > 0.05 else " "
        print(f"{ind1}-{ind2:<5} {doc_val:10.2f} {calc_val:10.2f} {diff:12.3f} {mark}")
    
    print("-"*45)
    print(f"Average absolute difference: {np.mean(differences):.3f}")
    print(f"Maximum absolute difference: {np.max(differences):.3f}")
    print("\n* indicates difference > 0.05")

def save_results(corr_matrix, n_obs, start_year, end_year):
    """
    Save results to CSV file.
    """
    filename = f'wgi_correlation_{start_year}_{end_year}.csv'
    corr_matrix.round(3).to_csv(filename)
    
    # Also save a summary file
    summary_file = f'wgi_correlation_summary_{start_year}_{end_year}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"WGI Correlation Analysis Summary\n")
        f.write(f"="*50 + "\n")
        f.write(f"Date Range: {start_year}-{end_year}\n")
        f.write(f"Observations: {n_obs}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("Correlation Matrix:\n")
        f.write(corr_matrix.round(3).to_string())
    
    print(f"\n✓ Results saved to:")
    print(f"  - {filename}")
    print(f"  - {summary_file}")

def main():
    """
    Main function - runs the complete analysis.
    """
    print("\n" + "="*70)
    print("WGI CORRELATION ANALYSIS - COMPLETE TOOL")
    print("="*70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Selected Period: {START_YEAR}-{END_YEAR}")
    
    # Step 1: Download data
    df = download_wgi_data(START_YEAR, END_YEAR)
    
    if df is None or df.empty:
        print("\n⚠ Failed to obtain data. Exiting.")
        return
    
    # Step 2: Calculate correlations using different methods
    print("\n" + "="*60)
    print("CALCULATING CORRELATIONS")
    print("="*60)
    
    # Method 1: Pooled (all observations)
    corr_pooled, n_obs = calculate_correlation_matrix(df, method='pooled')
    display_correlation_matrix(corr_pooled, 
        f"POOLED CORRELATION ({START_YEAR}-{END_YEAR}, n={n_obs})")
    
    # Method 2: Yearly average
    corr_yearly, _ = calculate_correlation_matrix(df, method='yearly_avg')
    display_correlation_matrix(corr_yearly, 
        f"AVERAGE YEARLY CORRELATION ({START_YEAR}-{END_YEAR})")
    
    # Method 3: Latest year only
    corr_latest, n_latest = calculate_correlation_matrix(df, method='latest')
    latest_year = df['Year'].max()
    display_correlation_matrix(corr_latest, 
        f"LATEST YEAR ONLY ({latest_year}, n={n_latest})")
    
    # Step 3: Compare with document
    print("\nUsing pooled correlation for comparison:")
    compare_with_document(corr_pooled)
    
    # Step 4: Calculate summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS (Pooled Correlation)")
    print("="*60)
    
    # Get upper triangle values
    upper_tri = corr_pooled.where(
        np.triu(np.ones(corr_pooled.shape), k=1).astype(bool)
    )
    corr_values = upper_tri.stack().values
    
    print(f"Number of observations: {n_obs}")
    print(f"Average correlation: {np.mean(corr_values):.3f}")
    print(f"Median correlation: {np.median(corr_values):.3f}")
    print(f"Minimum correlation: {np.min(corr_values):.3f}")
    print(f"Maximum correlation: {np.max(corr_values):.3f}")
    print(f"Standard deviation: {np.std(corr_values):.3f}")
    
    # Step 5: Save results
    save_results(corr_pooled, n_obs, START_YEAR, END_YEAR)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()