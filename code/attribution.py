#!/usr/bin/env python3
"""Counterfactual attribution using observed, population-only, thermal-only series.

Each scenario CSV has country,year,ES,EC columns from country_metrics.py.
The model assigns half of the slope residual to each counterfactual factor.
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, theilslopes


def read(f):
    d=defaultdict(dict)
    with open(f,encoding='utf-8',newline='') as handle:
        for row in csv.DictReader(handle):
            d[row['country']][int(row['year'])]=row
    return d


def trend(data):
    if len(data)<3:return np.nan,np.nan
    xy=sorted(data)
    x=np.array([z[0] for z in xy],dtype=float)
    y=np.array([z[1] for z in xy],dtype=float)
    if np.all(y==y[0]):return 0.,1.
    return float(theilslopes(y,x)[0]),float(kendalltau(x,y)[1])


def attribute(observed,population,thermal,output):
    o,p,t=read(observed),read(population),read(thermal)
    rows=[]
    for country in sorted(set(o)&set(p)&set(t)):
        for metric in ('ES','EC'):
            ys=sorted(set(o[country])&set(p[country])&set(t[country]))
            values=[]
            for source in (o,p,t):
                values.append([(year,float(source[country][year][metric])) for year in ys
                               if source[country][year][metric] not in ('',None)])
            common=sorted(set(y for y,_ in values[0])&set(y for y,_ in values[1])&set(y for y,_ in values[2]))
            series=[[(y,v) for y,v in vals if y in common] for vals in values]
            if len(common)<3:continue
            (obs,pvalue),(pop,_),(heat,_)=map(trend,series)
            if not np.isfinite(obs) or abs(obs)<1e-15:continue
            residual=obs-pop-heat
            cpop=pop+residual/2
            cheat=heat+residual/2
            denom=abs(pop)+abs(heat)
            ratio=abs(residual)/denom if denom>0 else np.nan
            rows.append([country,metric,len(common),obs,pvalue,pop,heat,residual,
                100*cpop/obs,100*cheat/obs,ratio,int(obs>0 and pvalue<.05)])
    fields=['country','metric','n_years','observed_slope','observed_p','population_only_slope',
            'thermal_only_slope','attribution_residual','population_contribution_pct',
            'thermal_contribution_pct','residual_ratio','significantly_increasing']
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    with open(output,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
    print(f'{len(rows)} metric-country records: {output}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('observed','population','thermal','output'):p.add_argument('--'+arg,required=True)
    a=p.parse_args();attribute(a.observed,a.population,a.thermal,a.output)

if __name__=='__main__':main()
