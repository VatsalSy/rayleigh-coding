# Contour and Filled Contour Plots

Guide for creating contour plots, filled contours, and combining contours with other plot elements for publication-quality scientific visualization.

## Basic Contour Pattern

```python
# Create meshgrid
X, Y = np.meshgrid(x_array, y_array)
Z = f(X, Y)  # Your 2D function or field

# Line contours
contours = ax.contour(
    X, Y, Z,
    levels=10,              # Number of contour levels
    colors='black',         # Line color
    linewidths=2,
    linestyles='solid'
)

# Add contour labels
ax.clabel(contours, inline=True, fontsize=16, fmt='%0.1f')

# Filled contours
contourf = ax.contourf(
    X, Y, Z,
    levels=20,              # More levels for smooth fill
    cmap='viridis'
)

# Colorbar
cbar = plt.colorbar(contourf, ax=ax)
cbar.set_label(r'$\psi(x,y)$', fontsize=30)
```

## Interface Detection (VOF Method)

Extract and plot iso-surfaces (e.g., liquid-gas interface at f = 0.5):

```python
# Phase field or volume fraction
phase = compute_phase_field(X, Y)

# Interface contour at f = 0.5
interface = ax.contour(
    X, Y, phase,
    levels=[0.5],           # Single level
    colors='#00B2FF',       # Interface color
    linewidths=4,
    zorder=5               # Draw on top
)

# Alternative: use LineCollection for more control
from matplotlib.collections import LineCollection

# Extract contour polylines (one path per level; to_polygons splits a path
# into its disconnected pieces). ContourSet.collections was removed in
# Matplotlib 3.10, so use get_paths().
segments = []
for path in interface.get_paths():
    segments.extend(path.to_polygons(closed_only=False))
interface.remove()  # drop the original contour lines if drawing the collection instead

lc = LineCollection(
    segments,
    colors='#00B2FF',
    linewidths=4,
    linestyle='solid',
    zorder=5
)
ax.add_collection(lc)
```

## Contour Levels

### Automatic Levels

```python
# Equally-spaced levels
contours = ax.contour(X, Y, Z, levels=10)  # 10 automatic levels
```

### Manual Levels

```python
# Specific values
levels = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
contours = ax.contour(X, Y, Z, levels=levels)

# Logarithmically-spaced
levels = np.logspace(-2, 1, 10)  # 10^-2 to 10^1
contours = ax.contour(X, Y, Z, levels=levels)

# Custom intervals
levels = np.concatenate([
    np.linspace(0, 1, 11),      # Fine spacing 0-1
    np.linspace(1.5, 5, 8)      # Coarse spacing 1.5-5
])
contours = ax.contour(X, Y, Z, levels=levels)
```

## Combining Contour and Contourf

```python
# Filled contours (smooth background)
contourf = ax.contourf(
    X, Y, Z,
    levels=50,              # Many levels for smooth gradient
    cmap='viridis',
    alpha=0.8
)

# Line contours (specific levels)
contour_lines = ax.contour(
    X, Y, Z,
    levels=[0.5, 1.0, 2.0, 5.0],  # Key isolines
    colors='black',
    linewidths=2,
    linestyles='solid'
)

# Add labels to line contours only
ax.clabel(contour_lines, inline=True, fontsize=16)

# Colorbar for filled contours
cbar = plt.colorbar(contourf, ax=ax)
```

## Contour with Velocity Vectors

Combine contours with quiver plots:

```python
# Compute velocity field from psi[y_index, x_index] (meshgrid default layout).
# np.gradient returns derivatives in axis order (y first) and uses the real
# grid spacing when the coordinate arrays are passed.
dpsi_dy, dpsi_dx = np.gradient(psi, y_array, x_array)
U = dpsi_dy    # u =  ∂ψ/∂y
V = -dpsi_dx   # v = -∂ψ/∂x  (flip both signs for the opposite convention)

# Streamlines (filled contours)
contourf = ax.contourf(X, Y, psi, levels=30, cmap='RdBu_r', alpha=0.6)

# Streamlines (line contours)
ax.contour(X, Y, psi, levels=15, colors='black', linewidths=1, alpha=0.3)

# Velocity vectors (downsampled for clarity)
skip = 10  # Plot every 10th vector
ax.quiver(
    X[::skip, ::skip], Y[::skip, ::skip],
    U[::skip, ::skip], V[::skip, ::skip],
    scale=50, width=0.003, color='darkblue', alpha=0.8
)

ax.set_aspect('equal')
```

## Tricontour for Irregular Grids

For unstructured data or irregular meshes:

```python
# Scattered data points
x = np.random.rand(500) * 4
y = np.random.rand(500) * 4
z = np.sin(x) * np.cos(y)

# Triangulation-based contour
tricontourf = ax.tricontourf(x, y, z, levels=20, cmap='viridis')
tricontour = ax.tricontour(x, y, z, levels=10, colors='black', linewidths=1)

cbar = plt.colorbar(tricontourf, ax=ax)

# Or specify triangulation explicitly
from matplotlib.tri import Triangulation
triang = Triangulation(x, y)
ax.tricontourf(triang, z, levels=20, cmap='viridis')
```

## Logarithmic Contours

For data spanning orders of magnitude:

```python
from matplotlib.colors import LogNorm

# Logarithmic colormap
contourf = ax.contourf(
    X, Y, Z,
    levels=np.logspace(-2, 2, 20),  # 0.01 to 100
    norm=LogNorm(vmin=0.01, vmax=100),
    cmap='viridis'
)

# Line contours at powers of 10
contour = ax.contour(
    X, Y, Z,
    levels=[0.01, 0.1, 1, 10, 100],
    colors='black',
    linewidths=2
)
ax.clabel(contour, fmt='%.2f')
```

## Negative Contours with Dashed Lines

Distinguish positive and negative values:

```python
# Positive contours (solid)
contour_pos = ax.contour(
    X, Y, Z,
    levels=np.linspace(0.1, 2.0, 10),
    colors='red',
    linewidths=2,
    linestyles='solid'
)

# Negative contours (dashed)
contour_neg = ax.contour(
    X, Y, Z,
    levels=np.linspace(-2.0, -0.1, 10),
    colors='blue',
    linewidths=2,
    linestyles='dashed'
)

# Zero contour (thick)
contour_zero = ax.contour(
    X, Y, Z,
    levels=[0],
    colors='black',
    linewidths=4
)
```

## Contour Label Formatting

```python
# Basic labels
contours = ax.contour(X, Y, Z, levels=10, colors='black')
labels = ax.clabel(
    contours,
    inline=True,           # Remove line under label
    fontsize=16,
    fmt='%0.2f'           # Format string
)

# Custom label format
def fmt(x):
    return f'{x:.1e}'  # Scientific notation
labels = ax.clabel(contours, inline=True, fontsize=16, fmt=fmt)

# Manual label positions
manual_locations = [(1, 2), (3, 4), (5, 6)]
labels = ax.clabel(contours, manual=manual_locations, fontsize=16)

# No labels
contours = ax.contour(X, Y, Z, levels=10)  # Don't call clabel
```

## Extend Colorbar Beyond Data Range

```python
contourf = ax.contourf(
    X, Y, Z,
    levels=np.linspace(0, 1, 11),
    cmap='viridis',
    extend='both'          # Options: 'neither', 'both', 'min', 'max'
)

cbar = plt.colorbar(contourf, ax=ax, extend='both')
# Adds triangular extensions to colorbar
```

## Phase Diagram with Contours

Overlay contours on scatter data:

```python
# Background scatter
scatter = ax.scatter(
    x_data, y_data,
    c=z_data,
    s=100,
    cmap='viridis',
    edgecolors='k',
    linewidth=0.5,
    zorder=2
)

# Create interpolated grid from scattered data
from scipy.interpolate import griddata
xi = np.linspace(x_data.min(), x_data.max(), 100)
yi = np.linspace(y_data.min(), y_data.max(), 100)
Xi, Yi = np.meshgrid(xi, yi)
Zi = griddata((x_data, y_data), z_data, (Xi, Yi), method='cubic')

# Overlay contours
contour = ax.contour(
    Xi, Yi, Zi,
    levels=5,
    colors='white',
    linewidths=2,
    linestyles='solid',
    alpha=0.7,
    zorder=3
)

cbar = plt.colorbar(scatter, ax=ax)
```

## Example: Complete Contour Plot

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Configure matplotlib
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# Generate sample data
x = np.linspace(-3, 3, 200)
y = np.linspace(-3, 3, 200)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.1 * (X**2 + Y**2))

# Create figure
fig, ax = plt.subplots(figsize=(12, 10))

# Filled contours
contourf = ax.contourf(
    X, Y, Z,
    levels=30,
    cmap='RdBu_r',
    alpha=0.9
)

# Line contours at specific levels
contour = ax.contour(
    X, Y, Z,
    levels=[-0.4, -0.2, 0.0, 0.2, 0.4],
    colors='black',
    linewidths=2
)

# Add labels
ax.clabel(contour, inline=True, fontsize=18, fmt='%0.2f')

# Colorbar
cbar = plt.colorbar(contourf, ax=ax)
cbar.set_label(r'$\psi(x,y)$', fontsize=30, labelpad=10)
cbar.ax.tick_params(labelsize=24)

# Configure axes
ax.set_xlabel(r'$x/L$', fontsize=40, labelpad=15)
ax.set_ylabel(r'$y/L$', fontsize=40, labelpad=15)
ax.tick_params(axis='both', labelsize=30, width=3, length=10)
for spine in ax.spines.values():
    spine.set_linewidth(3)

ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('contour_plot.pdf', bbox_inches='tight', dpi=300)
plt.close()
```

## Common Issues and Solutions

**Contours appear jagged:**
- Increase grid resolution (more points in X, Y)
- Use more levels for contourf
- Check interpolation method if using scattered data

**Labels overlap:**
- Reduce number of levels
- Use `manual=True` to specify label positions
- Adjust fontsize

**Contours don't align with data:**
- Verify X, Y, Z have same shape
- Check that extent matches data range
- Use `origin='lower'` consistently with imshow

**Missing contours:**
- Check data range (vmin, vmax)
- Verify levels are within data range
- Look for NaN or inf values in data

**Colorbar doesn't match contours:**
- Ensure colorbar uses same mappable
- Check that norm and levels are consistent
- Use `extend` parameter if needed
