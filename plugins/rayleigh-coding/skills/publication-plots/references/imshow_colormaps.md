# 2D Field Visualization with imshow

Guide for visualizing 2D scalar fields (velocity, pressure, strain rate, temperature, etc.) using `ax.imshow()` with proper interpolation and colormaps.

## Basic imshow Pattern

```python
# Assuming field data on a regular grid
R, Z = np.meshgrid(r_array, z_array)  # 2D coordinate grids
field = np.zeros_like(R)              # Compute your field here

# Create imshow plot
im = ax.imshow(
    field,
    cmap='hot_r',                # Colormap
    interpolation='bilinear',    # Smooth interpolation
    origin='lower',              # Bottom-left origin
    extent=[rmin, rmax, zmin, zmax],  # Physical coordinates
    vmin=0.0,                    # Minimum value for colormap
    vmax=1.0,                    # Maximum value for colormap
    aspect='auto'                # Aspect ratio
)

# Add colorbar
cbar = plt.colorbar(im, ax=ax, label=r'$|\boldsymbol{u}|$')
cbar.ax.tick_params(labelsize=30)
```

## Interpolation Methods

Choose interpolation based on data characteristics:

```python
# Smooth fields (velocity, pressure)
interpolation='bilinear'    # Best for continuous fields
interpolation='bicubic'     # Smoother but slower

# Sharp features (phase fields, discrete data)
interpolation='nearest'     # No smoothing
interpolation='none'        # Fastest, uses default

# High-quality output
interpolation='lanczos'     # Best quality, slowest
```

**Recommendation**: Use `'bilinear'` for most scientific visualizations.

## Split Axisymmetric Fields

An axisymmetric simulation stores fields only for r ≥ 0. A common layout shows
one field on the right (r ≥ 0) and a second field, reflected, on the left, so
two observables share one geometry. Each field is an array indexed
`[z_index, r_index]` with column 0 at r = 0. With `origin='lower'`, column 0 is
drawn at the left edge of the extent, so the left-hand field must be flipped
horizontally (`np.fliplr`) to put r = 0 at the symmetry line. To show a single
field on both sides, use the same array, colormap and limits on each half.

```python
fig, ax = plt.subplots(figsize=(12, 10))

# Positive r side (right)
im_right = ax.imshow(
    velocity_field,
    cmap='Purples',
    interpolation='bilinear',
    origin='lower',
    extent=[0, rmax, zmin, zmax],  # r from 0 to rmax
    vmin=0.0,
    vmax=1.0
)

# Negative r side (left): a second field, reflected about r = 0
im_left = ax.imshow(
    np.fliplr(strain_rate_field),
    cmap='hot_r',
    interpolation='bilinear',
    origin='lower',
    extent=[-rmax, 0, zmin, zmax],  # r from -rmax to 0
    vmin=-4.0,
    vmax=0.0
)

# Add colorbars for both sides
# Left colorbar
l, b, w, h = ax.get_position().bounds
cbar_ax_left = fig.add_axes([l - 0.04, b, 0.03, h])
cbar_left = plt.colorbar(im_left, cax=cbar_ax_left)
cbar_left.set_label(r'$\mathcal{D}:\mathcal{D}$', fontsize=30)
cbar_left.ax.yaxis.set_ticks_position('left')
cbar_left.ax.yaxis.set_label_position('left')

# Right colorbar
cbar_ax_right = fig.add_axes([l + w + 0.01, b, 0.03, h])
cbar_right = plt.colorbar(im_right, cax=cbar_ax_right)
cbar_right.set_label(r'$|\boldsymbol{u}|$', fontsize=30)

# Add symmetry line at r=0
ax.axvline(x=0, color='grey', linestyle='-.', linewidth=2)

ax.set_xlim(-rmax, rmax)
ax.set_ylim(zmin, zmax)
ax.set_xlabel(r'$r/R_0$', fontsize=40)
ax.set_ylabel(r'$z/R_0$', fontsize=40)
ax.set_aspect('equal')
```

## Colormap Normalization

### Linear Normalization (Default)

```python
im = ax.imshow(field, vmin=0.0, vmax=1.0)
```

### Logarithmic Normalization

For data spanning multiple orders of magnitude:

```python
from matplotlib.colors import LogNorm

im = ax.imshow(
    field,
    norm=LogNorm(vmin=1e-3, vmax=1e0),
    cmap='viridis',
)
```

### Symmetric Logarithmic

For data with positive and negative values:

```python
from matplotlib.colors import SymLogNorm

im = ax.imshow(
    field,
    norm=SymLogNorm(linthresh=0.01, vmin=-1.0, vmax=1.0),
    cmap='RdBu_r',
)
```

### Custom Normalization

```python
from matplotlib.colors import TwoSlopeNorm

# Center colormap at specific value (e.g., 0)
norm = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
im = ax.imshow(field, norm=norm, cmap='RdBu_r')
```

## Recommended Colormaps by Field Type

### Velocity/Speed (Positive Values)
```python
cmap='Purples'    # Single hue, clear progression
cmap='viridis'    # Perceptually uniform
cmap='plasma'     # High contrast
```

### Strain Rate/Dissipation (Positive Values)
```python
cmap='hot_r'      # Reversed hot (white→red→black)
cmap='YlOrRd'     # Yellow-orange-red
cmap='Reds'       # Single hue red
```

### Pressure/Scalar (Positive and Negative)
```python
cmap='RdBu_r'     # Red-blue diverging (reversed)
cmap='coolwarm'   # Cool-warm diverging
cmap='seismic'    # Blue-white-red
```

### Phase Field/Volume Fraction (0 to 1)
```python
cmap='gray'       # Grayscale
cmap='binary'     # Black and white
cmap='RdYlBu'     # Red-yellow-blue
```

### Vorticity (Positive and Negative)
```python
cmap='PiYG'       # Pink-yellow-green diverging
cmap='BrBG'       # Brown-blue-green diverging
```

## Transparency and Overlay

Layer multiple fields with alpha transparency:

```python
extent = [rmin, rmax, zmin, zmax]

# Base layer (opaque)
im1 = ax.imshow(velocity_field, cmap='Purples', alpha=1.0, extent=extent)

# Overlay layer (semi-transparent)
im2 = ax.imshow(pressure_field, cmap='RdBu_r', alpha=0.5, extent=extent)

# Add interface contour on top
ax.contour(R, Z, phase_field, levels=[0.5], colors='black', linewidths=3)
```

## Pixel Density and Resolution

Match grid resolution to output resolution:

```python
# For 12-inch figure width at 300 DPI
n_pixels = 12 * 300  # 3600 pixels
nr = n_pixels // 2   # If aspect ratio is 2:1

# Create grid
r = np.linspace(0, rmax, nr)
z = np.linspace(zmin, zmax, nz)
R, Z = np.meshgrid(r, z)
```

## Aspect Ratio Control

```python
# Equal aspect (1:1) - for circular domains
ax.set_aspect('equal')

# Auto aspect - fill available space
ax.set_aspect('auto')

# Custom aspect ratio
ax.set_aspect(2.0)  # one data unit in y is drawn twice as long as one in x

# Use set_box_aspect for overall figure
ax.set_box_aspect(1)  # Square bounding box
```

## Colorbar Formatting

### Tick Formatting

```python
from matplotlib.ticker import StrMethodFormatter

cbar = plt.colorbar(im, ax=ax)
cbar.ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
```

### Scientific Notation

```python
from matplotlib.ticker import LogFormatterSciNotation

cbar = plt.colorbar(im, ax=ax)
cbar.ax.yaxis.set_major_formatter(LogFormatterSciNotation())
```

### Custom Ticks

```python
cbar = plt.colorbar(im, ax=ax, ticks=[0, 0.25, 0.5, 0.75, 1.0])
cbar.ax.set_yticklabels(['0', '1/4', '1/2', '3/4', '1'])
```

## Example: Complete 2D Field Plot

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Configure matplotlib
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# Generate sample data
nr, nz = 256, 256
r = np.linspace(0, 4, nr)
z = np.linspace(0, 4, nz)
R, Z = np.meshgrid(r, z)
velocity = np.sqrt((R - 2)**2 + (Z - 2)**2)
strain = -np.exp(-((R - 2)**2 + (Z - 2)**2))

# Create figure
fig, ax = plt.subplots(figsize=(12, 10))

# Plot velocity field
im = ax.imshow(
    velocity,
    cmap='Purples',
    interpolation='bilinear',
    origin='lower',
    extent=[0, 4, 0, 4],
    vmin=0.0,
    vmax=3.0
)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label(r'$|\boldsymbol{u}|/U_0$', fontsize=30, labelpad=10)
cbar.ax.tick_params(labelsize=24)

# Configure axes
ax.set_xlabel(r'$r/R_0$', fontsize=40, labelpad=15)
ax.set_ylabel(r'$z/R_0$', fontsize=40, labelpad=15)
ax.tick_params(axis='both', labelsize=30, width=3, length=10)
for spine in ax.spines.values():
    spine.set_linewidth(3)

ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('velocity_field.pdf', bbox_inches='tight', dpi=300)
plt.close()
```

## Performance Tips

1. **Use appropriate grid resolution**: Match to output DPI × figure size
2. **Rasterization for large grids**: `im.set_rasterized(True)` reduces PDF size
3. **Downsample before plotting**: Use `scipy.ndimage.zoom` or `skimage.transform.resize`
4. **Cache computations**: Don't recompute fields in plotting loops
5. **Close figures**: Always `plt.close(fig)` after saving to free memory
