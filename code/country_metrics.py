#!/usr/bin/env python3
"""Compute national ES (sum) and EC (Gini) from annual HHEI rasters.

Country boundaries must contain a unique country ID column, and raster values
must be population-weighted HHEI with actual zeroes preserved as valid values.
"""
import argparse
import csv
import re
from pathlib import Path
from collections import defaultdict
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
import fiona


def gini(x, zero_policy='zero'):
    v=np.asarray(x,dtype='float64')
    v=v[np.isfinite(v)]
    if not len(v):return float('nan')
    if np.any(v<0): raise ValueError('Gini requires nonnegative HHEI')
    if not np.any(v):return 0.0 if zero_policy=='zero' else float('nan')
    v.sort()
    n=len(v)
    # Equivalent to sum_{i}(2i-n-1)*v_i / (n*sum(v_i))
    rank=np.arange(1,n+1,dtype='float64')
    return float(np.dot(2*rank-n-1,v)/(n*v.sum(dtype='float64')))


def scan_year(p):
    hits=re.findall(r'(?<!\d)(20\d{2})(?!\d)',Path(p).stem)
    if len(hits)!=1:raise ValueError(f'Filename must contain one year: {p}')
    return int(hits[0])


def national_metrics(boundaries, country_field, rasters, output, scenario, zero_policy):
    groups=defaultdict(list)
    with fiona.open(boundaries) as shp:
        crs=shp.crs_wkt or shp.crs
        if not crs:raise ValueError('Boundary data need a declared CRS')
        for feat in shp:
            props=feat['properties']
            if country_field not in props: raise ValueError(f'Country field {country_field} not found')
            name=str(props[country_field]).strip()
            if name and feat['geometry']:groups[name].append(dict(feat['geometry']))
    if not groups: raise ValueError('No countries read from boundaries')
    rows=[]
    for raster_path in rasters:
        year=scan_year(raster_path)
        with rasterio.open(raster_path) as src:
            transformed={country:[transform_geom(crs,src.crs,g) for g in geometries]
                         for country,geometries in groups.items()}
            for country,geo in sorted(transformed.items()):
                try:arr,_=mask(src,geo,crop=True,filled=False,all_touched=False,indexes=1)
                except ValueError:
                    rows.append([scenario,country,year,'','']);continue
                values=arr.compressed().astype('float64')
                values=values[np.isfinite(values)]
                if len(values)==0: rows.append([scenario,country,year,'','']);continue
                rows.append([scenario,country,year,float(values.sum()),gini(values,zero_policy)])
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    with open(output,'w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['scenario','country','year','ES','EC']);writer.writerows(rows)
    print(f'{len(rows)} country-year rows: {output}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--boundaries',required=True,help='Country-level GeoJSON/GPKG/shapefile')
    p.add_argument('--country-field',required=True)
    p.add_argument('--rasters',nargs='+',required=True,help='Annual HHEI GeoTIFFs with year in filename')
    p.add_argument('--scenario',choices=['observed','population','thermal'],default='observed')
    p.add_argument('--all-zero-ec',choices=['zero','missing'],default='zero')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    national_metrics(a.boundaries,a.country_field,a.rasters,a.output,a.scenario,a.all_zero_ec)

if __name__=='__main__':main()
