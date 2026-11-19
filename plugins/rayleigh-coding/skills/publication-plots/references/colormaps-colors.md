# Colormaps and Color Schemes

Color selection and colorbar configuration for publication figures.

## Recommended Colormaps

### Sequential Data (One Variable)

| Colormap | Use Case |
|----------|----------|
| `'viridis'` | Default, perceptually uniform |
| `'plasma'` | High contrast |
| `'Purples'`, `'Blues'`, `'Greens'` | Single hue |
| `'hot_r'` | Reversed hot (white to black to red) |

### Diverging Data (Positive/Negative)

| Colormap | Use Case |
|----------|----------|
| `'RdBu_r'` | Red-blue reversed |
| `'coolwarm'` | Cool-warm |
| `'seismic'` | Strong contrast at extremes |

## Custom Colors for Markers/Lines

```python
# RGB values (0-255) converted to matplotlib format (0-1)
COLOR = np.array([
    [26, 100, 179],    # Blue
    [252, 141, 89]     # Orange
], dtype=float) / 255.0

# Use in plots
ax.plot(x, y, color=COLOR[0])
ax.scatter(x, y, color=COLOR[1])
```

### Recommended Marker Colors

| Color | Hex | Use |
|-------|-----|-----|
| Blue | `#1A64B3` | Primary data |
| Orange | `#FC8D59` | Secondary data |
| Light pink | `#F3ECEF` | Fill regions |
| Light green | `#EDF4E4` | Fill regions |
| Gray | `gray` | Theory lines |

## Colorbar Configuration

### Standard Colorbar (Vertical, Right Side)

```python
cbar = plt.colorbar(mappable, ax=ax, orientation='vertical')
cbar.set_label(
    r'$\|\boldsymbol{u}\|$',
    fontsize=plt_settings['ColorbarFont'],
    labelpad=5
)
cbar.ax.tick_params(labelsize=plt_settings['AxesFont'])
```

### Manual Positioning for Multiple Colorbars

```python
l, b, w, h = ax.get_position().bounds

# Left colorbar
cbar_ax_left = fig.add_axes([l - 0.04, b, 0.03, h])
cbar_left = plt.colorbar(mappable1, cax=cbar_ax_left)
cbar_left.ax.yaxis.set_ticks_position('left')
cbar_left.ax.yaxis.set_label_position('left')

# Right colorbar
cbar_ax_right = fig.add_axes([l + w + 0.01, b, 0.03, h])
cbar_right = plt.colorbar(mappable2, cax=cbar_ax_right)
```

### Horizontal Colorbar

```python
cbar = plt.colorbar(mappable, ax=ax, orientation='horizontal')
cbar.ax.tick_params(labelsize=plt_settings['AxesFont'])
```

## Colormap Normalization

### Linear (Default)
```python
scatter = ax.scatter(x, y, c=values, cmap='viridis')
```

### Logarithmic
```python
from matplotlib.colors import LogNorm
scatter = ax.scatter(x, y, c=values, cmap='viridis',
                     norm=LogNorm(vmin=1e-3, vmax=1e0))
```

### Symmetric Around Zero
```python
from matplotlib.colors import TwoSlopeNorm
norm = TwoSlopeNorm(vmin=-10, vcenter=0, vmax=10)
scatter = ax.scatter(x, y, c=values, cmap='RdBu_r', norm=norm)
```

## zorder Reference

Control drawing order with `zorder`:

| Element | Recommended zorder |
|---------|-------------------|
| Background fills | 1 |
| Theoretical lines | 2 |
| Data points | 3 |
| Annotation lines | 3-4 |

```python
ax.fill_between(x, y_low, y_high, zorder=1)
ax.plot(x, y, zorder=2)
ax.scatter(x, y, zorder=3)
ax.axvline(x0, zorder=4)
```
