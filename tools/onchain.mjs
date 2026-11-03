/** Stable Studionet only. Persist every broadcast intent and hash; never auto-retry writes. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createClient,createAccount} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {summarizeReceipt} from './receipt.mjs';
const name=JSON.parse(fs.readFileSync('package.json')).name.replace('-primitive','');
const code=fs.readFileSync(`contracts/${name}.py`,'utf8');
const sha=crypto.createHash('sha256').update(code).digest('hex');
const stringify=x=>JSON.stringify(x,(_,v)=>typeof v==='bigint'?v.toString():v,2)+'\n';
const evidenceDir=process.env.DEPLOY_EVIDENCE_DIR || 'evidence';
fs.mkdirSync(evidenceDir,{recursive:true});
const file=`${evidenceDir}/studionet.json`;
const p=fs.existsSync(file)?JSON.parse(fs.readFileSync(file)):{chainId:61999,rpc:'https://studio.genlayer.com/api',sourceSha256:sha,transactions:{},receipts:{}};
assert.equal(p.sourceSha256,sha,'SOURCE_CHANGED: inspect existing deployment');
const save=()=>fs.writeFileSync(file,stringify(p));
// Optional local disposable test key file; never request or export a user wallet key.
const signerFile=process.env.TEST_SIGNER_FILE;
assert(signerFile,'Set TEST_SIGNER_FILE to a private local disposable test-key file');
if(!fs.existsSync(signerFile))fs.writeFileSync(signerFile,crypto.randomBytes(32).toString('hex'),{mode:0o600});
const account=createAccount('0x'+fs.readFileSync(signerFile,'utf8').trim().replace(/^0x/,''));
if(p.deployer)assert.equal(p.deployer,account.address);else p.deployer=account.address;
const c=createClient({chain:studionet,endpoint:p.rpc,account});
assert.equal(Number(BigInt(await c.request({method:'eth_chainId',params:[]}))),61999);
assert.equal(BigInt(await c.request({method:'eth_gasPrice',params:[]})),0n);
if(!p.transactions.deploy)await c.getContractSchemaForCode(code);
save();
async function step(label,submit){
 if(!p.transactions[label]){
  assert(!p.intent,`Unresolved broadcast intent ${p.intent}; inspect chain before any retry`);
  p.intent=label;save();
  const hash=await submit();p.transactions[label]=hash;delete p.intent;save();console.log(name,label,hash);
 }
 const hash=p.transactions[label];
 for(let i=0;i<180;i++){
  const tx=await c.getTransaction({hash});
  if(tx){
   const summary=summarizeReceipt(tx,hash);p.receipts[label]=summary;save();
   if(['CANCELED','UNDETERMINED','LEADER_TIMEOUT','VALIDATORS_TIMEOUT'].includes(summary.status))throw Error(`${label}: ${summary.status}; inspect ${file} and the stored hash; no automatic retry`);
   if(summary.status==='FINALIZED'){
    fs.writeFileSync(`${evidenceDir}/${label}-receipt.json`,stringify(tx));
    assert(summary.successful,`Finalized execution failed: ${stringify(summary)}`);return tx;
   }
  }
  await new Promise(r=>setTimeout(r,3000));
 }
 throw Error('Tracking timeout; resume same stored hash, no resubmission');
}
const dep=await step('deploy',()=>c.deployContract({code,args:[],leaderOnly:false}));
p.address=dep.to_address??dep.recipient??dep.txDataDecoded?.contractAddress;
assert.match(p.address,/^0x[a-fA-F0-9]{40}$/);save();
const liveCode=await c.getContractCode(p.address);
// SDK code return differs between node versions; retain full raw evidence and compare bytes.
fs.writeFileSync(`${evidenceDir}/deployed-code.json`,stringify(liveCode));
const actual=typeof liveCode==='string'?liveCode:liveCode?.code;
assert(typeof actual==='string','Unexpected code response');
const normalized=actual.startsWith('0x')?Buffer.from(actual.slice(2),'hex').toString('utf8'):actual;
assert.equal(normalized,code,'Deployed source mismatch');
const key=account.address.toLowerCase()+':basic';p.recordId=key;save();
const read=async()=>JSON.parse(await c.readContract({address:p.address,functionName:'get_record',args:[key]}));
await step('seal',()=>c.writeContract({address:p.address,functionName:'seal',args:['basic',fs.readFileSync('examples/basic.json','utf8')],value:0n,leaderOnly:false}));
if(!p.sealedReadback){const sealed=await read();assert.equal(sealed.state,'SEALED');p.sealedReadback=sealed;save();}
await step('assess',()=>c.writeContract({address:p.address,functionName:'assess',args:[key,0],value:0n,leaderOnly:false}));
if(!p.assessedReadback){const assessed=await read();assert.equal(assessed.state,'READY');
assert.deepEqual(JSON.parse(assessed.accepted),JSON.parse(fs.readFileSync('examples/expected.json')));
p.assessedReadback=assessed;save();}
await step('certify',()=>c.writeContract({address:p.address,functionName:'certify',args:[key,1],value:0n,leaderOnly:false}));
const final=await read();assert.equal(final.state,'CERTIFIED');assert.equal(final.revision,2);
p.finalReadback=final;p.verifiedAt=new Date().toISOString();save();
console.log(name,'FINALIZED VERIFIED',p.address,key);
