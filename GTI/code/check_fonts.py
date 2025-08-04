#!/usr/bin/env python3
"""Check available fonts and current matplotlib font settings"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Get list of available fonts
available_fonts = sorted([f.name for f in fm.fontManager.ttflist])

# Check if Arial is available
arial_available = any('Arial' in font for font in available_fonts)

print("=== Font Check ===")
print(f"Arial available: {arial_available}")

# Show Arial variants if available
arial_fonts = [f for f in available_fonts if 'Arial' in f]
if arial_fonts:
    print("\nArial variants found:")
    for font in arial_fonts:
        print(f"  - {font}")
else:
    print("\nNo Arial fonts found in system")

# Show current matplotlib settings
print("\n=== Current Matplotlib Font Settings ===")
print(f"font.family: {plt.rcParams['font.family']}")
print(f"font.sans-serif: {plt.rcParams['font.sans-serif']}")

# Show what font matplotlib will actually use
fig, ax = plt.subplots(figsize=(6, 2))
text = ax.text(0.5, 0.5, "Test Text in Current Font", 
               transform=ax.transAxes, ha='center', va='center', fontsize=20)
actual_font = text.get_fontname()
print(f"\nActual font being used: {actual_font}")
plt.close(fig)

# Show alternative fonts that look similar to Arial
print("\n=== Alternative Sans-Serif Fonts Available ===")
sans_fonts = [f for f in available_fonts if any(name in f.lower() for name in ['helvetica', 'sans', 'arial', 'nimbus'])]
for font in sans_fonts[:10]:  # Show first 10
    print(f"  - {font}")