# Bond Data Scraping and Visualization

This project scrapes sovereign credit ratings and government bond spread data from worldgovernmentbonds.com and creates professional visualizations.

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- Internet connection for web scraping

## Setup Instructions

### 1. Create a Virtual Environment

```bash
# Navigate to the project directory
cd /Users/mac/Desktop/Trustworthy_Digital_Society/GTI/code

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Required Packages

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install pandas numpy selenium webdriver-manager matplotlib seaborn

# For flag icons (optional but recommended):
pip install requests cairosvg

# If you encounter issues with cairosvg on macOS, you may need to install cairo first:
# brew install cairo
```

### 3. Create requirements.txt (for future use)

```bash
pip freeze > requirements.txt
```

## Running the Scripts

### Step 1: Scrape the Data

```bash
python scrape_bond_data.py
```

This will:
- Download and install ChromeDriver automatically (first run only)
- Scrape bond spread data from worldgovernmentbonds.com
- Scrape credit ratings data with S&P, Moody's, and Fitch ratings
- Convert ratings to numeric scale (1-22)
- Merge the datasets
- Create three CSV files:
  - `government_bond_spreads.csv`
  - `world_credit_ratings_with_numeric.csv`
  - `credit_ratings_and_spreads.csv` (merged data)

Expected runtime: 2-5 minutes

### Step 2: Create Visualizations

```bash
python visualize_bond_data.py
```

This will:
- Load the merged data from Step 1
- Download country flag icons (first run only)
- Create two visualization files:
  - `bond_spreads_vs_ratings.png` - Full scatter plot with all countries
  - `investment_grade_plot.png` - Investment-grade countries only

Expected runtime: 1-2 minutes

## Output Files

### Data Files (CSV)
- `government_bond_spreads.csv` - Bond spread data for each country
- `world_credit_ratings_with_numeric.csv` - Credit ratings with numeric conversions
- `credit_ratings_and_spreads.csv` - Merged dataset used for visualization

### Visualization Files (PNG)
- `bond_spreads_vs_ratings.png` - Full scatter plot (12x12 inches, 300 DPI)
- `investment_grade_plot.png` - Investment-grade plot (3732x3566 pixels)

### Log Files
- `scraping_YYYYMMDD_HHMMSS.log` - Detailed scraping log with timestamps

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver errors:
```bash
# Option 1: Let webdriver-manager handle it (recommended)
# This is already done in the script

# Option 2: Install ChromeDriver manually via Homebrew (macOS)
brew install chromedriver

# Then allow it in Security & Privacy settings if blocked
```

### Permission Errors on macOS
If ChromeDriver is blocked by macOS security:
1. Go to System Preferences > Security & Privacy
2. Click "Allow Anyway" for chromedriver
3. Run the script again

### Missing Dependencies
If you get import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux

# Reinstall all requirements
pip install -r requirements.txt
```

### Cairo/CairoSVG Issues (for flag icons)
If cairosvg installation fails:
```bash
# On macOS:
brew install cairo pkg-config

# On Ubuntu/Debian:
sudo apt-get install libcairo2-dev

# Then retry:
pip install cairosvg
```

Note: The visualization will still work without cairosvg - it will use country ISO codes instead of flags.

## Customization

### Modify Scraping Behavior
In `scrape_bond_data.py`:
- `headless=True` - Set to `False` to see browser window during scraping
- Add delays between requests by modifying `time.sleep()` values

### Modify Visualizations
In `visualize_bond_data.py`:
- `jitter_x=5` - Adjust horizontal scatter of points
- `flag_height=24` - Change size of flag icons
- Color schemes in `sns.color_palette()`
- Figure dimensions in `figure.figsize`

## Project Structure

```
code/
├── scrape_bond_data.py      # Web scraping script
├── visualize_bond_data.py   # Visualization script
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── venv/                   # Virtual environment (created)
├── flag_icons/            # Country flags (created on first run)
├── *.csv                  # Data files (created after scraping)
├── *.png                  # Chart images (created after visualization)
└── *.log                  # Log files (created during execution)
```

## Notes

- The scraper uses Selenium WebDriver in headless mode by default
- Data is scraped from public sources at worldgovernmentbonds.com
- Be respectful of the website's resources - avoid running too frequently
- The scripts include error handling and will log any issues
- Flag icons are cached locally after first download

## License

This project is for educational and research purposes. Please respect the terms of service of the data sources.