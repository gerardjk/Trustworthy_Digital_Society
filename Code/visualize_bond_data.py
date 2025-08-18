#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visualize_bond_data.py - Creates bond spreads vs credit ratings visualizations

This script creates two charts:
1. Full scatter plot showing all countries
2. Investment-grade only plot (BBB and above)

Input: credit_ratings_and_spreads.csv
Output: 
- bond_spreads_vs_ratings.png
- investment_grade_plot.png
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Country to ISO code mapping
COUNTRY_TO_CODE = {
    "Switzerland": "ch", "Singapore": "sg", "Norway": "no", "Netherlands": "nl",
    "Germany": "de", "Australia": "au", "Sweden": "se", "Denmark": "dk",
    "Canada": "ca", "New Zealand": "nz", "United States": "us", "USA": "us",
    "Finland": "fi", "Austria": "at", "Qatar": "qa", "Taiwan": "tw",
    "Ireland": "ie", "South Korea": "kr", "Korea, South": "kr", "Hong Kong": "hk",
    "United Kingdom": "gb", "UK": "ua", "Uk": "ua", "uk": "ua", "Belgium": "be", "Czech Republic": "cz",
    "Czechia": "cz", "France": "fr", "Iceland": "is", "Slovenia": "si",
    "Japan": "jp", "China": "cn", "Lithuania": "lt", "Malta": "mt",
    "Chile": "cl", "Portugal": "pt", "Slovakia": "sk", "Poland": "pl",
    "Spain": "es", "Croatia": "hr", "Cyprus": "cy", "Israel": "il",
    "Malaysia": "my", "Botswana": "bw", "Bulgaria": "bg", "Philippines": "ph",
    "Italy": "it", "Indonesia": "id", "Peru": "pe", "Kazakhstan": "kz",
    "Mexico": "mx", "Hungary": "hu", "Greece": "gr", "India": "in",
    "Mauritius": "mu", "Romania": "ro", "Colombia": "co", "Serbia": "rs",
    "Morocco": "ma", "Vietnam": "vn", "Brazil": "br", "South Africa": "za",
    "Jordan": "jo", "Namibia": "na", "Turkey": "tr", "Bangladesh": "bd",
    "Bahrain": "bh", "Uganda": "ug", "Nigeria": "ng", "Egypt": "eg",
    "Kenya": "ke", "Pakistan": "pk", "Sri Lanka": "lk", "Zambia": "zm",
    "Ukraine": "ua", "Ukraine (*)": "ua", "Russia": "ru", "Bosnia and Herzegovina": "ba",
    "Bosnia": "ba", "Bolivia": "bo"
}

# Rating number to letter mapping
RATING_LABEL = {
    22: "AAA", 21: "AA+", 20: "AA", 19: "AA-", 18: "A+", 17: "A", 16: "A-",
    15: "BBB+", 14: "BBB", 13: "BBB-", 12: "BB+", 11: "BB", 10: "BB-",
    9: "B+", 8: "B", 7: "B-", 6: "CCC+", 5: "CCC", 4: "CCC-",
    3: "CC", 2: "C", 1: "D"
}

def load_icon(code: str, icon_dir: Path):
    """Load flag icon for given country code."""
    png_path = icon_dir / f"{code}.png"
    if png_path.exists():
        return plt.imread(png_path)
    return None

def create_full_plot(df, icon_dir, output_file="bond_spreads_vs_ratings.png",
                    jitter_x=5, label_dx=8, flag_height=24):
    """Create the full scatter plot with all countries."""
    logger.info("Creating full bond spreads vs ratings plot...")
    
    # Set style with Arial font and internal tick marks
    mpl.rcParams.update({
        "figure.figsize": (12, 12),
        "axes.titlesize": 40, "axes.labelsize": 32,
        "xtick.labelsize": 24, "ytick.labelsize": 24,
        "legend.fontsize": 24,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],  # Arial first
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 6,
        "ytick.major.size": 6,
    })
    
    # Force matplotlib to use Arial if available
    import matplotlib.font_manager as fm
    arial_fonts = [f for f in fm.fontManager.ttflist if f.name == 'Arial']
    if arial_fonts:
        plt.rcParams['font.sans-serif'].insert(0, 'Arial')
    
    palette = sns.color_palette("bright", 3)
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    
    # Prepare data
    df["Spread_Numeric"] = pd.to_numeric(df["Spread"], errors='coerce')
    
    # Create figure
    fig, ax = plt.subplots()
    
    # Set tick parameters for this axes
    ax.tick_params(axis='both', direction='in', length=6)
    
    per_ctry = {}
    all_x_vals = []
    all_y_vals = []
    
    # Plot each agency's ratings
    for colour, (col, lbl) in zip(
            palette,
            [("S&P_Numeric", "S&P"), ("Moody's_Numeric", "Moody's"), 
             ("Fitch_Numeric", "Fitch")]):
        
        if col not in df.columns:
            continue
            
        sub = df.dropna(subset=[col, "Spread_Numeric"])
        jitter_x_vals = sub["Spread_Numeric"] + rng.normal(0, jitter_x, len(sub))
        y_vals = sub[col]
        
        ax.scatter(jitter_x_vals, y_vals, s=140, c=[colour],
                   alpha=.85, label=lbl)
        
        all_x_vals.extend(sub["Spread_Numeric"].tolist())
        all_y_vals.extend(y_vals.tolist())
        
        for ctry, x0, y0 in zip(sub["Country"], sub["Spread_Numeric"], sub[col]):
            d = per_ctry.setdefault(ctry, {"x": x0, "ys": []})
            d["ys"].append(y0)
    
    # Draw vertical tie lines
    for d in per_ctry.values():
        if len(d["ys"]) > 1:
            ax.plot([d["x"], d["x"]], [min(d["ys"]), max(d["ys"])],
                    color="grey", lw=2, alpha=.55, zorder=2)
    
    # Add correlation line
    x_arr = np.array(all_x_vals)
    y_arr = np.array(all_y_vals)
    m, b = np.polyfit(x_arr, y_arr, 1)
    xs = np.linspace(x_arr.min(), x_arr.max(), 100)
    ax.plot(xs, m*xs + b, color='black', lw=2, linestyle='--', zorder=1)
    
    # Calculate and display correlation
    corr = np.corrcoef(x_arr, y_arr)[0, 1]
    ax.text(0.95, 0.05, f"r = {corr:.2f}", transform=ax.transAxes,
            ha='right', va='bottom', fontsize=20, 
            bbox=dict(facecolor='white', alpha=0.7))
    
    # Add country labels/flags with improved positioning
    # Sort countries by x-position for better overlap handling
    country_data = []
    for _, row in df.iterrows():
        ctry = row["Country"]
        code = COUNTRY_TO_CODE.get(ctry, ctry[:2].lower())
        
        # Debug for UK/Ukraine
        if ctry == "UK" or "ukraine" in ctry.lower():
            logger.info(f"Country: '{ctry}' -> Code: '{code}' (should be 'ua' for Ukraine)")
        
        x = row["Spread_Numeric"]
        
        # Get the maximum rating for this country
        rating_cols = ["S&P_Numeric", "Moody's_Numeric", "Fitch_Numeric"]
        ratings = [row.get(c, np.nan) for c in rating_cols]
        y = np.nanmax(ratings)
        
        if not np.isnan(x) and not np.isnan(y):
            country_data.append((x, y, ctry, code))
    
    # Sort by x position
    country_data.sort(key=lambda item: item[0])
    
    # Track positions to avoid overlaps
    used_positions = []
    min_distance = 0.8  # Minimum vertical distance between flags
    
    for x, y, ctry, code in country_data:
        lx = x + label_dx
        ly = y
        
        # Check for overlaps and adjust position
        for used_x, used_y in used_positions:
            if abs(lx - used_x) < 50:  # If x positions are close
                if abs(ly - used_y) < min_distance:
                    # Adjust position up or down
                    if ly >= used_y:
                        ly = used_y + min_distance
                    else:
                        ly = used_y - min_distance
        
        used_positions.append((lx, ly))
        
        icon = load_icon(code, icon_dir)
        
        if icon is not None:
            zoom = flag_height / icon.shape[0]
            ab = AnnotationBbox(OffsetImage(icon, zoom=zoom),
                                (lx, ly), frameon=False,
                                box_alignment=(0, .5), zorder=4)
            ax.add_artist(ab)
        else:
            # Log which flag is missing
            if ctry == "UK":
                logger.warning(f"Flag not found for {ctry} (code: {code}), using text instead")
            ax.text(lx, ly, code.upper(), fontsize=14, fontweight="bold",
                    va="center", zorder=4)
    
    # Add shaded backgrounds
    ax.axhspan(13, 22, color="#cce6ff", alpha=.25, zorder=0)  # Investment grade
    ax.axhspan(1, 13, color="#e8d5ff", alpha=.25, zorder=0)   # Speculative grade
    
    ax.text(ax.get_xlim()[1]*.985, 13.2, "Investment Grade",
            ha="right", va="bottom", color="navy", fontsize=18, alpha=.8)
    ax.text(ax.get_xlim()[1]*.985, 12.8, "Speculative Grade",
            ha="right", va="top", color="#5e3b7f", fontsize=18, alpha=.8)
    
    # Set Y-axis labels
    ticks = range(1, 23)
    ax.set_yticks(ticks)
    ax.set_yticklabels([RATING_LABEL.get(t, "") for t in ticks])
    
    # Labels and formatting
    ax.set_xlabel("10-Year Bond Spread to US (bp)")
    ax.set_ylabel("Credit Rating")
    ax.set_title("Bond Spreads vs. Sovereign Credit Ratings", pad=45, fontweight='bold')
    
    # Set axis limits
    pad = (x_arr.max() - x_arr.min()) * .05
    ax.set_xlim(x_arr.min()-pad, x_arr.max()+pad)
    ax.set_ylim(0, 23.5)
    
    # Add reference line and grid
    ax.axvline(0, color="black", lw=2, alpha=.4)
    ax.grid(alpha=.3)
    ax.legend()
    
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    logger.info(f"Saved full plot: {output_file}")

def create_investment_grade_plot(df, icon_dir, output_file="investment_grade_plot.png",
                                jitter_x=5, label_dx=8, flag_height=24):
    """Create investment-grade only plot."""
    logger.info("Creating investment-grade plot...")
    
    # Filter for investment grade only (rating >= 14)
    agency_cols = ["S&P_Numeric", "Moody's_Numeric", "Fitch_Numeric"]
    df_filtered = df[df[agency_cols].max(axis=1) >= 14].copy()
    
    # Calculate exact figure dimensions for 3732x3566 pixels at 300 dpi
    width_inches = 3732 / 300
    height_inches = 3566 / 300
    
    # Reset matplotlib defaults
    mpl.rcdefaults()
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],  # Arial first
        'font.size': 12,
        'axes.titlesize': 40,
        'axes.labelsize': 32,
        'xtick.labelsize': 24,
        'ytick.labelsize': 24,
        'legend.fontsize': 24,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 6,
        'ytick.major.size': 6,
    })
    
    # Force matplotlib to use Arial if available
    import matplotlib.font_manager as fm
    arial_fonts = [f for f in fm.fontManager.ttflist if f.name == 'Arial']
    if arial_fonts:
        plt.rcParams['font.sans-serif'].insert(0, 'Arial')
    
    rng = np.random.default_rng(42)
    palette = sns.color_palette("bright", 3)
    
    # Prepare data
    df_filtered["Spread_Numeric"] = pd.to_numeric(df_filtered["Spread"], errors='coerce')
    
    # Create figure with exact positioning
    fig = plt.figure(figsize=(width_inches, height_inches))
    ax = fig.add_axes([0.12, 0.12, 0.78, 0.75])  # Precise positioning
    
    # Set tick parameters for this axes
    ax.tick_params(axis='both', direction='in', length=6)
    
    # Plot data
    per_ctry = {}
    all_x, all_y = [], []
    
    for colour, (col, lbl) in zip(palette, [(c, c.split('_')[0]) for c in agency_cols]):
        if col not in df_filtered.columns:
            continue
            
        sub = df_filtered.dropna(subset=[col, "Spread_Numeric"])
        jittered = sub["Spread_Numeric"] + rng.normal(0, jitter_x, len(sub))
        y_vals = sub[col]
        
        ax.scatter(jittered, y_vals, s=140, c=[colour], alpha=.85, label=lbl)
        
        all_x.extend(sub["Spread_Numeric"].tolist())
        all_y.extend(y_vals.tolist())
        
        for ctry, x0, y0 in zip(sub["Country"], sub["Spread_Numeric"], sub[col]):
            d = per_ctry.setdefault(ctry, {"x": x0, "ys": []})
            d["ys"].append(y0)
    
    # Vertical tie lines
    for d in per_ctry.values():
        if len(d["ys"]) > 1:
            ax.plot([d["x"], d["x"]], [min(d["ys"]), max(d["ys"])],
                    color="grey", lw=2, alpha=.55, zorder=2)
    
    # Correlation line
    x_arr, y_arr = np.array(all_x), np.array(all_y)
    m, b = np.polyfit(x_arr, y_arr, 1)
    xs = np.linspace(-500, 500, 300)
    ax.plot(xs, m*xs + b, linestyle="--", lw=2, color="black", zorder=1)
    
    r = np.corrcoef(x_arr, y_arr)[0, 1]
    ax.text(0.95, 0.05, f"r = {r:.2f}", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=20,
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
    
    # Add flags with improved positioning
    # Collect and sort country data
    country_data = []
    for _, row in df_filtered.iterrows():
        ctry = row["Country"]
        code = COUNTRY_TO_CODE.get(ctry, ctry[:2].lower())
        x = row["Spread_Numeric"]
        y = np.nanmax([row.get(c, np.nan) for c in agency_cols])
        
        if not np.isnan(y) and not np.isnan(x):
            country_data.append((x, y, ctry, code))
    
    # Sort by x position then by y position
    country_data.sort(key=lambda item: (item[0], item[1]))
    
    # Track positions to avoid overlaps
    used_positions = []
    min_distance = 0.6  # Minimum vertical distance between flags (smaller for investment grade)
    
    for x, y, ctry, code in country_data:
        lx = x + label_dx
        ly = y
        
        # Check for overlaps and adjust position
        adjusted = False
        for used_x, used_y in used_positions:
            if abs(lx - used_x) < 40:  # If x positions are close
                if abs(ly - used_y) < min_distance:
                    # Try multiple positions to find best spot
                    candidates = [
                        used_y + min_distance,
                        used_y - min_distance,
                        used_y + min_distance * 1.5,
                        used_y - min_distance * 1.5
                    ]
                    
                    # Find position with least overlap
                    best_ly = ly
                    min_overlap = float('inf')
                    
                    for candidate in candidates:
                        if 13.8 <= candidate <= 22.5:  # Keep within plot bounds
                            overlap = sum(1 for ux, uy in used_positions 
                                        if abs(lx - ux) < 40 and abs(candidate - uy) < min_distance)
                            if overlap < min_overlap:
                                min_overlap = overlap
                                best_ly = candidate
                    
                    ly = best_ly
                    adjusted = True
                    break
        
        used_positions.append((lx, ly))
        
        # Add flag or code
        icon = load_icon(code, icon_dir)
        if icon is not None:
            zoom = flag_height / icon.shape[0]
            ab = AnnotationBbox(OffsetImage(icon, zoom=zoom), (lx, ly),
                               frameon=False, box_alignment=(0, 0.5), zorder=4)
            ax.add_artist(ab)
        else:
            ax.text(lx, ly, code.upper(), fontsize=14, fontweight="bold",
                   va="center", zorder=4)
    
    # Shaded background
    ax.axhspan(14, 22, color="#cce6ff", alpha=.25, zorder=0)
    
    # Y-axis labels (investment grade only)
    investment_ticks = list(range(14, 23))
    ax.set_yticks(investment_ticks)
    ax.set_yticklabels([RATING_LABEL[t] for t in investment_ticks])
    
    # Labels and formatting
    ax.set_xlabel("10-Year Bond Spread to US (bp)")
    ax.set_ylabel("Credit Rating")
    
    # Title on figure
    fig.text(0.5, 0.94, "Bond Spreads vs. Sovereign Credit Ratings",
            ha='center', fontsize=40, fontweight='bold')
    
    # Set exact limits
    ax.set_xlim(-500, 500)
    ax.set_ylim(13.8, 22.5)
    
    # Reference line and grid
    ax.axvline(0, color="black", lw=2, alpha=.4)
    ax.grid(alpha=.3)
    ax.legend(loc='upper right', framealpha=0.9)
    
    ax.set_aspect('auto')
    
    # Save with exact dimensions
    fig.savefig(output_file, dpi=300, facecolor='white', edgecolor='none')
    logger.info(f"Saved investment-grade plot: {output_file}")

def download_flag_icons():
    """Download flag icons if not present."""
    logger.info("Checking for flag icons...")
    
    icon_dir = Path("flag_icons")
    icon_dir.mkdir(exist_ok=True)
    
    # Always check for missing flags even if directory exists
    missing_flags = []
    for country, code in COUNTRY_TO_CODE.items():
        code = code.lower()
        png_path = icon_dir / f"{code}.png"
        if not png_path.exists():
            missing_flags.append((country, code))
    
    if not missing_flags:
        logger.info("All flag icons already present")
        return icon_dir
    
    logger.info(f"Need to download {len(missing_flags)} missing flag(s)")
    
    try:
        import requests
        import cairosvg
        
        logger.info("Downloading missing flag icons...")
        version = "latest"
        svg_base_url = f"https://cdn.jsdelivr.net/npm/flag-icons@{version}/flags/4x3/{{code}}.svg"
        
        # Download only missing flags
        downloaded = 0
        for country, code in missing_flags:
            svg_url = svg_base_url.format(code=code)
            png_path = icon_dir / f"{code}.png"
            
            try:
                logger.info(f"Downloading flag for {country} ({code})...")
                resp = requests.get(svg_url, timeout=10)
                resp.raise_for_status()
                
                cairosvg.svg2png(
                    bytestring=resp.content,
                    write_to=str(png_path),
                    output_width=80
                )
                downloaded += 1
            except Exception as e:
                logger.warning(f"Failed to download flag for {country} ({code}): {e}")
        
        logger.info(f"Downloaded {downloaded} of {len(missing_flags)} missing flag icons")
        
    except ImportError:
        logger.warning("requests or cairosvg not installed. Using fallback ISO codes instead of flags.")
        logger.warning("Install with: pip install requests cairosvg")
    
    return icon_dir

def main():
    """Main execution function."""
    # Check for input file
    csv_file = Path("credit_ratings_and_spreads.csv")
    if not csv_file.exists():
        logger.error(f"Input file not found: {csv_file}")
        logger.info("Please run scrape_bond_data.py first to generate the data")
        sys.exit(1)
    
    # Load data
    try:
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded data with {len(df)} countries")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        sys.exit(1)
    
    # Download flag icons if needed
    icon_dir = download_flag_icons()
    
    # Create visualizations
    try:
        create_full_plot(df, icon_dir)
        create_investment_grade_plot(df, icon_dir)
        logger.info("Visualization complete!")
        
    except Exception as e:
        logger.error(f"Failed to create visualizations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()