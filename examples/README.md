# Examples

This directory contains sample gEQDSK files and screenshots demonstrating the Flux Surface Mesh Generator application.

## Sample Files

### 1. sample_simple.geqdsk

**Description**: Simplified circular plasma equilibrium for testing and learning.

**Characteristics**:
- Grid size: 65 × 65
- Major radius: 1.0-2.0 m
- Vertical extent: -1.0 to +1.0 m
- Configuration: Limited (circular cross-section)
- O-point: Approximately (1.5, 0.0)
- No X-points

**Use case**:
- First-time users learning the interface
- Quick testing of basic functionality
- Validation of circular flux surface extraction

**Suggested psi_N values**: `0.2, 0.4, 0.6, 0.8, 0.95`

### 2. sample_single_null.geqdsk

**Description**: Single-null divertor configuration (realistic tokamak equilibrium).

**Characteristics**:
- Grid size: 129 × 129
- Major radius: 0.88-2.25 m
- Vertical extent: -1.6 to +1.6 m
- Configuration: Single-null diverted
- O-point: Approximately (1.5, 0.0)
- X-point: Lower X-point at approximately (1.2, -1.0)

**Use case**:
- Realistic tokamak mesh generation
- Testing X-point detection
- Divertor region meshing

**Suggested psi_N values**: `0.1, 0.3, 0.5, 0.7, 0.85, 0.95`

### 3. sample_double_null.geqdsk (if available)

**Description**: Double-null divertor configuration.

**Characteristics**:
- Grid size: 129 × 129
- Configuration: Double-null diverted
- Two X-points (upper and lower)

**Use case**:
- Advanced equilibrium testing
- Multiple X-point detection validation
- Symmetric divertor configurations

## Quick Start

### Using Sample Files

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Load a sample**:
   - File → Open gEQDSK
   - Navigate to `examples/` directory
   - Select `sample_simple.geqdsk`

3. **Add flux surfaces**:
   - Enter in left panel: `0.2, 0.4, 0.6, 0.8, 0.95`
   - Click "Add"

4. **Preview mesh**:
   - View → Toggle Meshing Preview
   - Check statistics in status bar

5. **Export**:
   - Click "Export Mesh..." button in Meshing tab
   - Choose output directory
   - Select desired format (.msh, .vtk, .smb, or .dmg)

## Expected Results

### sample_simple.geqdsk

After loading and adding suggested psi_N values:

- **Flux surfaces**: 5 concentric circular contours
- **O-point marker**: Center of plasma (red circle with "O" label)
- **X-point markers**: None (limited configuration)
- **Mesh statistics** (with n_rays=360):
  - Nodes: ~1800
  - Triangles: ~3600
  - Min angle: ~28-35°

### sample_single_null.geqdsk

After loading and adding suggested psi_N values:

- **Flux surfaces**: 6 D-shaped contours
- **O-point marker**: Near geometric center (upper region)
- **X-point marker**: Lower X-point (red X with label)
- **LCFS**: Separatrix passing through X-point
- **Mesh statistics** (with n_rays=360):
  - Nodes: ~2200
  - Triangles: ~4400
  - Min angle: ~24-32°

## Screenshots

### Workflow Examples

1. **Initial load**
   - `screenshot_01_load.png`: Application after loading sample_simple.geqdsk
   - Shows limiter boundary, default view

2. **Flux surface display**
   - `screenshot_02_flux_surfaces.png`: Multiple flux surfaces added
   - Demonstrates color coding and contour alignment

3. **Mesh preview**
   - `screenshot_03_mesh_preview.png`: Meshing preview enabled
   - Shows triangle edges and structure

4. **Single-null configuration**
   - `screenshot_04_single_null.png`: sample_single_null.geqdsk loaded
   - X-point marker visible, D-shaped plasma

5. **Batch processing dialog**
   - `screenshot_05_batch_dialog.png`: Batch Run dialog
   - Multiple files selected for processing

6. **Paraview visualization**
   - `screenshot_06_paraview.png`: Exported .vtk file in Paraview
   - Demonstrates mesh quality visualization

*Note: Screenshots to be added when application is run with GUI display*

## Generating Your Own Examples

### From Experimental Data

If you have access to EFIT reconstructions:

1. **Locate gEQDSK file**: Usually named like `g123456.00100` (shot 123456, time 100ms)

2. **Copy to examples**:
   ```bash
   cp /path/to/geqdsk/g123456.00100 examples/my_equilibrium.geqdsk
   ```

3. **Add documentation**:
   - Shot number
   - Device name
   - Time slice
   - Plasma parameters (Ip, Bt, shape)

### Synthetic Equilibria

For testing specific scenarios:

```python
# Generate synthetic circular equilibrium
from mesh_gui_project.data.geqdsk_parser import parse_geqdsk
import numpy as np

# Create synthetic psi field
NR, NZ = 65, 65
R = np.linspace(1.0, 2.0, NR)
Z = np.linspace(-1.0, 1.0, NZ)
R_grid, Z_grid = np.meshgrid(R, Z)

# Simple circular flux surfaces: psi ~ (R-R0)^2 + (Z-Z0)^2
R0, Z0 = 1.5, 0.0
psi = (R_grid - R0)**2 + (Z_grid - Z0)**2

# Write gEQDSK format (see geqdsk_parser.py for format details)
# ...
```

## Common Workflows

### Workflow 1: Quick Mesh Generation

**Goal**: Generate mesh from equilibrium in under 2 minutes.

1. Load `sample_simple.geqdsk`
2. Add psi_N: `0.2, 0.4, 0.6, 0.8, 0.95`
3. Enable meshing preview
4. Save mesh as .msh and .vtk
5. Done!

### Workflow 2: High-Quality Edge-Focused Mesh

**Goal**: Create refined mesh for edge physics simulation.

1. Load `sample_single_null.geqdsk`
2. Add psi_N with edge focus: `0.5, 0.7, 0.8, 0.85, 0.9, 0.93, 0.95, 0.97`
3. Increase n_rays to 540
4. Verify mesh quality (min angle > 25°)
5. Export with metadata (psi_N at nodes)
6. Validate in Paraview (see [PARAVIEW_GUIDE.md](../docs/PARAVIEW_GUIDE.md))

### Workflow 3: Batch Processing Multiple Time Slices

**Goal**: Process full discharge evolution (50 time slices).

1. Organize gEQDSK files in directory:
   ```
   discharge_12345/
     t00100.geqdsk
     t00200.geqdsk
     ...
     t05000.geqdsk
   ```

2. Launch batch mode:
   - File → Batch Run
   - Add all 50 files
   - Enter shared psi_N: `0.2, 0.4, 0.6, 0.8, 0.95`
   - Select output directory

3. Run and wait for completion (~5-10 minutes for 50 files)

4. Review summary and check for failures

5. Process outputs with custom script if needed

## Testing with Examples

### Unit Test Integration

The sample files are used in automated tests:

```python
# tests/test_integration.py
def test_full_workflow_simple_equilibrium():
    """Integration test using sample_simple.geqdsk"""
    eq = parse_geqdsk("examples/sample_simple.geqdsk")
    # ... full workflow test
```

### Manual Validation Checklist

Use this checklist when validating new features:

- [ ] Load sample_simple.geqdsk without errors
- [ ] O-point detected within 1 cm of expected location
- [ ] 5 flux surfaces extract successfully
- [ ] Mesh generates without inverted elements
- [ ] Export to .msh reads back correctly with meshio
- [ ] Export to .vtk opens in Paraview
- [ ] Batch mode processes both sample files
- [ ] No memory leaks after 10 load/unload cycles

## Troubleshooting

### "Failed to parse sample file"

**Cause**: File corruption or incorrect path.

**Solution**:
- Verify file exists: `ls -l examples/sample_simple.geqdsk`
- Check file size (should be ~50-200 KB)
- Re-download or regenerate from repository

### "X-point not detected in sample_single_null.geqdsk"

**Cause**: Grid resolution too coarse or X-point outside search region.

**Solution**:
- Verify file is correct single-null configuration
- Check console output for search region used
- Try increasing search region in critical_points.py

### Poor mesh quality in examples

**Cause**: Default n_rays too low for complex geometry.

**Solution**:
- Increase n_rays from 360 to 540 or 720
- Add more intermediate psi_N values
- Avoid psi_N > 0.97 near separatrix

## Contributing Examples

To contribute new example files:

1. **Ensure data is shareable**: Public domain or appropriately licensed

2. **Document thoroughly**:
   - Source (simulation code, device, or synthetic)
   - Physical parameters
   - Expected results

3. **Test workflow**:
   - Verify file loads correctly
   - Confirm reasonable mesh generation
   - Check no unusual errors

4. **Submit PR** with:
   - gEQDSK file in examples/
   - Update this README
   - Add screenshots if available

## File Format Reference

### gEQDSK Format Quick Reference

Minimal gEQDSK structure:

```
  EQDSK_ID_STRING                     3 03/15/2012    #   65  65
  0.5000E+00  0.5000E+00  1.0000E+00 -0.5000E+00  1.5000E+00
  1.5000E+00  0.0000E+00  0.5000E+00  1.0000E+00  1.5000E+00
  ...
  (psi grid data, 5 values per line)
  ...
  (boundary points if NBDRY > 0)
  (limiter points if NLIM > 0)
```

Key fields:
- Line 1: ID, shot, time, NR, NZ
- Line 2: RDIM, ZDIM, RCENTR, RLEFT, ZMID
- Line 3: RMAG, ZMAG, PSIAXIS, PSIBDRY, BCENTR
- Subsequent lines: Grid data and polylines

See [TECHSPEC.md](../docs/TECHSPEC.md) Section 3 for complete format specification.

## Additional Resources

- [USER_GUIDE.md](../docs/USER_GUIDE.md): Complete user documentation
- [DEVELOPER_GUIDE.md](../docs/DEVELOPER_GUIDE.md): API and architecture reference
- [PARAVIEW_GUIDE.md](../docs/PARAVIEW_GUIDE.md): Visualization validation steps
- [TECHSPEC.md](../docs/TECHSPEC.md): Technical specification

## Support

For issues with example files or questions about usage:
- Review documentation in [docs/](../docs/)
- Check [USER_GUIDE.md](../docs/USER_GUIDE.md) troubleshooting section
- Report bugs with example file name and error message

---

**Last Updated**: 2025-11-21
**Example Files Version**: 1.0
