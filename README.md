# Human heat exposure and spatial inequality

**Manuscript:** *Widespread increases in human heat exposure and spatial inequality within countries*  

This repository provides Python scripts and figure-related data for analyzing the scale and within-country spatial concentration of population-weighted heat exposure.

## Data

The `data/` directory contains four Excel workbooks:

| File | Content |
| --- | --- |
| `Figure1_GlobalAnnual.xlsx` | Global annual human heat exposure series (Figure 1). |
| `Figure2_ExposureScale.xlsx` | Countries with increasing exposure-scale (ES), selected national time series, and population/thermal-stress attribution (Figure 2). |
| `Figure3_ExposureConcentration.xlsx` | Countries with increasing exposure-concentration (EC), selected national time series, and attribution (Figure 3). |
| `Figure4_Global South and North.xlsx` | Joint ES–EC classifications, Global South/North summaries, and attribution values used in boxplots (Figure 4). |

Each workbook contains labelled worksheets for its corresponding results.

## Code

The `code/` directory includes:

| Script | Purpose |
| --- | --- |
| `HHSI.py` | Calculate the human heat stress index (HHSI). |
| `HHEI.py` | Calculate the human heat exposure index (HHEI) from HHSI and gridded population. |
| `country_metrics.py` | Summarize national ES and calculate EC using the Gini coefficient. |
| `MK.py` | Estimate Theil–Sen trends and Kendall significance. |
| `attribution.py` | Estimate population and thermal-stress contributions using counterfactual time series. |

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

## Measures

- **HHEI:** Population-weighted heat stress at the grid-cell level.
- **ES:** National sum of grid-cell HHEI.
- **EC:** Gini coefficient of the within-country distribution of grid-cell HHEI.

The analyses use monthly GloUTCI-M thermal-stress data and annual LandScan population data, as described in the manuscript.
