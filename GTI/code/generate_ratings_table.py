#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_ratings_table.py - Generate a summary table of countries by rating grade
"""

import pandas as pd
import numpy as np

# Rating grade categories based on the image
RATING_GRADES = {
    'Prime': {'S&P': ['AAA'], 'Moody\'s': ['Aaa'], 'range': (22, 22)},
    'High Medium Grade': {'S&P': ['AA+', 'AA', 'AA-'], 'Moody\'s': ['Aa1', 'Aa2', 'Aa3'], 'range': (19, 21)},
    'Upper Medium Grade': {'S&P': ['A+', 'A', 'A-'], 'Moody\'s': ['A1', 'A2', 'A3'], 'range': (16, 18)},
    'Lower Medium Grade': {'S&P': ['BBB+', 'BBB', 'BBB-'], 'Moody\'s': ['Baa1', 'Baa2', 'Baa3'], 'range': (13, 15)},
    'Speculative': {'S&P': ['BB+', 'BB', 'BB-'], 'Moody\'s': ['Ba1', 'Ba2', 'Ba3'], 'range': (10, 12)},
    'Highly Speculative': {'S&P': ['B+', 'B', 'B-'], 'Moody\'s': ['B1', 'B2', 'B3'], 'range': (7, 9)},
    'Substantial Risk': {'S&P': ['CCC+', 'CCC', 'CCC-'], 'Moody\'s': ['Caa1', 'Caa2', 'Caa3'], 'range': (4, 6)},
    'Extremely Speculative': {'S&P': ['CC', 'C'], 'Moody\'s': ['Ca'], 'range': (2, 3)},
    'In Default': {'S&P': ['D'], 'Moody\'s': ['C'], 'range': (1, 1)}
}

def categorize_by_average_rating(avg_rating):
    """Categorize a country based on its average numeric rating."""
    if pd.isna(avg_rating):
        return 'No Rating'
    
    for grade, info in RATING_GRADES.items():
        min_val, max_val = info['range']
        if min_val <= avg_rating <= max_val:
            return grade
    
    return 'No Rating'

def generate_ratings_summary_table():
    """Generate a summary table of countries grouped by rating grade."""
    
    try:
        # Read the credit ratings file with numeric values
        df = pd.read_csv('world_credit_ratings_with_numeric.csv')
        
        # Find the country column
        country_col = None
        for col in df.columns:
            if 'country' in col.lower():
                country_col = col
                break
        
        if not country_col:
            print("Error: Could not find country column")
            return None
        
        # Ensure Average_Rating column exists
        if 'Average_Rating' not in df.columns:
            print("Error: Average_Rating column not found")
            return None
        
        # Add grade category
        df['Grade_Category'] = df['Average_Rating'].apply(categorize_by_average_rating)
        
        # Create simple output table with just Grade and Countries
        output_data = []
        
        # Define order of grades (from best to worst)
        grade_order = [
            'Prime',
            'High Medium Grade', 
            'Upper Medium Grade',
            'Lower Medium Grade',
            'Speculative',
            'Highly Speculative',
            'Substantial Risk',
            'Extremely Speculative',
            'In Default',
            'No Rating'
        ]
        
        for grade in grade_order:
            countries_in_grade = df[df['Grade_Category'] == grade]
            
            if not countries_in_grade.empty:
                # Sort countries by average rating within the grade (best first)
                countries_in_grade = countries_in_grade.sort_values('Average_Rating', ascending=False)
                country_list = countries_in_grade[country_col].tolist()
                
                # Join all countries with comma separator
                output_data.append({
                    'Grade': grade,
                    'Countries': ', '.join(country_list)
                })
        
        # Create output DataFrame
        output_df = pd.DataFrame(output_data)
        
        # Save to CSV
        output_df.to_csv('ratings_by_grade.csv', index=False)
        print("Ratings summary saved to: ratings_by_grade.csv")
        
        # Display the table
        print("\nRatings by Grade:")
        print("-" * 50)
        for _, row in output_df.iterrows():
            countries = row['Countries'].split(', ')
            print(f"\n{row['Grade']} ({len(countries)} countries):")
            print(f"  {row['Countries']}")
        
        return output_df
        
    except FileNotFoundError:
        print("Error: Could not find 'world_credit_ratings_with_numeric.csv'")
        print("Please run scrape_bond_data.py first to generate the data.")
        return None
    except Exception as e:
        print(f"Error generating ratings table: {e}")
        return None

if __name__ == "__main__":
    df = generate_ratings_summary_table()
    
    if df is not None:
        print("\n\nRatings table generation complete!")