/**
# Data Extraction Utility

Extract field data from simulation snapshots for post-processing.

## Description

This utility reads simulation snapshots and outputs sampled field data
on a regular grid suitable for visualization tools.

## Usage

```
./utility <snapshot> <xmin> <ymin> <xmax> <ymax> <ny>
```

Where:
- `snapshot`: Path to simulation snapshot file
- `xmin`, `ymin`: Lower domain bounds
- `xmax`, `ymax`: Upper domain bounds
- `ny`: Grid points in y-direction

## Workflow

1. Parse command-line arguments into config struct
2. Restore snapshot via `restore(file=...)`
3. Register derived fields in `field_list`
4. Compute fields and interpolate to grid
5. Output `x y field0 field1 ...` rows

## Adding New Fields

To add a new derived quantity (e.g., `vorticity`):
1. Declare scalar: `scalar omega[];`
2. Register: `field_list = list_add(field_list, omega);`
3. Compute: `compute_vorticity(omega);`

## Author

Your Name (your.email@example.org)
Affiliation
*/

#include "utils.h"

/**
## Data Structures
*/

typedef struct {
  char filename[256];
  double xmin, ymin, xmax, ymax;
  int nx, ny;
} Config;

scalar field1[], field2[];
scalar * field_list = NULL;

/**
## Function Declarations
*/

static int parse_args(int argc, char **argv, Config *cfg);
static void register_fields(void);
static void compute_fields(void);

/**
## Main Function

Entry point for the extraction utility.

### Parameters
- `argc`: Argument count
- `argv`: Argument vector

### Returns
- `0` on success, non-zero on error
*/
int main(int argc, char **argv)
{
  Config cfg;

  /**
  Parse and validate command-line arguments: */
  if (parse_args(argc, argv, &cfg) != 0) {
    fprintf(stderr, "Usage: %s <snapshot> <xmin> <ymin> <xmax> <ymax> <ny>\n",
            argv[0]);
    return 1;
  }

  /**
  Restore simulation state and compute fields: */
  restore(file = cfg.filename);
  register_fields();
  compute_fields();

  /**
  Output sampled data to stdout: */
  // ... sampling and output code ...

  return 0;
}

/**
### parse_args()

Parse command-line arguments into configuration struct.

#### Parameters
- `argc`: Argument count
- `argv`: Argument vector
- `cfg`: Output configuration struct

#### Returns
- `0` on success, `-1` on invalid arguments
*/
static int parse_args(int argc, char **argv, Config *cfg)
{
  if (argc < 7)
    return -1;

  strncpy(cfg->filename, argv[1], sizeof(cfg->filename) - 1);
  cfg->xmin = atof(argv[2]);
  cfg->ymin = atof(argv[3]);
  cfg->xmax = atof(argv[4]);
  cfg->ymax = atof(argv[5]);
  cfg->ny = atoi(argv[6]);

  return 0;
}
