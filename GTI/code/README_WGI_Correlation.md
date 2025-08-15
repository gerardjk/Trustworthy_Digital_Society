# WGI Correlation Matrix Updater

This folder contains Python scripts to update the Worldwide Governance Indicators (WGI) correlation matrix shown in Table 6 of the GTI document.

## Files

1. **update_wgi_correlation.py** - Comprehensive script that attempts to automatically download WGI data
2. **wgi_correlation_simple.py** - Simpler version that works with manually downloaded CSV files
3. **requirements_wgi.txt** - Python package dependencies

## Setup

Install required packages:
```bash
pip install -r requirements_wgi.txt
```

## Usage

### Option 1: Automatic Download (update_wgi_correlation.py)
```bash
python update_wgi_correlation.py
```
This script will:
- Attempt to download the latest WGI data from World Bank
- Calculate the correlation matrix
- Display formatted results matching Table 6 format
- Save results to CSV

### Option 2: Manual Data Download (wgi_correlation_simple.py)

1. Download WGI data from World Bank:
   - Go to: https://databank.worldbank.org/source/worldwide-governance-indicators
   - Select all 6 indicators (Voice & Accountability, Political Stability, etc.)
   - Select the most recent year available
   - Select all countries
   - Export as CSV

2. Save the file as `wgi_data.csv` in this directory

3. Run the script:
```bash
python wgi_correlation_simple.py
```

This script will:
- Load your CSV file
- Calculate correlations
- Create a heatmap visualization
- Compare results with document values
- Save results to CSV

## Output Files

- **wgi_correlation_matrix_YYYYMMDD.csv** - Correlation matrix in CSV format
- **wgi_correlation_heatmap_YYYYMMDD.png** - Heatmap visualization (simple version only)

## Understanding the Results

The correlation matrix shows how the six WGI indicators relate to each other:
- **VA**: Voice and Accountability
- **PSV**: Political Stability and Absence of Violence/Terrorism
- **GE**: Government Effectiveness
- **RQ**: Regulatory Quality
- **RL**: Rule of Law
- **CC**: Control of Corruption

Higher correlations (closer to 1.0) indicate that countries scoring high on one indicator tend to score high on the other.

## Expected Differences from Document

You may see small differences from the values in Table 6 due to:
- Using a different year of data (document may use older data)
- Updates to the WGI methodology over time
- Changes in which countries are included
- Data revisions by the World Bank

Typical differences should be less than 0.05 for most correlations.

## Troubleshooting

**Problem**: Can't download data automatically
- **Solution**: Use the manual download option with wgi_correlation_simple.py

**Problem**: CSV columns not recognized
- **Solution**: Ensure your CSV includes columns with indicator names (e.g., containing "Voice and Accountability", "Political Stability", etc.)

**Problem**: Missing data warnings
- **Solution**: This is normal - some countries may lack data for certain indicators

## Data Source

World Bank Worldwide Governance Indicators:
- Website: https://info.worldbank.org/governance/wgi/
- Databank: https://databank.worldbank.org/source/worldwide-governance-indicators

## Notes

The WGI are updated annually, typically released in September/October with data through the previous year.