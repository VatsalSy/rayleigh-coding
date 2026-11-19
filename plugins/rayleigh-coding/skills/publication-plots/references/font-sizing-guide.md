# Font Sizing Guide

Standard font sizes for publication-quality figures.

## Default Settings (12-19" figures)

```python
plt_settings = {
    'LabelFont': 40,      # Axis labels (xlabel, ylabel)
    'AxesFont': 30,       # Tick labels
    'TitleFont': 40,      # Plot titles
    'LegendFont': 30,     # Legend entries
    'ColorbarFont': 30,   # Colorbar labels and ticks
}
```

## Size Adjustments

| Figure Size | Scale Factor | Example LabelFont |
|-------------|--------------|-------------------|
| Large (12-19") | 1.0x | 40 |
| Medium (8-12") | 0.85x | 34 |
| Small (6-8") | 0.70-0.75x | 28-30 |
| Multi-panel | 1.10-1.15x | 44-46 |

## Usage Patterns

### Axis Labels
```python
ax.set_xlabel(
    r'$Oh = \frac{\mu}{\sqrt{\rho\gamma R}}$',
    fontsize=plt_settings['LabelFont'],
    labelpad=15  # Distance from axis
)
```

### Tick Labels
```python
ax.tick_params(
    axis='both',
    labelsize=plt_settings['AxesFont'],
    pad=10  # Distance from ticks
)
```

### Legend
```python
ax.legend(
    loc='best',
    frameon=False,
    fontsize=plt_settings['LegendFont'],
    handlelength=2,
    markerscale=1.2
)
```

### Colorbar
```python
cbar = plt.colorbar(mappable, ax=ax)
cbar.set_label(
    r'$\|\boldsymbol{u}\|$',
    fontsize=plt_settings['ColorbarFont'],
    labelpad=5
)
cbar.ax.tick_params(labelsize=plt_settings['AxesFont'])
```

## Notes

- Use `labelpad` to prevent label overlap with tick labels
- Multi-panel figures need larger fonts due to reduced subplot size
- Always verify readability in the final PDF at print scale
