#!/usr/bin/env python3
"""Annual HHSI from monthly UTCI or from occurrence/intensity/frequency rasters.

HHSI = sum_{month=1}^{12} max(UTCI_month - 26, 0).
If using components, HSI must be the mean positive exceedance above 26 C,
not the mean unadjusted UTCI during qualifying months.
"""
import argparse
from contextlib import ExitStack
from pathlib import Path
import numpy as np
import rasterio

NODATA = -9999.0


def check_grids(srcs):
    ref = srcs[0]
    for src in srcs[1:]:
        if (src.width, src.height, src.crs, src.transform) != (ref.width, ref.height, ref.crs, ref.transform):
            raise ValueError(f'Raster alignment mismatch: {src.name}')


def create_hhsi(files, output, mode, threshold):
    files = [Path(f) for f in files]
    if mode == 'monthly' and len(files) != 12:
        raise ValueError('Monthly mode requires exactly 12 UTCI rasters in calendar order.')
    if mode == 'components' and len(files) != 3:
        raise ValueError('Component mode requires HSA, HSI and HSF rasters.')
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        srcs = [stack.enter_context(rasterio.open(p)) for p in files]
        check_grids(srcs)
        profile = srcs[0].profile.copy()
        profile.update(driver='GTiff', dtype='float32', nodata=NODATA, count=1, compress='deflate')
        with rasterio.open(output, 'w', **profile) as dest:
            for _, window in srcs[0].block_windows(1):
                rasters = [s.read(1, window=window, masked=True) for s in srcs]
                valid = ~np.logical_or.reduce([np.ma.getmaskarray(a) for a in rasters])
                a = [np.asarray(x.filled(0), dtype='float64') for x in rasters]
                if mode == 'monthly':
                    result = np.maximum(np.stack(a, axis=0) - threshold, 0.0).sum(axis=0)
                else:
                    hsa, hsi, hsf = a
                    if np.any(hsi[valid] < 0) or np.any(hsf[valid] < 0):
                        raise ValueError('HSI and HSF must be nonnegative.')
                    if np.any(~np.isclose(hsa[valid], 0) & ~np.isclose(hsa[valid], 1)):
                        raise ValueError('HSA must be a binary occurrence raster.')
                    result = hsa * hsi * hsf
                result = np.where(valid, result, NODATA).astype('float32')
                dest.write(result, 1, window=window)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    a = sub.add_parser('monthly', help='Compute directly from twelve monthly UTCI rasters')
    a.add_argument('--utci', nargs=12, required=True, metavar='TIFF')
    a.add_argument('--threshold', type=float, default=26.)
    b = sub.add_parser('components', help='HHSI=HSA*HSI*HSF, with HSI as mean exceedance')
    for name in ('hsa','hsi','hsf'):
        b.add_argument('--'+name, required=True)
    for s in (a,b): s.add_argument('--out', required=True)
    args = p.parse_args()
    files = args.utci if args.mode == 'monthly' else [args.hsa, args.hsi, args.hsf]
    create_hhsi(files, args.out, args.mode, getattr(args,'threshold',26.))
    print(f'Created {args.out}')


if __name__ == '__main__': main()
