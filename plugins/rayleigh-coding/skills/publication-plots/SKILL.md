---
name: publication-plots
description: >-
  Use for every figure, plot or video task: matplotlib, exploratory,
  diagnostic, paper, talk, report, log-log, contour, field and multi-panel
  work. Produces consistent, publication-quality figures and videos.
---

# Publication-quality scientific plots

Generate clear scientific figures and videos: publication typography when the
target needs it, quick readable previews for working analysis. Use this skill
for every figure task, including exploratory and diagnostic plots, and combine
it with the relevant domain skill; none replaces it.

## Gotchas

- **Parallel frame workers should use mathtext.** Matplotlib's external TeX
  calls and caches contend and can stall parallel rendering. Set
  `text.usetex=False` and `mathtext.fontset='cm'` in multiprocessing or joblib
  frame pipelines. Keep `usetex=True` for serial publication figures.
- **Journals reject PDFs without embedded fonts.** Check with
  `pdffonts figure.pdf`; Type 3 or non-embedded fonts are a common rejection
  trigger. Saving with `usetex=True` and a working LaTeX installation is the
  safe path.
- **`bbox_inches='tight'` can clip colourbars or annotations** placed outside
  the axes. Add `pad_inches=0.1`.
- **In-figure prose is the least maintainable text in a project.** It cannot
  be corrected without a re-render, is invisible to search, unreadable at
  thumbnail size, and goes stale silently. Put explanation where it can be
  edited: the caption or the analysis note.
- **Source edits are not visual verification.** After any annotation, legend,
  panel-label, arrow or arc change, render the figure and inspect the affected
  panel or crop at output resolution before calling it fixed.
- **Schematic annotations must obey the physics.** Arrows, arcs and labels sit
  in the region they describe: a contact-angle arc ends at the actual
  interface, a distance arrow lies inside the phase being measured, and labels
  do not overlap arrows, interfaces or data.
- **Log axes silently drop non-positive values.** If a log-scale plot looks
  empty or partial, check the data for zeros or negatives.
- **RGB is not CMYK.** Saturated colours can shift in print. For print figures
  check the journal's colour policy.
- **Multi-frame and video output needs a pre-encode QA pass.** Confirm the
  requested physical field (for example concentration rather than volume
  fraction), sort frames numerically rather than lexicographically, and keep
  data geometry, crop, labels and colour limits fixed unless a change is
  intended and disclosed. Inspect the first, middle, last and scientifically
  decisive frames before encoding. A feature tracker that loses its target
  must not silently jump to another object; use a fixed view or disclose gaps.

## Core configuration

Serial publication figures:

```python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Computer Modern Roman']
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
```

Computer Modern ships free with every TeX distribution (TeX Live, MiKTeX,
MacTeX). Without a TeX installation, or for parallel and batch rendering, use
mathtext, which bundles a Computer Modern look-alike:

```python
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['mathtext.fontset'] = 'cm'
```

| Use LaTeX (`usetex=True`) | Use mathtext |
|---|---|
| Publication figures (PDF) | Diagnostic previews |
| Single plots or small batches | Video frames, multiprocessing |
| Typography must match the paper | Any batch of 100+ images |

Save publication figures as PDF
(`plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)`), working previews
as PNG and animations as MP4. A TeX installation is not a prerequisite for
understanding a result.

## Font sizes (12 x 12 inch working canvas)

| Element | Size | Parameter |
|---|---|---|
| Axis labels | 40 | `fontsize=40, labelpad=15` |
| Tick labels | 30 | `labelsize=30, pad=10` |
| Legend | 30 | `fontsize=30` |
| Colourbar | 30 | `fontsize=30` |

The large canvas is scaled down in the document. For figures drawn at final
journal size use the 9 to 10 pt settings in
[journal_styles.md](references/journal_styles.md) and never go below 8 pt.
See [font-sizing-guide.md](references/font-sizing-guide.md).

## Workflow

1. Initialise with the serial or parallel configuration above.
2. Choose the figure size from [figure-sizing.md](references/figure-sizing.md).
3. Plot with the patterns in [code-patterns.md](references/code-patterns.md).
4. Style axes per [axis-styling.md](references/axis-styling.md).
5. Label with LaTeX from [latex-notation.md](references/latex-notation.md).
   Define every symbol and dimensionless group in the caption.
6. Save: PDF for publication, PNG for previews, MP4 for videos.
7. **Keep explanatory text out of the pixels.** A figure or frame carries only
   what identifies the plotted quantities: axis and tick labels, colourbar
   label, legend entries, and a parameter or time stamp where a sequence needs
   one. Interpretation, method notes and provenance go in the caption or the
   analysis note. Add prose to a rendering only on explicit request (for
   example a figure that must travel without its caption). When removing prose
   from an existing figure, move it to the caption rather than deleting it.
8. **Render and inspect.** Open the output; for multi-panel figures crop the
   panels you touched and check overlaps at the real output resolution.
9. **For videos, run the pre-encode QA pass,** encode only when all frames
   pass, then inspect the encoded file (duration, frame count, the same
   checks).

## Provenance

Keep the plotting script separate from the data it reads, and write output to
a path given on the command line rather than into the source repository. Each
figure should be reproducible from a recorded code commit, the pinned solver
or library version, and the input data. A public caption needs only the code
commit and the pinned solver version; it should not carry internal run names,
host names or file-system paths. Give a re-rendered figure a new file name (for
example a `-v2` suffix) instead of overwriting one a document may embed.

## Minimal complete example

```python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Computer Modern Roman']
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

rng = np.random.default_rng(0)
x = 10 ** rng.uniform(-3, 0, 40)
y = 10 ** rng.uniform(0, 3, 40)
values = np.log10(x * y)

fig, ax = plt.subplots(figsize=(12, 12))
ax.scatter(x, y, s=200, c=values, cmap='viridis', edgecolors='k', zorder=3)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(r'$Oh$', fontsize=40, labelpad=15)
ax.set_ylabel(r'$We$', fontsize=40, labelpad=15)
ax.tick_params(which='both', direction='out', width=3, labelsize=30, pad=10)
ax.tick_params(which='major', length=12)
ax.tick_params(which='minor', length=6)
for spine in ax.spines.values():
    spine.set_linewidth(3)
ax.minorticks_on()
ax.set_box_aspect(1)

plt.tight_layout()
plt.savefig('figure.pdf', bbox_inches='tight', dpi=300)
plt.close(fig)
```

## Plot types

| Type | Reference |
|---|---|
| Log-log scatter, line plus theory, shaded regions, multi-panel | [code-patterns.md](references/code-patterns.md) |
| Colormaps and colourbars | [colormaps-colors.md](references/colormaps-colors.md) |
| 2D fields (`imshow`) | [imshow_colormaps.md](references/imshow_colormaps.md) |
| Contour plots | [contour_plots.md](references/contour_plots.md) |
| 3D surfaces | [3d_plots.md](references/3d_plots.md) |
| JFM and APS journal formatting | [journal_styles.md](references/journal_styles.md) |
| Guidelines and troubleshooting | [best-practices.md](references/best-practices.md) |
