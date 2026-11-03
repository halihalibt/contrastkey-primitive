"""Official SDK lifecycle check; model mocked, no network consensus."""
from gltest.direct import VMContext, deploy_contract, create_address
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
name=root.name.removesuffix('-primitive')
vm=VMContext();vm.sender=create_address(name)
with vm.activate():
    c=deploy_contract(root/'contracts'/f'{name}.py',vm,sdk_version='v0.3.0-rc7')
    vm.check_pickling=True
    vm.mock_llm('.*',(root/'examples/expected.json').read_text())
    key=c.seal('sdk-test',(root/'examples/basic.json').read_text())
    result=json.loads(c.assess(key,0));assert result['state']=='READY'
    final=json.loads(c.certify(key,1));assert final['state']=='CERTIFIED'
    assert json.loads(c.get_record(key))==final
    print('PASS official SDK storage/calldata/serialization; mocked model, no real consensus')
