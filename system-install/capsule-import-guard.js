const CAPSULE_IMPORT_GUARD_VERSION='20260714-03';

function validateImportData(data){
 if(!data||data.format!=='PhantomCapsule'||!data.stores||typeof data.stores!=='object'||Array.isArray(data.stores))throw new Error('格式不符');
 const normalized={};
 for(const s of CAPSULE_STORES){
  const arr=data.stores[s];
  if(arr===undefined){normalized[s]=[];continue}
  if(!Array.isArray(arr))throw new Error(`${s} 資料格式不符`);
  const ids=new Set();
  normalized[s]=arr.map(x=>{
   if(!x||typeof x!=='object'||Array.isArray(x)||typeof x.id!=='string'||!x.id.trim())throw new Error(`${s} 物件缺少有效 id`);
   if(ids.has(x.id))throw new Error(`${s} 備份內含重複 id：${x.id}`);
   ids.add(x.id);
   return x;
  });
 }
 return normalized;
}

async function prepareImportPlan(data){
 const normalized=validateImportData(data);
 if(!db)await openDB();
 const plan={};
 for(const s of CAPSULE_STORES){
  const existing=new Map((await getAll(s)).map(x=>[String(x.id),JSON.stringify(x)]));
  plan[s]=[];
  for(const x of normalized[s]){
   const id=String(x.id),serialized=JSON.stringify(x);
   if(!existing.has(id)){plan[s].push(x);continue}
   if(existing.get(id)===serialized)continue;
   throw new Error(`${s} 物件 id 衝突，未寫入：${id}`);
  }
 }
 return plan;
}

function commitImportPlan(plan){
 return new Promise((resolve,reject)=>{
  const transaction=db.transaction(CAPSULE_STORES,'readwrite');
  transaction.oncomplete=()=>resolve();
  transaction.onabort=()=>reject(transaction.error||new Error('匯入交易已中止'));
  transaction.onerror=()=>reject(transaction.error||new Error('匯入交易失敗'));
  for(const s of CAPSULE_STORES)for(const x of plan[s])transaction.objectStore(s).put(x);
 });
}

async function importCapsuleFile(file,atLock){
 if(!file)return;
 try{
  const data=JSON.parse(await file.text());
  const plan=await prepareImportPlan(data);
  await commitImportPlan(plan);
  if(atLock){alert('已匯入。請用原本名字與密語解鎖。');location.reload()}
  else{await refreshAll();qs('transferStatus').innerHTML='<div class="status ok">匯入完成；既有同 ID 資產未被覆蓋。</div>'}
 }catch(e){alert('匯入失敗，未寫入任何衝突或無效資料：'+(e.message||e))}
}
