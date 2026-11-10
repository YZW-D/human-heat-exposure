#!/usr/bin/env python3
"""Population-weighted heat exposure: HHEI = HHSI * gridded population.

Input rasters must share CRS, transform and dimensions. Valid zero values are
retained as zero; only input NoData cells are masked. Uses float output.
"""
import argparse
from pathlib import Path
import numpy as np
import rasterio

NODATA = -9999.0


def create_hhei(hhsi_path, population_path, output, population_scale=1.0):
    if population_scale <= 0: raise ValueError('population_scale must be positive')
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(hhsi_path) as heat, rasterio.open(population_path) as pop:
        if (heat.width,heat.height,heat.crs,heat.transform) != (pop.width,pop.height,pop.crs,pop.transform):
            raise ValueError('HHSI and population rasters are not aligned.')
        profile=heat.profile.copy()
        profile.update(driver='GTiff',dtype='float32',nodata=NODATA,count=1,compress='deflate')
        with rasterio.open(output,'w',**profile) as dest:
            for _,window in heat.block_windows(1):
                a=heat.read(1,window=window,masked=True)
                b=pop.read(1,window=window,masked=True)
                valid=~(np.ma.getmaskarray(a)|np.ma.getmaskarray(b))
                ah=np.asarray(a.filled(0),dtype='float64')
                bp=np.asarray(b.filled(0),dtype='float64')
                if np.any(bp[valid]<0):raise ValueError('Negative population values')
                result=ah*bp*population_scale
                dest.write(np.where(valid,result,NODATA).astype('float32'),1,window=window)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hhsi',required=True)
    p.add_argument('--population',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--population-scale',type=float,default=1.0,
      help='Multiplier converting the population raster value into persons; default 1')
    a=p.parse_args()
    create_hhei(a.hhsi,a.population,a.out,a.population_scale)
    print(f'Created {a.out}')

if __name__=='__main__':main()
