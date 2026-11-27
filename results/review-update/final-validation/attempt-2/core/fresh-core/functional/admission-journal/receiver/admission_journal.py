"""Durable owned repair-approval workflow with receiver-owned request identity.

This is an application consumer, not a source-mapping or deployment proof.
Full checking and certificate-free recalculation have identical information.
An accepted packet may refute a repair; only semantic ACCEPT permits approval.
Receipts also bind the trusted receiver implementation. Historical receipts
remain audit records after an upgrade, but a new receiver must check again.

The source files and loaded modules are trusted and fixed for a process's
lifetime. The database is owned by the receiver; its hashes are consistency
checks, not authentication against an attacker who can rewrite the database.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import proof_dag_checker as core

LIMIT=32*1024*1024

def canonical(value):return core.canonical_bytes(value)
def identity(value):return hashlib.sha256(canonical(value)).hexdigest()

# Capture the implementation when the trusted modules are loaded. Paths do not
# contribute, so moving an unchanged artifact does not invalidate its receipts.
# Source edits (including conservative nonsemantic edits) do invalidate them.
_RECEIVER_MANIFEST = {
    'scheme': 'repairseal-owned-receiver-v2',
    'python': {'implementation': sys.implementation.name,
               'version': list(sys.version_info)},
    'modules': {
        'proof_dag_checker': hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),
        'admission_journal': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    },
}
_RECEIVER_IDENTITY = identity(_RECEIVER_MANIFEST)

def receiver_identity():
    """Identity of this process's fixed trusted checker and journal implementation."""
    return _RECEIVER_IDENTITY

def request_identity(request):
    # Mapping order is semantic: it binds source parameters, coordinates and
    # witness rows. Sorted JSON alone cannot distinguish a reordered domain.
    return identity(dict(input_order=list(request['inputs']), request=request))

def request_bytes(request):
    # Preserve the receiver's declared coordinate order across SQLite reloads.
    return json.dumps(request,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
def read_json(path):
    with Path(path).open('rb') as f:raw=f.read(LIMIT+1)
    if len(raw)>LIMIT:raise ValueError('bounded input exceeded')
    return core.load_json_strict(raw.decode('utf-8'))

class AdmissionJournal:
    def __init__(self,path,work_limit=2_000_000):
        if type(work_limit) is not int or not 0<=work_limit<=2_000_000:raise ValueError('work limit')
        self.work_limit=work_limit
        self.receiver_identity=receiver_identity()
        self.db=sqlite3.connect(str(path),timeout=5,isolation_level=None)
        try:
            self.db.execute('PRAGMA synchronous=FULL')
            self.db.execute('PRAGMA journal_mode=DELETE')
            self.db.execute('BEGIN IMMEDIATE')
            self.db.execute('''CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY, revision INTEGER NOT NULL, identity TEXT NOT NULL, body TEXT NOT NULL)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS receipts (
                token TEXT PRIMARY KEY, request_id TEXT NOT NULL, revision INTEGER NOT NULL,
                request_identity TEXT NOT NULL, mode TEXT NOT NULL, packet_identity TEXT NOT NULL,
                decision TEXT NOT NULL, result TEXT NOT NULL, receiver_identity TEXT)''')
            columns={row[1] for row in self.db.execute('PRAGMA table_info(receipts)')}
            if 'receiver_identity' not in columns:
                # A legacy receipt supplies no evidence of its checker version.
                # NULL deliberately cannot satisfy the current approval query.
                self.db.execute('ALTER TABLE receipts ADD COLUMN receiver_identity TEXT')
            self.db.commit()
        except BaseException:
            if self.db.in_transaction:self.db.rollback()
            self.db.close()
            raise

    def register(self,request,expected_identity=None):
        core.validate_request(request)
        body=request_bytes(request)
        if len(body)>LIMIT:raise ValueError('request byte bound')
        digest=request_identity(request);key=request['id']
        try:
            self.db.execute('BEGIN IMMEDIATE')
            old=self.db.execute('SELECT revision,identity FROM requests WHERE id=?',(key,)).fetchone()
            if old is None:
                if expected_identity is not None:raise ValueError('expected request absent')
                revision=1
            else:
                if expected_identity!=old[1]:raise ValueError('request replacement requires current identity')
                revision=old[0]+1
            self.db.execute('INSERT INTO requests VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,identity=excluded.identity,body=excluded.body',
                (key,revision,digest,body.decode('utf-8')))
            self.db.commit()
            return dict(request_id=key,revision=revision,request_identity=digest)
        except BaseException:
            if self.db.in_transaction:self.db.rollback()
            raise

    def decide(self,key,token,mode,packet=None):
        if type(token) is not str or not 1<=len(token)<=128:raise ValueError('receipt token')
        if mode not in ('proof','direct'):raise ValueError('decision mode')
        if mode=='direct' and packet is not None:raise ValueError('direct mode accepts no packet')
        packet_id=identity(packet)
        try:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT revision,identity,body FROM requests WHERE id=?',(key,)).fetchone()
            if row is None:raise ValueError('unregistered authoritative request')
            revision,digest,body=row
            request=core.load_json_strict(body)
            if request_identity(request)!=digest:raise ValueError('authoritative request identity changed')
            previous=self.db.execute('SELECT request_id,revision,request_identity,mode,packet_identity,receiver_identity,result FROM receipts WHERE token=?',(token,)).fetchone()
            if previous:
                if previous[:5]!=(key,revision,digest,mode,packet_id):raise ValueError('receipt token belongs to another request or payload')
                if previous[5]!=self.receiver_identity:
                    raise ValueError('receipt belongs to another receiver implementation; recheck with a new token')
                self.db.commit();return dict(json.loads(previous[6]),replayed_receipt=True)
            remaining=self.work_limit
            def tick(category,n):
                nonlocal remaining
                remaining-=n
                if remaining<0:raise RuntimeError('consumer work budget exhausted')
            result=core.check(request,packet,count=tick) if mode=='proof' else core.evaluate_topological(request,count=tick)
            if result['status'] not in ('ACCEPT','REFUTED'):raise ValueError('no semantic decision')
            receipt=dict(request_id=key,revision=revision,request_identity=digest,mode=mode,
                receiver_identity=self.receiver_identity,
                packet_identity=packet_id,semantic_status=result['status'],approved=result['status']=='ACCEPT',
                witness=result['witness'],checked_cells=result['checked_cells'])
            self.db.execute('''INSERT INTO receipts
                (token,request_id,revision,request_identity,mode,packet_identity,decision,result,receiver_identity)
                VALUES(?,?,?,?,?,?,?,?,?)''',
                (token,key,revision,digest,mode,packet_id,result['status'],canonical(receipt).decode('utf-8'),self.receiver_identity))
            self.db.commit();return dict(receipt,replayed_receipt=False)
        except BaseException:
            if self.db.in_transaction:self.db.rollback()
            raise

    def approved(self,key,expected_identity):
        if type(expected_identity) is not str or len(expected_identity)!=64:raise ValueError('explicit request identity required')
        row=self.db.execute('''SELECT q.body,q.identity,EXISTS(
            SELECT 1 FROM receipts AS r
            WHERE r.request_id=q.id AND r.revision=q.revision AND r.request_identity=q.identity
              AND r.receiver_identity=? AND r.decision='ACCEPT')
            FROM requests AS q WHERE q.id=? AND q.identity=?''',
            (self.receiver_identity,key,expected_identity)).fetchone()
        if row is None:return False
        request=core.load_json_strict(row[0])
        if request_identity(request)!=row[1]:raise ValueError('authoritative request identity changed')
        return bool(row[2])

    def close(self):self.db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('database',type=Path)
    sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('register');r.add_argument('request',type=Path);r.add_argument('--expected-identity')
    d=sub.add_parser('decide');d.add_argument('request_id');d.add_argument('token');d.add_argument('--mode',choices=['proof','direct'],required=True);d.add_argument('--packet',type=Path)
    q=sub.add_parser('approved');q.add_argument('request_id');q.add_argument('request_identity')
    a=p.parse_args();owner=AdmissionJournal(a.database)
    try:
        if a.action=='register':result=owner.register(read_json(a.request),a.expected_identity)
        elif a.action=='approved':result=dict(approved=owner.approved(a.request_id,a.request_identity))
        else:result=owner.decide(a.request_id,a.token,a.mode,read_json(a.packet) if a.packet else None)
        print(json.dumps(result,sort_keys=True))
    finally:owner.close()
if __name__=='__main__':main()
