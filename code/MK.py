#!/usr/bin/env python3
"""Theil-Sen slopes and two-sided Kendall/Mann-Kendall trend p-values.

Input has columns country, 2001, 2002, ..., 2021 (e.g. Figure2/3 CSV).
"""
import argparse
import csv
from pathlib import Path
import numpy as np
from scipy.stats import kendalltau, theilslopes


def trend(year_values):
    a=sorted((float(year),float(value)) for year,value in year_values if value not in (None,''))
    if len(a)<3:return {'slope':'','kendall_tau':'','p_two_sided':'','significant_increase':''}
    x=np.array([v[0] for v in a]);y=np.array([v[1] for v in a])
    if np.all(y==y[0]): return {'slope':0.,'kendall_tau':0.,'p_two_sided':1.,'significant_increase':0}
    sl=float(theilslopes(y,x)[0]); tau,p=kendalltau(x,y)
    return {'slope':sl,'kendall_tau':float(tau),'p_two_sided':float(p),
            'significant_increase':int(sl>0 and p<0.05)}


def run(input_csv,output_csv):
    with open(input_csv,encoding='utf-8',newline='') as f:rr=list(csv.DictReader(f))
    yy=[str(i) for i in range(2001,2022)]
    if not rr or not all(y in rr[0] for y in yy):raise ValueError('Expected 2001–2021 columns')
    result=[]
    for row in rr:
        z={'country':row['country']}
        z.update(trend([(year,row[year]) for year in yy]))
        result.append(z)
    Path(output_csv).parent.mkdir(parents=True,exist_ok=True)
    with open(output_csv,'w',encoding='utf-8',newline='') as f:
        ww=csv.DictWriter(f,fieldnames=list(result[0]));ww.writeheader();ww.writerows(result)
    print(f'{len(result)} country records: {output_csv}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.input,a.output)

if __name__=='__main__':main()
