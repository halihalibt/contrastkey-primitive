/** Read-only reconciliation of superseded transaction evidence. */
import fs from 'node:fs';import path from 'node:path';
import {createClient} from 'genlayer-js';import {studionet} from 'genlayer-js/chains';
import {summarizeReceipt} from './receipt.mjs';
const c=createClient({chain:studionet,endpoint:'https://studio.genlayer.com/api'});
const json=x=>JSON.stringify(x,(_,v)=>typeof v==='bigint'?v.toString():v,2)+'\n';
function find(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(x=>x.isDirectory()?find(path.join(d,x.name)):x.name==='studionet.json'?[path.join(d,x.name)]:[])}
for(const file of find('evidence/deployment-history')){
 const p=JSON.parse(fs.readFileSync(file));
 for(const [label,hash] of Object.entries(p.transactions)){
  const tx=await c.getTransaction({hash});p.receipts[label]=summarizeReceipt(tx,hash);
  fs.writeFileSync(path.join(path.dirname(file),`${label}-receipt.json`),json(tx));
 }
 const addr=p.address??p.receipts.deploy.contractAddress;
 const code=await c.getContractCode(addr);fs.writeFileSync(path.join(path.dirname(file),'source.py'),code);
 if(p.recordId)p.finalRecord=await c.readContract({address:addr,functionName:'get_record',args:[p.recordId]});
 fs.writeFileSync(file,json(p));console.log(file,Object.fromEntries(Object.entries(p.receipts).map(([k,v])=>[k,v.status])));
}
