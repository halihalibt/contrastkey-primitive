"""Scripted-host tests. No LLM, GenVM, or network consensus is claimed."""
import importlib.util
import itertools
import json
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = ROOT.name.removesuffix('-primitive')
class Return:
    def __init__(self, value): self.calldata = value
class Host:
    outputs = []
    mismatch = False
    calls = 0
    @classmethod
    def prompt(cls, *args, **kwargs):
        cls.calls += 1
        return cls.outputs.pop(0)
    @classmethod
    def consensus(cls, leader, validator):
        value = leader()
        assert validator(Return(value)), 'CONSENSUS_REJECTED'
        return value
public=types.SimpleNamespace(view=lambda f:f, write=lambda f:f)
gl=types.SimpleNamespace(Contract=object, public=public, message=types.SimpleNamespace(sender_address='0xa'),
    nondet=types.SimpleNamespace(exec_prompt=Host.prompt),vm=types.SimpleNamespace(Return=Return,run_nondet_unsafe=Host.consensus))
fake=types.ModuleType('genlayer');fake.gl=gl;fake.TreeMap=dict;fake.u32=int
sys.modules['genlayer']=fake
spec=importlib.util.spec_from_file_location(NAME,ROOT/'contracts'/f'{NAME}.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=json.loads((ROOT/'examples/basic.json').read_text())
ANSWER=(ROOT/'examples/expected.json').read_text()
class Lifecycle(unittest.TestCase):
    def setUp(self):
        Host.calls=0;Host.outputs=[];gl.message.sender_address='0xa'
        self.c=getattr(m,'ContrastKey' if NAME=='contrastkey' else 'QuorumShape')()
        self.c.records={};self.c.counts={}
    def seal(self):return self.c.seal('basic',json.dumps(DATA))
    def test_lifecycle_and_terminal(self):
        key=self.seal();self.assertEqual(self.seal(),key)
        Host.outputs=[ANSWER,ANSWER];out=json.loads(self.c.assess(key,0))
        self.assertEqual(out['state'],'READY');self.assertEqual(Host.calls,2)
        final=json.loads(self.c.certify(key,1));self.assertEqual(final['state'],'CERTIFIED')
        self.assertEqual(json.loads(self.c.get_record(key)),final)
        with self.assertRaisesRegex(Exception,'STALE_REVISION'):self.c.assess(key,0)
        with self.assertRaisesRegex(Exception,'NOT_READY'):self.c.certify(key,2)
    def test_validator_disagreement_is_atomic(self):
        key=self.seal();before=self.c.get_record(key)
        alt=json.loads(ANSWER)
        if NAME=='contrastkey':alt['matrix'][0][0]='N'
        else:alt['table'][0]='Y'
        Host.outputs=[ANSWER,json.dumps(alt)]
        with self.assertRaisesRegex(AssertionError,'CONSENSUS_REJECTED'):self.c.assess(key,0)
        self.assertEqual(self.c.get_record(key),before)
    def test_model_failure_is_atomic(self):
        key=self.seal();before=self.c.get_record(key);Host.outputs=[ANSWER,'not json']
        with self.assertRaises(AssertionError):self.c.assess(key,0)
        self.assertEqual(self.c.get_record(key),before)
    def test_owner_namespace_conflict_and_revisions(self):
        key=self.seal();gl.message.sender_address='0xb'
        with self.assertRaisesRegex(Exception,'OWNER_ONLY'):self.c.assess(key,0)
        other=self.seal();self.assertNotEqual(key,other)
        changed=dict(DATA);changed['scope']='Different scope'
        with self.assertRaisesRegex(Exception,'ID_CONFLICT'):self.c.seal('basic',json.dumps(changed))
    def test_bounded_inputs_and_duplicates(self):
        for raw in ['{}','{"scope":"x","scope":"y"}', 'x'*15000]:
            with self.assertRaises(Exception):self.c.seal('basic',raw)
        with self.assertRaises(Exception):self.c.seal('../x',json.dumps(DATA))
    def test_fail_closed_result_schema(self):
        for raw in ['{}','{"table":[]}','{"matrix":[[true]]}','{"table":["Y"],"table":[]}']:
            with self.assertRaises(Exception):m.parse_result(raw,DATA)
    def test_object_json_response(self):
        key=self.seal();Host.outputs=[json.loads(ANSWER),json.loads(ANSWER)]
        self.assertEqual(json.loads(self.c.assess(key,0))["state"],"READY")
    def test_quota(self):
        for i in range(16):self.c.seal('rec'+str(i),json.dumps(DATA))
        with self.assertRaisesRegex(Exception,'OWNER_LIMIT'):self.c.seal('overflow',json.dumps(DATA))

class Algorithm(unittest.TestCase):
    def test_exhaustive_three_candidates_two_questions(self):
        # Independent recursion enumerates every legal root and all adversarial unknown branches.
        def oracle(matrix, ids):
            if len(ids)==1:return 0
            best=99
            for q in range(2):
                a=tuple(i for i in ids if matrix[i][q]!='N')
                b=tuple(i for i in ids if matrix[i][q]!='Y')
                if len(a)<len(ids) and len(b)<len(ids):
                    best=min(best,1+max(oracle(matrix,a),oracle(matrix,b)))
            return min(best,99)
        for cells in itertools.product('YNU',repeat=6):
            mat=[list(cells[i:i+2]) for i in range(0,6,2)]
            out=m.derive(json.dumps({'matrix':mat}));cost=oracle(mat,(0,1,2))
            self.assertEqual(out['tree'] is None,cost==99)
            if cost<99:
                self.assertEqual(out['tree']['depth'],cost)
                def walk(t,ids):
                    if 'leaf' in t:self.assertEqual(ids,[t['leaf']]);return
                    q=t['question']
                    walk(t['yes'],[i for i in ids if mat[i][q]!='N'])
                    walk(t['no'],[i for i in ids if mat[i][q]!='Y'])
                walk(out['tree'],[0,1,2])
    def test_unknown_is_not_no(self):
        out=m.derive('{"matrix":[["Y"],["U"]]}')
        self.assertEqual(out['status'],'AMBIGUOUS');self.assertEqual(out['indistinguishable_pairs'],[[0,1]])
    def test_non_ready_cannot_certify(self):
        c=m.ContrastKey();c.records={};c.counts={}
        key=c.seal('bad',json.dumps(DATA));a=json.dumps({'matrix':[['U','U']]*3});Host.outputs=[a,a]
        self.assertEqual(json.loads(c.assess(key,0))['state'],'AMBIGUOUS')
        with self.assertRaisesRegex(Exception,'NOT_READY'):c.certify(key,1)

if __name__=='__main__':unittest.main()
