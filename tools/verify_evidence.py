"""Verify recorded evidence, source identity, deterministic proof and commitments offline."""
from pathlib import Path
import hashlib,json,importlib.util
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('test_host',root/'tests/test_contract.py')
host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
m=host.m
p=json.loads((root/'evidence/studionet.json').read_text())
name=root.name.removesuffix('-primitive')
assert p['chainId']==61999 and p['rpc']=='https://studio.genlayer.com/api'
source=(root/'contracts'/f'{name}.py').read_text()
assert p['sourceSha256']==hashlib.sha256(source.encode()).hexdigest()
assert json.loads((root/'evidence/deployed-code.json').read_text())==source
for label in ['deploy','seal','assess','certify']:
    receipt=p['receipts'][label]
    assert receipt['hash']==p['transactions'][label]
    assert receipt['status']=='FINALIZED' and receipt['successful'] and receipt['quorumAgreed']
    raw=json.loads((root/'evidence'/f'{label}-receipt.json').read_text())
    assert raw['hash']==receipt['hash']
r=p['finalReadback']
assert r['id']==p['recordId'] and r['revision']==2 and r['state']=='CERTIFIED'
assert r['input']==json.loads((root/'examples/basic.json').read_text())
assert json.loads(r['accepted'])==json.loads((root/'examples/expected.json').read_text())
assert r['proof']==m.derive(r['accepted'])
assert r['input_hash']==m.digest({'version':m.VERSION,'input':r['input']})
assert r['assessment_hash']==m.digest({'input_hash':r['input_hash'],'accepted':r['accepted'],'proof':r['proof']})
assert r['certificate_hash']==m.digest({'version':m.VERSION,'input_hash':r['input_hash'],'assessment_hash':r['assessment_hash']})
print('PASS: source bytes, four finalized receipt records, readback, deterministic derivation and all commitments')
print('Offline validation of recorded RPC evidence; not a fresh consensus execution.')
