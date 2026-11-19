# Code Patterns

Complete code examples for common publication plot types.

## Log-Log Scatter Plot

```python
fig, ax = plt.subplots(figsize=(12, 12))

# Create scatter plot with colormap
scatter = ax.scatter(
    x_data, y_data,
    s=200,                    # Marker size
    c=color_values,           # Values for colormap
    cmap='viridis',           # Colormap
    marker='o',
    edgecolors='w',           # White edge
    linewidth=0.5,
    zorder=3                  # Draw on top
)

# Configure log scales
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([1e-3, 1e0])
ax.set_ylim([1e-2, 1e0])

# Labels with LaTeX
ax.set_xlabel(
    r'$Oh = \frac{\mu}{\sqrt{\rho\gamma R}}$',
    fontsize=plt_settings['LabelFont'],
    labelpad=15
)
ax.set_ylabel(
    r'$Bo = \frac{\rho g R^2}{\gamma}$',
    fontsize=plt_settings['LabelFont'],
    labelpad=15
)

# Colorbar
cbar = plt.colorbar(scatter, label=r'$U_j/\sqrt{\gamma/\rho R}$')
cbar.set_label(
    r'$U_j/\sqrt{\gamma/\rho R}$',
    size=plt_settings['ColorbarFont']
)
cbar.ax.tick_params(labelsize=plt_settings['AxesFont'])

# Apply standard tick styling
ax.tick_params(which='both', direction='out', width=3,
               labelsize=plt_settings['AxesFont'], pad=10)
ax.tick_params(which='major', length=12)
ax.tick_params(which='minor', length=6)
for spine in ax.spines.values():
    spine.set_linewidth(3)

ax.set_box_aspect(1)
plt.tight_layout()
plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
```

## Line Plot with Theoretical Curves

```python
fig, ax = plt.subplots(figsize=(12, 10))

# Experimental data (markers only)
ax.plot(
    x_exp, y_exp,
    linestyle='None',
    marker='o',
    markersize=20,
    markerfacecolor='#1A64B3',  # Blue
    markeredgecolor='k',
    linewidth=2,
    label='Experimental data',
    zorder=2
)

# Simulation data (different marker)
ax.plot(
    x_sim, y_sim,
    linestyle='None',
    marker='D',                  # Diamond marker
    markersize=20,
    markerfacecolor='#FC8D59',   # Orange
    markeredgecolor='k',
    linewidth=2,
    label='Simulation',
    zorder=3
)

# Theoretical curves (lines only)
ax.plot(
    x_theory, y_theory,
    linestyle='--',              # Dashed line
    linewidth=5,
    color='gray',
    alpha=0.7,
    label=r'Theory: $y \sim x^{2/5}$',
    zorder=1
)

# Configure axes
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([1e-3, 0.3])
ax.set_ylim([1e-2, 0.3])
ax.set_xlabel(r'$Oh$', fontsize=50, labelpad=15)
ax.set_ylabel(r'$U_j/U_c$', fontsize=50, labelpad=15)

# Legend
ax.legend(
    loc='best',
    frameon=False,              # No frame
    fontsize=30,
    handlelength=2,
    markerscale=1.2
)

ax.tick_params(which='both', direction='out', width=3,
               labelsize=40, pad=10)
ax.tick_params(which='major', length=12)
ax.tick_params(which='minor', length=6)
for spine in ax.spines.values():
    spine.set_linewidth(3)

ax.set_box_aspect(1)
plt.tight_layout()
plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
```

## Shaded Regions and Fill Between

```python
# Create theoretical boundary curve
x_boundary = np.logspace(-3, 0, 500)
y_boundary = 0.9 * (1 - x_boundary / 0.25)

# Fill region above curve (non-bouncing regime)
ax.fill_between(
    x_boundary, y_boundary, 1.5,
    color='#F3ECEF',           # Light pink
    zorder=1,                  # Draw behind data
    label='Non-bouncing'
)

# Fill region below curve (bouncing regime)
ax.fill_between(
    x_boundary, 1e-2, y_boundary,
    color='#EDF4E4',           # Light green
    zorder=1,
    label='Bouncing'
)

# Vertical fill for different regime
ax.fill_betweenx(
    [1e-2, 1.5], 0.25, 1.5,
    color='#F3ECEF',
    zorder=1
)

# Boundary line
ax.plot(
    x_boundary, y_boundary,
    color='red',
    linestyle='--',
    linewidth=4,
    zorder=2,
    label='Critical boundary'
)
```

## Multi-Panel Figure

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
fig.set_facecolor('white')

# Configure each panel independently
# ... plot data on ax1 ...
# ... plot data on ax2 ...

# Consistent styling across panels
for ax in [ax1, ax2]:
    ax.tick_params(which='both', direction='out', width=3,
                   labelsize=40, pad=10)
    ax.tick_params(which='major', length=12)
    ax.tick_params(which='minor', length=6)
    for spine in ax.spines.values():
        spine.set_linewidth(3)
    ax.set_box_aspect(1)

plt.tight_layout()
plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
```

## Logarithmically-Spaced Markers

For uniform marker distribution on log scales:

```python
# Create 80 logarithmically-spaced indices
log_indices = np.logspace(0, np.log10(len(x)-1), 80, dtype=int)
log_indices = np.unique(log_indices)  # Remove duplicates

# Plot only at these indices
ax.plot(
    x[log_indices], y[log_indices],
    linestyle='None',
    marker='D',
    markersize=15,
    markerfacecolor='#FC8D59',
    markeredgecolor='k',
    linewidth=2
)
```

## Annotation Lines

```python
# Vertical reference line
ax.axvline(
    x=0.2,
    linestyle='-',
    linewidth=5,
    color='black',
    alpha=0.7,
    label=r'$Oh = Oh_c$',
    zorder=3
)

# Horizontal reference line
ax.axhline(
    y=0.22,
    linestyle='--',
    linewidth=5,
    color='gray',
    alpha=0.7,
    label='Theoretical limit'
)
```

## Custom Tick Formatters

```python
from matplotlib.ticker import StrMethodFormatter, LogFormatterSciNotation

# Format with 2 decimal places
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))

# Scientific notation for log scales
ax.xaxis.set_major_formatter(LogFormatterSciNotation())
```
