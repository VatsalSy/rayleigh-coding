# Best Practices and Troubleshooting

Guidelines for publication-quality figures.

## Best Practices

1. **Always save as PDF** for vector graphics:
   ```python
   plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
   ```

2. **Use `bbox_inches='tight'`** to eliminate excess whitespace

3. **Set `fig.set_facecolor('white')`** for multi-panel figures to ensure white background

4. **Close figures** after saving to free memory:
   ```python
   plt.close(fig)
   ```

5. **Use `zorder`** to control drawing order:
   - Background fills: `zorder=1`
   - Lines and curves: `zorder=2`
   - Data points: `zorder=3`

6. **Consistent marker sizes**: Use `s=200` or `markersize=20` for visibility

7. **Edge colors on markers**: `edgecolors='k'` or `markeredgecolor='k'` with `linewidth=2` for contrast

8. **Legend placement**: `loc='best'` lets matplotlib optimize, or use specific positions like `loc='upper right'`

9. **Aspect ratio**: Use `ax.set_box_aspect(1)` for square plots when axes should be equal

10. **Label padding**: Use `labelpad=15` to prevent label overlap with tick labels

11. **Keep explanatory prose out of the pixels.** Axis labels, tick labels,
    colourbar labels, legend entries, and a parameter or time stamp identify
    what is plotted. Sentences that explain, interpret or caption belong in
    the embedding document, not in the figure or video frame, unless the author
    asks for a standalone rendering.

## Troubleshooting

### LaTeX Compilation Errors

**Problem**: Figure won't render, LaTeX error messages

**Solutions**:
- Check for unescaped special characters (`$`, `%`, `&`, `_`, `#`)
- Ensure matching braces in LaTeX expressions
- Verify `amsmath` package is in preamble
- Use raw strings: `r'$\alpha$'` not `'$\alpha$'`

### Font Size Too Small in Final PDF

**Problem**: Labels/ticks appear tiny in exported figure

**Solutions**:
- Increase `figsize` while maintaining font sizes
- Or increase all font sizes proportionally
- Check DPI setting (use `dpi=300`)

### Ticks Not Visible

**Problem**: Tick marks don't appear or are too faint

**Solutions**:
- Increase tick parameters: `tick_params(width=3, length=12)`
- Check axis limits aren't hiding ticks
- Verify `minorticks_on()` is called

### Colorbar Label Overlap

**Problem**: Colorbar label overlaps with tick labels

**Solutions**:
- Increase `labelpad` in `cbar.set_label(..., labelpad=10)`
- Adjust colorbar width in manual positioning
- Use `orientation='horizontal'` if space permits

### Markers Hidden Behind Lines

**Problem**: Data points invisible behind theoretical curves

**Solutions**:
- Set data points to higher `zorder` (3+)
- Set theoretical lines to lower `zorder` (1-2)
- Reduce line `alpha` for transparency

### Log Scale Issues

**Problem**: Negative or zero values cause errors on log scale

**Solutions**:
- Filter data: `data[data > 0]`
- Use `ax.set_xlim(x_min, x_max)` with `0 < x_min < x_max` chosen from the data (for example the smallest positive value) to exclude zero
- Consider `symlog` scale for data crossing zero

### Memory Issues with Many Figures

**Problem**: Script crashes when generating many figures

**Solutions**:
- Always call `plt.close(fig)` after saving
- Use `plt.close('all')` periodically
- Process figures in batches

### Parallel Rendering with Multiprocessing

**Problem**: Using `usetex=True` with `multiprocessing.Pool` causes serialization or lock errors

**Why**: LaTeX rendering spawns external subprocesses (`latex` + `dvipng`) for each unique string. Workers contend for cache locks, and unique strings (like timestamps) can't be cached.

**Solutions**:
- Use mathtext instead of usetex for parallel work:
  ```python
  matplotlib.rcParams['text.usetex'] = False   # also undoes an earlier usetex=True
  matplotlib.rcParams['font.family'] = 'serif'
  matplotlib.rcParams['mathtext.fontset'] = 'cm'
  ```
- Reserve `usetex=True` for single publication plots (PDF output)
- Mathtext supports most LaTeX math notation and is fully parallel-safe

### Inconsistent Appearance Across Systems

**Problem**: Figure looks different on different computers

**Solutions**:
- Explicitly set all font parameters
- Use `matplotlib.rcParams` at script start
- Export as PDF (vector) not PNG (raster)
- Verify LaTeX installation is consistent

## Pre-Submission Checklist

- [ ] All text readable at print size
- [ ] Consistent font sizes across all figures
- [ ] Color scheme accessible (colorblind-friendly if possible)
- [ ] Axes labels have units or are dimensionless
- [ ] Legend entries match data
- [ ] Figure saved as PDF (vector format)
- [ ] White background (no transparency issues)
- [ ] Aspect ratio appropriate for data
