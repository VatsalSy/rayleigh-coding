# Journal-Specific Figure Styles

Guidelines for creating figures that meet specific journal formatting requirements. Use these styles **only when explicitly requested** by the user (e.g., "JFM style", "PRL format", "APS figure").

## General Principles

- **Ask for clarification** if the target journal/format is unclear
- **Font size minimum**: Never use fonts below 8 pt — warn the user if they request smaller
- **Default style**: When no journal is specified, use the standard publication-plots settings

## JFM (Journal of Fluid Mechanics) Style

**Strict figure width**: 135 mm (5.31 inches)

```python
import matplotlib
import matplotlib.pyplot as plt

# JFM configuration
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Computer Modern Roman']
# Mathtext by default: it needs no external programs. Turn TeX on only after a
# probe render with the same preamble and backend succeeds.
def tex_works(preamble=r'\usepackage{amsmath}'):
    import io
    from matplotlib.figure import Figure  # not registered with pyplot
    try:
        with matplotlib.rc_context({'text.usetex': True, 'text.latex.preamble': preamble}):
            fig = Figure()
            fig.text(0.5, 0.5, r'$\alpha_{\mathrm{test}}$')
            fig.savefig(io.BytesIO(), format='pdf')
        return True
    except Exception:
        return False                          # the probe figure is simply discarded

if tex_works():
    matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
else:
    matplotlib.rcParams['text.usetex'] = False
    matplotlib.rcParams['font.serif'] = ['DejaVu Serif']   # bundled with matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'cm'          # Computer Modern maths
    matplotlib.rcParams['pdf.fonttype'] = 42                 # embed TrueType, as journals ask

# JFM dimensions
JFM_WIDTH_MM = 135
JFM_WIDTH_INCHES = JFM_WIDTH_MM / 25.4  # 5.31 inches

# JFM font sizes (9-10 pt, minimum 8 pt)
jfm_settings = {
    'LabelFont': 10,       # Axis labels
    'AxesFont': 9,         # Tick labels
    'TitleFont': 10,       # Titles (use sparingly)
    'LegendFont': 9,       # Legend entries
    'ColorbarFont': 9,     # Colorbar labels
}

# JFM line and marker settings (scaled for 135mm width)
jfm_line = {
    'linewidth': 1.5,      # Main data lines
    'theory_linewidth': 1.2,  # Theoretical curves
    'spine_width': 1.0,    # Axis spines
    'tick_width': 0.8,     # Tick marks
    'tick_length_major': 5,
    'tick_length_minor': 2.5,
    'markersize': 6,       # Marker diameter
    'markeredgewidth': 0.5,
}

# Create JFM figure (adjust height as needed)
def create_jfm_figure(height_inches=4.0, square=False):
    """Create figure with JFM-compliant width."""
    if square:
        height_inches = JFM_WIDTH_INCHES
    fig, ax = plt.subplots(figsize=(JFM_WIDTH_INCHES, height_inches))
    return fig, ax

# Example usage
fig, ax = create_jfm_figure(height_inches=4.5)

# Apply JFM styling to axes
def style_jfm_axes(ax):
    """Apply JFM styling to an axes object."""
    ax.tick_params(
        axis='both', which='major',
        labelsize=jfm_settings['AxesFont'],
        width=jfm_line['tick_width'],
        length=jfm_line['tick_length_major'],
        direction='out', pad=4
    )
    ax.tick_params(
        which='minor',
        width=jfm_line['tick_width'] * 0.7,
        length=jfm_line['tick_length_minor'],
        direction='out'
    )
    for spine in ax.spines.values():
        spine.set_linewidth(jfm_line['spine_width'])
    ax.minorticks_on()

style_jfm_axes(ax)

# Labels
ax.set_xlabel(r'$x/R$', fontsize=jfm_settings['LabelFont'], labelpad=6)
ax.set_ylabel(r'$y/R$', fontsize=jfm_settings['LabelFont'], labelpad=6)

# Data with JFM styling
ax.plot(x, y, linewidth=jfm_line['linewidth'], color='#1A64B3')
ax.scatter(x, y, s=jfm_line['markersize']**2, edgecolors='k',
           linewidth=jfm_line['markeredgewidth'])

plt.tight_layout()  # fits the content inside the fixed-size canvas
# No bbox_inches='tight': it would crop the page and break the 135 mm width.
with matplotlib.rc_context({'savefig.bbox': None}):   # a style cannot crop it either
    plt.savefig('figure_jfm.pdf', dpi=300)
```

### JFM Quick Reference

| Element | Value |
|---------|-------|
| Figure width | 135 mm (5.31 in) — **strict** |
| Figure height | Flexible (adjust to content) |
| Label font | 10 pt |
| Tick font | 9 pt |
| Legend font | 9 pt |
| Line width | 1.5 pt |
| Spine width | 1.0 pt |
| Marker size | 6 pt |
| Minimum font | 8 pt — **warn if below** |

## APS Style (PRL, PRF, PRE, etc.)

**Figure widths**:
- Single column: 3.375 inches (8.6 cm) — use for most figures
- Double column: 6.75 inches (17.1 cm) — full page width

```python
import matplotlib
import matplotlib.pyplot as plt

# APS configuration
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Computer Modern Roman']
# Mathtext by default: it needs no external programs. Turn TeX on only after a
# probe render with the same preamble and backend succeeds.
def tex_works(preamble=r'\usepackage{amsmath}'):
    import io
    from matplotlib.figure import Figure  # not registered with pyplot
    try:
        with matplotlib.rc_context({'text.usetex': True, 'text.latex.preamble': preamble}):
            fig = Figure()
            fig.text(0.5, 0.5, r'$\alpha_{\mathrm{test}}$')
            fig.savefig(io.BytesIO(), format='pdf')
        return True
    except Exception:
        return False                          # the probe figure is simply discarded

if tex_works():
    matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
else:
    matplotlib.rcParams['text.usetex'] = False
    matplotlib.rcParams['font.serif'] = ['DejaVu Serif']   # bundled with matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'cm'          # Computer Modern maths
    matplotlib.rcParams['pdf.fonttype'] = 42                 # embed TrueType, as journals ask

# APS dimensions
APS_SINGLE_COL = 3.375  # inches (8.6 cm)
APS_DOUBLE_COL = 6.75   # inches (17.1 cm)

# APS font sizes (9-10 pt, minimum 8 pt)
aps_settings = {
    'LabelFont': 10,       # Axis labels
    'AxesFont': 9,         # Tick labels
    'TitleFont': 10,       # Titles (use sparingly)
    'LegendFont': 8,       # Legend (can be slightly smaller)
    'ColorbarFont': 9,     # Colorbar labels
}

# APS line and marker settings
# Single column (compact)
aps_single_line = {
    'linewidth': 1.2,
    'theory_linewidth': 1.0,
    'spine_width': 0.8,
    'tick_width': 0.6,
    'tick_length_major': 4,
    'tick_length_minor': 2,
    'markersize': 5,
    'markeredgewidth': 0.4,
}

# Double column (more space)
aps_double_line = {
    'linewidth': 1.5,
    'theory_linewidth': 1.2,
    'spine_width': 1.0,
    'tick_width': 0.8,
    'tick_length_major': 5,
    'tick_length_minor': 2.5,
    'markersize': 6,
    'markeredgewidth': 0.5,
}

def create_aps_figure(double_column=False, height_inches=None, square=False):
    """Create figure with APS-compliant width.
    
    Args:
        double_column: If True, use full page width (6.75 in)
        height_inches: Custom height (default: width * 0.75)
        square: If True, make figure square
    """
    width = APS_DOUBLE_COL if double_column else APS_SINGLE_COL
    if square:
        height = width
    elif height_inches:
        height = height_inches
    else:
        height = width * 0.75  # Default aspect ratio
    
    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax

def style_aps_axes(ax, double_column=False):
    """Apply APS styling to an axes object."""
    line = aps_double_line if double_column else aps_single_line
    
    ax.tick_params(
        axis='both', which='major',
        labelsize=aps_settings['AxesFont'],
        width=line['tick_width'],
        length=line['tick_length_major'],
        direction='out', pad=3
    )
    ax.tick_params(
        which='minor',
        width=line['tick_width'] * 0.7,
        length=line['tick_length_minor'],
        direction='out'
    )
    for spine in ax.spines.values():
        spine.set_linewidth(line['spine_width'])
    ax.minorticks_on()

# Example: Single column figure
fig, ax = create_aps_figure(double_column=False)
style_aps_axes(ax, double_column=False)

ax.set_xlabel(r'$Oh$', fontsize=aps_settings['LabelFont'], labelpad=4)
ax.set_ylabel(r'$We$', fontsize=aps_settings['LabelFont'], labelpad=4)

# Data
ax.plot(x, y, linewidth=aps_single_line['linewidth'])
ax.scatter(x, y, s=aps_single_line['markersize']**2,
           edgecolors='k', linewidth=aps_single_line['markeredgewidth'])

plt.tight_layout()  # fits the content inside the fixed-size canvas
# No bbox_inches='tight': it would crop the page and change the column width.
with matplotlib.rc_context({'savefig.bbox': None}):   # a style cannot crop it either
    plt.savefig('figure_prl.pdf', dpi=300)
```

### APS Quick Reference

| Element | Single Column | Double Column |
|---------|---------------|---------------|
| Figure width | 3.375 in (8.6 cm) | 6.75 in (17.1 cm) |
| Label font | 10 pt | 10 pt |
| Tick font | 9 pt | 9 pt |
| Legend font | 8–9 pt | 9 pt |
| Line width | 1.2 pt | 1.5 pt |
| Spine width | 0.8 pt | 1.0 pt |
| Marker size | 5 pt | 6 pt |
| Minimum font | 8 pt — **warn if below** |

## Multi-Panel Figures

### JFM Multi-Panel

```python
# Two panels side by side (each ~65mm wide)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(JFM_WIDTH_INCHES, 3.5))
fig.subplots_adjust(wspace=0.35)

for ax in [ax1, ax2]:
    style_jfm_axes(ax)

# Panel labels
ax1.text(-0.15, 1.05, r'$(a)$', transform=ax1.transAxes,
         fontsize=jfm_settings['LabelFont'], fontweight='bold')
ax2.text(-0.15, 1.05, r'$(b)$', transform=ax2.transAxes,
         fontsize=jfm_settings['LabelFont'], fontweight='bold')
```

### APS Multi-Panel

```python
# Two panels in double-column width
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(APS_DOUBLE_COL, 2.8))
fig.subplots_adjust(wspace=0.3)

for ax in [ax1, ax2]:
    style_aps_axes(ax, double_column=True)

# Panel labels
ax1.text(-0.12, 1.05, r'(a)', transform=ax1.transAxes,
         fontsize=aps_settings['LabelFont'])
ax2.text(-0.12, 1.05, r'(b)', transform=ax2.transAxes,
         fontsize=aps_settings['LabelFont'])
```

## Font Size Validation

```python
def validate_font_size(size, element="element"):
    """Warn if font size is below minimum (8 pt)."""
    MIN_FONT = 8
    if size < MIN_FONT:
        print(f"⚠️  WARNING: {element} font size ({size} pt) is below "
              f"minimum ({MIN_FONT} pt). Journal may reject figure.")
        return False
    return True

# Use before setting fonts
validate_font_size(aps_settings['LegendFont'], "Legend")
```

## Choosing Between Styles

| If the user says... | Use this style |
|---------------------|----------------|
| "JFM", "Journal of Fluid Mechanics" | JFM style |
| "PRL", "Phys Rev Lett", "Physical Review Letters" | APS single column |
| "PRF", "Phys Rev Fluids", "Physical Review Fluids" | APS single/double |
| "PRE", "PRX", "APS", "Physical Review" | APS style |
| "full width", "two-column figure" | APS double column |
| Nothing specified | Ask or use default style |

## Comparison with Default Style

| Property | Default | JFM | APS Single | APS Double |
|----------|---------|-----|------------|------------|
| Width | 12 in | 5.31 in | 3.375 in | 6.75 in |
| Label font | 40 pt | 10 pt | 10 pt | 10 pt |
| Tick font | 30 pt | 9 pt | 9 pt | 9 pt |
| Line width | 5 pt | 1.5 pt | 1.2 pt | 1.5 pt |
| Spine width | 3 pt | 1.0 pt | 0.8 pt | 1.0 pt |
| Marker size | 20 pt | 6 pt | 5 pt | 6 pt |

The default style is optimized for presentations and large displays. Journal styles are optimized for print at actual size.
