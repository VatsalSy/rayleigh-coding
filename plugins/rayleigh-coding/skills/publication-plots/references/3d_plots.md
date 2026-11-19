# 3D Surface and Scatter Plots

Guide for creating 3D visualizations including surface plots, scatter plots, wireframes, and projections for publication-quality figures.

## Basic 3D Setup

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Configure viewing angle
ax.view_init(elev=30, azim=45)  # Elevation and azimuth angles
```

## 3D Surface Plot

```python
# Generate data
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# Create surface
surf = ax.plot_surface(
    X, Y, Z,
    cmap='viridis',         # Colormap
    linewidth=0,            # No grid lines
    antialiased=True,       # Smooth surface
    alpha=0.9,              # Transparency
    shade=True              # Shading for depth perception
)

# Colorbar
cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
cbar.set_label(r'$z(x,y)$', fontsize=30)

# Labels
ax.set_xlabel(r'$x$', fontsize=30, labelpad=10)
ax.set_ylabel(r'$y$', fontsize=30, labelpad=10)
ax.set_zlabel(r'$z$', fontsize=30, labelpad=10)

# Tick parameters
ax.tick_params(axis='both', labelsize=20)
```

## 3D Scatter Plot

```python
# Data points
x = np.random.randn(500)
y = np.random.randn(500)
z = x**2 + y**2

# Colour by the plotted quantity, so the colourbar reads in its units
scatter = ax.scatter(
    x, y, z,
    c=z,                    # Colour values: f(x, y) = z
    cmap='plasma',
    s=50,                   # Marker size
    alpha=0.8,
    edgecolors='k',
    linewidth=0.3
)

# Colorbar
cbar = fig.colorbar(scatter, ax=ax, shrink=0.5)
cbar.set_label(r'$f(x,y)$', fontsize=30)

ax.set_xlabel(r'$x$', fontsize=30)
ax.set_ylabel(r'$y$', fontsize=30)
ax.set_zlabel(r'$z$', fontsize=30)
```

## Wireframe Plot

For showing structure without obscuring data:

```python
wire = ax.plot_wireframe(
    X, Y, Z,
    color='black',
    linewidth=0.5,
    alpha=0.5,
    rstride=5,              # Row stride (every 5th line)
    cstride=5               # Column stride
)

# Alternative: contour3D for cleaner look
ax.contour3D(X, Y, Z, 50, cmap='viridis', linewidths=1)
```

## Surface with Contour Projection

```python
# Surface
surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)

# Project contours onto bottom plane
zmin = Z.min()
ax.contour(X, Y, Z, levels=10, offset=zmin, cmap='viridis', linewidths=2)

# Set z-limit to show projection
ax.set_zlim(zmin, Z.max())
```

## Parametric Surface

```python
# Parametric coordinates (e.g., sphere)
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
U, V = np.meshgrid(u, v)

# Sphere equations
X = np.cos(U) * np.sin(V)
Y = np.sin(U) * np.sin(V)
Z = np.cos(V)

# Colour by height: map Z (-1 to 1) into the colormap's 0-1 input first
from matplotlib.colors import Normalize

norm = Normalize(vmin=-1, vmax=1)
surf = ax.plot_surface(
    X, Y, Z,
    facecolors=plt.cm.viridis(norm(Z)),
    linewidth=0,
    antialiased=True
)
```

## Multiple Surfaces

```python
# First surface
surf1 = ax.plot_surface(X, Y, Z1, cmap='Blues', alpha=0.7)

# Second surface
surf2 = ax.plot_surface(X, Y, Z2, cmap='Reds', alpha=0.7)

# Legend (requires proxy artists)
from matplotlib.patches import Rectangle
blue_proxy = Rectangle((0, 0), 1, 1, fc='blue', alpha=0.7)
red_proxy = Rectangle((0, 0), 1, 1, fc='red', alpha=0.7)
ax.legend([blue_proxy, red_proxy], ['Surface 1', 'Surface 2'], fontsize=20)
```

## Camera Position and Limits

```python
# Viewing angle
ax.view_init(elev=20, azim=60)  # Elevation 20°, azimuth 60°

# Axis limits
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_zlim(0, 10)

# Aspect ratio
ax.set_box_aspect([1, 1, 0.5])  # X:Y:Z ratio

# Remove background
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False

# Grid transparency
ax.xaxis.pane.set_alpha(0.1)
ax.yaxis.pane.set_alpha(0.1)
ax.zaxis.pane.set_alpha(0.1)
```

## Quiver 3D (Vector Field)

```python
# Vector field data
x = np.arange(-2, 2, 0.5)
y = np.arange(-2, 2, 0.5)
z = np.arange(-2, 2, 0.5)
X, Y, Z = np.meshgrid(x, y, z)

# Vector components
U = -X
V = -Y
W = np.ones_like(Z) * 0.5

# Quiver plot
quiver = ax.quiver(
    X, Y, Z, U, V, W,
    length=0.3,             # Arrow length
    normalize=True,         # Normalize to same length
    arrow_length_ratio=0.3,
    color='black',
    alpha=0.7
)

ax.set_xlabel(r'$x$', fontsize=30)
ax.set_ylabel(r'$y$', fontsize=30)
ax.set_zlabel(r'$z$', fontsize=30)
```

## Filled Contours in 3D

```python
# Multiple z-levels, with one set of levels and one normalisation for all
# slices, so equal colours mean equal values across heights
from matplotlib.colors import Normalize

z_levels = [0, 1, 2, 3, 4]
slices = [np.sin(X) * np.cos(Y) * np.exp(-0.1 * zl) for zl in z_levels]
vmin = min(s.min() for s in slices)
vmax = max(s.max() for s in slices)
levels = np.linspace(vmin, vmax, 11)
norm = Normalize(vmin=vmin, vmax=vmax)

for zl, values in zip(z_levels, slices):
    cs = ax.contourf(
        X, Y, values,
        zdir='z',           # Project onto z
        offset=zl,          # Z position
        levels=levels,
        norm=norm,
        cmap='viridis',
        alpha=0.7
    )
ax.set_zlim(min(z_levels), max(z_levels))  # height axis spans the slice offsets, not field values
fig.colorbar(cs, ax=ax, shrink=0.5)
```

## Line Plot in 3D

```python
# Parametric curve
t = np.linspace(0, 4*np.pi, 200)
x = np.cos(t)
y = np.sin(t)
z = t

ax.plot(
    x, y, z,
    linewidth=3,
    color='blue',
    label='Helix'
)

# Multiple lines
for i in range(5):
    offset = i * 0.5
    ax.plot(x + offset, y, z, linewidth=2)
```

## 2D Contours on 3D Axes

```python
# Pass X, Y, Z in their original order every time: zdir chooses the wall
# and rotates the coordinates itself, as in Matplotlib's projection example.

# XY plane projection (floor)
ax.contour(X, Y, Z, levels=10, offset=Z.min(), cmap='viridis', zdir='z')

# XZ plane projection (back wall)
ax.contour(X, Y, Z, levels=10, offset=Y.max(), cmap='plasma', zdir='y')

# YZ plane projection (side wall)
ax.contour(X, Y, Z, levels=10, offset=X.min(), cmap='coolwarm', zdir='x')

# Fix the limits so each offset lies on the wall that is drawn
ax.set_xlim(X.min(), X.max())
ax.set_ylim(Y.min(), Y.max())
ax.set_zlim(Z.min(), Z.max())
```

## Colormap Normalization in 3D

```python
from matplotlib.colors import Normalize

# Custom normalization
norm = Normalize(vmin=-1, vmax=1)

surf = ax.plot_surface(
    X, Y, Z,
    facecolors=plt.cm.RdBu_r(norm(Z)),
    shade=False
)

# Add scalar mappable for colorbar
import matplotlib.cm as cm
m = cm.ScalarMappable(cmap=plt.cm.RdBu_r, norm=norm)
m.set_array([])
cbar = fig.colorbar(m, ax=ax, shrink=0.5)
```

## Lighting and Shading

```python
from matplotlib.colors import LightSource

# Create light source
ls = LightSource(azdeg=315, altdeg=45)  # Light direction

# Apply shading
rgb = ls.shade(Z, cmap=plt.cm.viridis, vert_exag=0.1)

surf = ax.plot_surface(
    X, Y, Z,
    facecolors=rgb,
    shade=False,            # We're providing our own shading
    antialiased=True
)
```

## Interactive Viewing (Optional)

```python
# For Jupyter notebooks or interactive backends
%matplotlib notebook  # or %matplotlib widget

# Enable rotation/zoom
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot as normal...
surf = ax.plot_surface(X, Y, Z, cmap='viridis')

plt.show()  # Interactive window
```

## Saving with Transparency

```python
plt.savefig(
    'figure_3d.pdf',
    bbox_inches='tight',
    dpi=300,
    transparent=True,       # Transparent background
    facecolor='white'       # Or specific color
)
```

## Example: Complete 3D Surface Plot

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib

# Configure matplotlib
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

# Generate data
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.1*(X**2 + Y**2))

# Create figure
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Surface
surf = ax.plot_surface(
    X, Y, Z,
    cmap='viridis',
    linewidth=0,
    antialiased=True,
    alpha=0.9
)

# Contour projection on bottom
zmin = -0.5
ax.contour(X, Y, Z, levels=10, offset=zmin, cmap='viridis', linewidths=2)

# Colorbar
cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'$f(x,y)$', fontsize=30, labelpad=10)
cbar.ax.tick_params(labelsize=20)

# Labels
ax.set_xlabel(r'$x/L$', fontsize=30, labelpad=15)
ax.set_ylabel(r'$y/L$', fontsize=30, labelpad=15)
ax.set_zlabel(r'$f(x,y)$', fontsize=30, labelpad=15)

# Ticks
ax.tick_params(axis='both', labelsize=20, pad=8)

# View angle
ax.view_init(elev=25, azim=45)

# Limits
ax.set_zlim(zmin, Z.max())

# Clean background
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False

plt.tight_layout()
plt.savefig('surface_3d.pdf', bbox_inches='tight', dpi=300)
plt.close()
```

## Common Issues

**Surface appears faceted:**
- Increase grid resolution (more points)
- Set `antialiased=True`
- Use `shade=True` for smoother appearance

**Colorbar doesn't match surface:**
- Ensure surface uses same cmap and normalization
- Use ScalarMappable if needed for custom colors

**Labels overlap with plot:**
- Adjust `labelpad` parameter
- Change viewing angle with `view_init()`
- Modify `tick_params(pad=...)`

**Slow rendering:**
- Reduce grid resolution
- Use `rcount` and `ccount` in plot_surface
- Simplify with wireframe or contour plots

**Z-ordering issues:**
- Set `zsort='average'` or `zsort='max'` in plot_surface
- Plot in order (back to front)
- Adjust alpha values for transparency
