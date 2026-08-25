/**
# Field Operations Header

Common field manipulation utilities for simulation post-processing.

## Description

Provides data structures and function declarations for extracting,
transforming, and outputting simulation field data.

## Dependencies

Requires the following Basilisk headers:
- `utils.h`: Basic utility functions
- `output.h`: Output routines

## Author

Your Name (your.email@example.org)
*/

#ifndef FIELD_OPS_H
#define FIELD_OPS_H

#include "utils.h"

/**
## Data Structures
*/

/**
### FieldConfig

Configuration for field extraction and sampling.

#### Members
- `filename`: Path to input snapshot
- `bounds`: Domain boundaries [xmin, ymin, xmax, ymax]
- `resolution`: Grid points [nx, ny]
*/
typedef struct {
  char filename[256];
  double bounds[4];
  int resolution[2];
} FieldConfig;

/**
### FieldData

Container for sampled field values on a regular grid.

#### Members
- `x`, `y`: Coordinate arrays (size nx, ny)
- `values`: Field values (size nx * ny)
- `nx`, `ny`: Grid dimensions
*/
typedef struct {
  double *x;
  double *y;
  double *values;
  int nx, ny;
} FieldData;

/**
## Function Declarations
*/

/**
### field_config_init()

Initialize a field configuration with default values.

#### Parameters
- `cfg`: Configuration struct to initialize

#### Returns
- `0` on success
*/
int field_config_init(FieldConfig *cfg);

/**
### field_data_alloc()

Allocate memory for field data arrays.

#### Parameters
- `data`: Field data struct
- `nx`, `ny`: Grid dimensions

#### Returns
- `0` on success, `-1` on allocation failure
*/
int field_data_alloc(FieldData *data, int nx, int ny);

/**
### field_data_free()

Release memory allocated for field data.

#### Parameters
- `data`: Field data struct to free
*/
void field_data_free(FieldData *data);

/**
### field_sample()

Sample a scalar field onto a regular grid.

#### Parameters
- `s`: Source scalar field
- `cfg`: Extraction configuration
- `data`: Output field data (must be pre-allocated)

#### Returns
- `0` on success, `-1` on error
*/
int field_sample(scalar s, const FieldConfig *cfg, FieldData *data);

#endif /* FIELD_OPS_H */
