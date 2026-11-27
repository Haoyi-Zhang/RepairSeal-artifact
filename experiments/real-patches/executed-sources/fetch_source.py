#!/usr/bin/env python3
"""Fetch the published patch archive to an external location and verify it."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request

URL='https://zenodo.org/api/records/1012686/files/esemdata-20171016T065923Z-002.zip/content'
BYTES=1088378260
SHA256='65814e170d5887074b04cbb0dee958f078b12e5da49671364a6f7f2a6f7f7c7e'
MD5='8347801dc54761bbbf1a9f8dc156e3f2'
ARTIFACT=Path(__file__).resolve().parents[2]


def verify(path):
    if path.stat().st_size!=BYTES:raise ValueError('fixed archive size mismatch')
    h=hashlib.sha256();m=hashlib.md5()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b);m.update(b)
    if h.hexdigest()!=SHA256 or m.hexdigest()!=MD5:raise ValueError('fixed archive digest mismatch')
    return {'bytes':BYTES,'sha256':SHA256,'md5':MD5,'verified':True,'source_url':URL}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--verify-only',action='store_true');p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
    out=a.output.resolve()
    if out==ARTIFACT or ARTIFACT in out.parents:raise ValueError('keep the full external archive outside the distributable artifact')
    if out.exists():print(json.dumps(verify(out)));return
    if a.verify_only:raise FileNotFoundError(out)
    if not 1<=a.jobs<=8:raise ValueError('jobs must be 1..8')
    out.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='angelix-download-',suffix='.part',dir=out.parent);tmp=Path(name)
    try:
        os.ftruncate(fd,BYTES)
        def transfer(bounds):
            start,end=bounds
            req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'RepairSeal-public-patch-fetch/1'})
            with urllib.request.urlopen(req,timeout=60) as r:
                if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{BYTES}':raise ValueError('server did not honor exact byte range')
                pos=start
                for b in iter(lambda:r.read(1048576),b''):
                    if pos+len(b)>end+1:raise ValueError('range too long')
                    os.pwrite(fd,b,pos);pos+=len(b)
                if pos!=end+1:raise ValueError('range incomplete')
        block=16*1048576
        ranges=[(i,min(i+block,BYTES)-1) for i in range(0,BYTES,block)]
        with ThreadPoolExecutor(max_workers=a.jobs) as pool:
            for f in as_completed([pool.submit(transfer,r) for r in ranges]):f.result()
        os.close(fd);fd=None
        receipt=verify(tmp);os.link(tmp,out)
        print(json.dumps(receipt))
    finally:
        if fd is not None:os.close(fd)
        tmp.unlink(missing_ok=True)


if __name__=='__main__':main()
