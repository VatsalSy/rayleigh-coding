#!/usr/bin/env python3
"""
# Data Processing Module

Process and visualize simulation output data.

## Description

This module provides utilities for loading simulation snapshots,
extracting field data, and generating publication-quality figures.

## Dependencies

- numpy: Array operations
- matplotlib: Visualization
- pathlib: Path handling

## Author

Your Name (your.email@example.org)
Affiliation
Last updated: Jan 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

"""
## Configuration

Set up matplotlib with publication-quality defaults.
"""

plt.rcParams.update({
    'font.size': 12,
    'figure.dpi': 150,
    'axes.linewidth': 1.2
})

"""
## Data Structures
"""


@dataclass(frozen=True)
class DomainConfig:
    """
    Configuration for the computational domain.

    #### Attributes

    - `xmin`, `xmax`: Domain bounds in x-direction.
    - `ymin`, `ymax`: Domain bounds in y-direction.
    - `nx`, `ny`: Grid resolution.
    """
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    nx: int
    ny: int


"""
## Data Loading
"""


def load_snapshot(filepath: Path, config: DomainConfig) -> Tuple[np.ndarray, ...]:
    """
    Load field data from a simulation snapshot.

    Reads binary data from the snapshot file and reshapes it according
    to the domain configuration.

    #### Args

    - `filepath`: Path to the snapshot file.
    - `config`: Domain configuration specifying grid dimensions.

    #### Returns

    - `tuple[np.ndarray, np.ndarray, np.ndarray]`: Coordinate arrays `(X, Y)` and field data `Z`.

    #### Raises

    - `FileNotFoundError`: If the snapshot file doesn't exist.
    - `ValueError`: If data size doesn't match expected grid dimensions.

    #### Example

    ```python
    config = DomainConfig(0, 1, 0, 1, 100, 100)
    X, Y, Z = load_snapshot(Path("snapshot-0.1"), config)
    plt.contourf(X, Y, Z)
    ```
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Snapshot not found: {filepath}")

    data = np.fromfile(filepath, dtype=np.float64)
    expected_size = config.nx * config.ny

    if data.size != expected_size:
        raise ValueError(f"Data size {data.size} != expected {expected_size}")

    Z = data.reshape((config.ny, config.nx))
    x = np.linspace(config.xmin, config.xmax, config.nx)
    y = np.linspace(config.ymin, config.ymax, config.ny)
    X, Y = np.meshgrid(x, y)

    return X, Y, Z


"""
## Visualization
"""


class FieldPlotter:
    """
    Generate publication-quality field visualizations.

    #### Attributes

    - `config`: Domain configuration.
    - `figsize`: Figure dimensions in inches.
    - `cmap`: Colormap for contour plots.

    #### Methods

    - `plot_contour()`: Create filled contour plot.
    - `plot_streamlines()`: Create streamline visualization.
    - `save()`: Export figure to file.
    """

    def __init__(self, config: DomainConfig, figsize: Tuple[float, float] = (8, 6)):
        """Initialize plotter with domain configuration."""
        self.config = config
        self.figsize = figsize
        self.cmap = 'viridis'
        self._fig = None
        self._ax = None

    def plot_contour(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                     levels: int = 20) -> None:
        """
        Create a filled contour plot of field data.

        #### Args

        - `X`, `Y`: Coordinate meshgrids.
        - `Z`: Field values on the grid.
        - `levels`: Number of contour levels.
        """
        self._fig, self._ax = plt.subplots(figsize=self.figsize)
        self._ax.contourf(X, Y, Z, levels=levels, cmap=self.cmap)
        self._ax.set_xlabel('$x$')
        self._ax.set_ylabel('$y$')
        self._ax.set_aspect('equal')

    def save(self, filepath: Path) -> None:
        """Export the current figure to a file."""
        if self._fig is not None:
            self._fig.savefig(filepath, bbox_inches='tight')


if __name__ == "__main__":
    # Example usage
    config = DomainConfig(0, 1, 0, 1, 50, 50)
    print(f"Domain: [{config.xmin}, {config.xmax}] x [{config.ymin}, {config.ymax}]")
