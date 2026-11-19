# Axis Styling

Configure axes with thick spines and prominent ticks for publication-quality figures.

## Standard Configuration

```python
# Major tick parameters
ax.tick_params(
    axis='both',               # Apply to both x and y axes
    which='major',             # Major ticks
    labelsize=plt_settings['AxesFont'],
    width=3,                   # Tick width
    length=12,                 # Tick length
    direction='out',           # Ticks point outward
    pad=10                     # Distance from axis
)

# Minor tick parameters
ax.tick_params(
    which='minor',             # Minor ticks
    width=2,
    length=6,
    direction='out'
)

# Thick axis spines
for spine in ax.spines.values():
    spine.set_linewidth(3)

# Enable minor ticks
ax.minorticks_on()
```

## Quick Reference

| Element | Parameter | Value |
|---------|-----------|-------|
| Major tick width | `width` | 3 |
| Major tick length | `length` | 12 |
| Minor tick width | `width` | 2 |
| Minor tick length | `length` | 6 |
| Spine linewidth | `set_linewidth()` | 3 |
| Tick direction | `direction` | 'out' |
| Label padding | `pad` | 10 |

## Applying to Multiple Axes

For multi-panel figures, apply consistent styling:

```python
for ax in [ax1, ax2, ax3]:
    ax.tick_params(which='both', direction='out', labelsize=40, pad=10)
    ax.tick_params(which='major', width=3, length=12)
    ax.tick_params(which='minor', width=2, length=6)
    for spine in ax.spines.values():
        spine.set_linewidth(3)
    ax.minorticks_on()
```

## Special Cases

### Log Scale Axes
Minor ticks are automatically placed at appropriate positions:
```python
ax.set_xscale('log')
ax.set_yscale('log')
# minorticks_on() works automatically with log scales
```

### Square Aspect Ratio
When one unit on x must equal one unit on y (geometry, phase diagrams in the
same units), use equal data scaling:
```python
ax.set_aspect('equal', adjustable='box')  # equal data scales; the box follows the ranges
```
When only the plotting box should be square and the axes keep different
scales, use `ax.set_box_aspect(1)` instead.

### Hiding Spines
For cleaner plots (rarely needed for publication):
```python
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
```
