# Figure Sizing

Standard figure sizes for different publication contexts.

## Common Sizes

```python
# Single panel, square plot (phase diagrams, scatter plots)
fig, ax = plt.subplots(figsize=(12, 12))
ax.set_box_aspect(1)  # Enforce square aspect ratio

# Single panel, rectangular (time series, standard x-y plots)
fig, ax = plt.subplots(figsize=(12, 9))

# Wide figure for video frames or presentations
fig, ax = plt.subplots(figsize=(19.20, 10.80))  # 16:9 aspect ratio

# Multi-panel (2 subplots side by side)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))

# Multi-panel (2 subplots stacked)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
```

## Size Selection Guide

| Use Case | figsize | Aspect |
|----------|---------|--------|
| Phase diagram | (12, 12) | 1:1 |
| Standard x-y | (12, 9) | 4:3 |
| Time series | (14, 8) | 7:4 |
| Presentation | (19.2, 10.8) | 16:9 |
| Side-by-side panels | (24, 10) | 12:5 |
| Stacked panels | (12, 16) | 3:4 |

## Multi-Panel Layouts

### Shared Axes
```python
# Share x-axis across panels (common time axis)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16), sharex=True)

# Only label bottom panel
ax2.set_xlabel(r'$t/\tau$', fontsize=40)
```

### Grid Layout
```python
fig, axes = plt.subplots(2, 3, figsize=(24, 16))

# Access individual panels
axes[0, 0]  # Top-left
axes[1, 2]  # Bottom-right
```

### Custom Spacing
```python
fig, axes = plt.subplots(2, 2, figsize=(20, 20))
plt.subplots_adjust(wspace=0.3, hspace=0.3)  # Width/height spacing
```

## Final Output

Always finalize with:
```python
fig.set_facecolor('white')  # Ensure white background
plt.tight_layout()
plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
plt.close(fig)  # Free memory
```
