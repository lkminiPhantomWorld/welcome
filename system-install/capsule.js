const DB_NAME='phantom_capsule_db', DB_VER=1;
const CAPSULE_STORES=['chat','voice','events','files','secrets','meta'];
const ALLOWED_MEETING_PROTOCOLS=new Set(['https:','http:','facetime:','facetime-audio:','zoommtg:','tel:']);
let db, currentOwner='', recorder=null, chunks=[];
let cachedExportFile=null;
let voiceObjectURLs=[];

function qs(id){return document.getElementById(id)}
function nowISO(){return new Date().toISOString()}
function uid(){return crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random().toString(16).slice(2)}
function esc(s=''){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}
function b64(buf){
 const bytes=new Uint8Array(buf),chunkSize=0x8000,parts=[];
 for(let i=0;i<bytes.length;i+=chunkSize)parts.push(String.fromCharCode(...bytes.subarray(i,i+chunkSize)));
 return btoa(parts.join(''));
}
function unb64(s){const x=atob(s),a=new Uint8Array(x.length);for(let i=0;i<x.length;i++)a[i]=x.charCodeAt(i);return a.buffer}
function safeMeetingURL(raw){
 const text=String(raw||'').trim();if(!text)return null;
 try{const u=new URL(text,location.href);return ALLOWED_MEETING_PROTOCOLS.has(u.protocol)?u.href:null}catch(e){return null}
}
function icsEscape(s=''){return String(s).replace(/\\/g,'\\\\').replace(/\r?\n/g,'\\n').replace(/,/g,'\\,').replace(/;/g,'\\;')}

function openDB(){
 return new Promise((resolve,reject)=>{
  const r=indexedDB.open(DB_NAME,DB_VER);
  r.onupgradeneeded=()=>{
   const d=r.result;
   CAPSULE_STORES.forEach(n=>{if(!d.objectStoreNames.contains(n))d.createObjectStore(n,{keyPath:'id'})});
  };
  r.onsuccess=()=>{db=r.result;resolve(db)};r.onerror=()=>reject(r.error);
 });
}
function tx(store,mode='readonly'){return db.transaction(store,mode).objectStore(store)}
function put(store,obj){return new Promise((res,rej)=>{const r=tx(store,'readwrite').put(obj);r.onsuccess=()=>res(obj);r.onerror=()=>rej(r.error)})}
function getAll(store){return new Promise((res,rej)=>{const r=tx(store).getAll();r.onsuccess=()=>res(r.result||[]);r.onerror=()=>rej(r.error)})}
function del(store,id){return new Promise((res,rej)=>{const r=tx(store,'readwrite').delete(id);r.onsuccess=()=>res();r.onerror=()=>rej(r.error)})}
function clearStore(store){return new Promise((res,rej)=>{const r=tx(store,'readwrite').clear();r.onsuccess=()=>res();r.onerror=()=>rej(r.error)})}

async function deriveKey(pass,salt){
 const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pass),'PBKDF2',false,['deriveKey']);
 return crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:180000,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
}
async function encryptText(text){
 const salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
 const key=await deriveKey(qs('passphrase').value||sessionStorage.getItem('capsulePass')||'',salt);
 const ct=await crypto.subtle.encrypt({name:'AES-GCM',iv},key,new TextEncoder().encode(text));
 return {salt:b64(salt),iv:b64(iv),ct:b64(ct)};
}
async function decryptText(obj){
 const pass=sessionStorage.getItem('capsulePass')||'';
 const key=await deriveKey(pass,new Uint8Array(unb64(obj.salt)));
 const pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:new Uint8Array(unb64(obj.iv))},key,unb64(obj.ct));
 return new TextDecoder().decode(pt);
}

async function unlockCapsule(){
 const owner=qs('ownerName').value.trim(),pass=qs('passphrase').value;
 if(!owner||pass.length<4){qs('lockStatus').innerHTML='<div class="status warning">請輸入名字，密語至少 4 個字元。</div>';return}
 try{
  await openDB();
  const meta=(await getAll('meta')).find(x=>x.id==='identity');
  const passHash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(pass+'|'+owner));
  const hash=b64(passHash);
  if(meta&&(meta.owner!==owner||meta.passHash!==hash)){qs('lockStatus').innerHTML='<div class="status dangerbox">名字或密語不正確。</div>';return}
  if(!meta)await put('meta',{id:'identity',owner,passHash:hash,createdAt:nowISO(),meetingLink:''});
  sessionStorage.setItem('capsulePass',pass);currentOwner=owner;
  qs('ownerTitle').textContent=owner;qs('lockView').classList.add('hidden');qs('appView').classList.remove('hidden');qs('tabs').classList.remove('hidden');
  await refreshAll();
 }catch(e){qs('lockStatus').innerHTML='<div class="status dangerbox">膠囊無法開啟：'+esc(e.message||e)+'</div>'}
}
function showImportAtLock(){qs('lockImport').classList.remove('hidden');qs('lockImport').click()}
function lockNow(){sessionStorage.removeItem('capsulePass');location.reload()}
function openModule(id){document.querySelectorAll('section.module').forEach(x=>x.classList.remove('active'));const target=qs(id);if(target)target.classList.add('active');window.scrollTo({top:0,behavior:'smooth'})}
async function refreshAll(){await Promise.all([renderChats(),renderVoices(),renderEvents(),renderFiles(),renderSecrets(),renderSummary(),loadMeetingLink()])}

async function saveChat(){
 const text=qs('chatText').value.trim();if(!text)return;
 await put('chat',{id:uid(),text,createdAt:nowISO()});qs('chatText').value='';await renderChats();await renderSummary();
}
function clearChatInput(){qs('chatText').value=''}
async function renderChats(){
 if(!db)return;const arr=(await getAll('chat')).sort((a,b)=>b.createdAt.localeCompare(a.createdAt));
 qs('chatList').innerHTML=arr.length?arr.map(x=>`<div class="item"><div class="meta">${new Date(x.createdAt).toLocaleString()}</div><div>${esc(x.text).replace(/\n/g,'<br>')}</div><button class="danger" style="margin-top:8px" onclick="removeItem('chat','${x.id}')">刪除</button></div>`).join(''):'<p class="small">還沒有聊天紀錄。</p>';
}

async function startRecording(){
 try{
  const stream=await navigator.mediaDevices.getUserMedia({audio:true});
  recorder=new MediaRecorder(stream);chunks=[];
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=async()=>{
   try{
    const blob=new Blob(chunks,{type:recorder.mimeType||'audio/webm'}),ab=await blob.arrayBuffer();
    await put('voice',{id:uid(),title:qs('voiceTitle').value.trim()||'未命名語音',type:blob.type,data:b64(ab),createdAt:nowISO()});
    qs('voiceTitle').value='';qs('voiceStatus').textContent='已保存。';await renderVoices();await renderSummary();
   }catch(e){qs('voiceStatus').textContent='保存語音失敗：'+(e.message||e)}finally{stream.getTracks().forEach(t=>t.stop());qs('recordBtn').classList.remove('hidden');qs('stopBtn').classList.add('hidden')}
  };
  recorder.start();qs('recordBtn').classList.add('hidden');qs('stopBtn').classList.remove('hidden');qs('voiceStatus').textContent='錄音中……';
 }catch(e){qs('voiceStatus').textContent='無法啟用麥克風：'+(e.message||e)}
}
function stopRecording(){if(recorder&&recorder.state!=='inactive')recorder.stop()}
async function renderVoices(){
 if(!db)return;voiceObjectURLs.forEach(URL.revokeObjectURL);voiceObjectURLs=[];
 const arr=(await getAll('voice')).sort((a,b)=>b.createdAt.localeCompare(a.createdAt));
 qs('voiceList').innerHTML=arr.length?arr.map(x=>{const url=URL.createObjectURL(new Blob([unb64(x.data)],{type:x.type}));voiceObjectURLs.push(url);return `<div class="item"><div class="meta">${new Date(x.createdAt).toLocaleString()}</div><strong>${esc(x.title)}</strong><audio controls src="${url}"></audio><button class="danger" onclick="removeItem('voice','${x.id}')">刪除</button></div>`}).join(''):'<p class="small">還沒有語音。</p>';
}

async function saveEvent(){
 const title=qs('eventTitle').value.trim(),start=qs('eventStart').value,end=qs('eventEnd').value;
 if(!title||!start){alert('請填事件名稱與開始時間');return}
 await put('events',{id:uid(),title,start,end,note:qs('eventNote').value.trim(),createdAt:nowISO()});
 qs('eventTitle').value='';qs('eventStart').value='';qs('eventEnd').value='';qs('eventNote').value='';await renderEvents();await renderSummary();
}
async function renderEvents(){
 if(!db)return;const arr=(await getAll('events')).sort((a,b)=>a.start.localeCompare(b.start));
 qs('eventList').innerHTML=arr.length?arr.map(x=>`<div class="item"><strong>${esc(x.title)}</strong><div class="meta">${new Date(x.start).toLocaleString()}${x.end?' → '+new Date(x.end).toLocaleString():''}</div><div>${esc(x.note||'').replace(/\n/g,'<br>')}</div><button class="danger" style="margin-top:8px" onclick="removeItem('events','${x.id}')">刪除</button></div>`).join(''):'<p class="small">還沒有事件。</p>';
}
function icsTime(s){return new Date(s).toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z')}
async function downloadICS(){
 const arr=await getAll('events');if(!arr.length){alert('尚無事件');return}
 let body='BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Phantom Capsule//ZH-TW\r\n';
 for(const x of arr){body+=`BEGIN:VEVENT\r\nUID:${icsEscape(x.id)}\r\nDTSTAMP:${icsTime(x.createdAt)}\r\nDTSTART:${icsTime(x.start)}\r\n${x.end?`DTEND:${icsTime(x.end)}\r\n`:''}SUMMARY:${icsEscape(x.title)}\r\nDESCRIPTION:${icsEscape(x.note||'')}\r\nEND:VEVENT\r\n`}
 body+='END:VCALENDAR\r\n';downloadBlob(new Blob([body],{type:'text/calendar'}),'📅幻影膠囊行事曆.ics');
}

async function saveFiles(){
 const files=[...qs('fileInput').files];if(!files.length)return;
 try{
  for(const f of files){const ab=await f.arrayBuffer();await put('files',{id:uid(),name:f.name,type:f.type||'application/octet-stream',size:f.size,data:b64(ab),createdAt:nowISO()})}
  qs('fileInput').value='';await renderFiles();await renderSummary();
 }catch(e){alert('檔案保存失敗：'+(e.message||e))}
}
async function renderFiles(){
 if(!db)return;const arr=(await getAll('files')).sort((a,b)=>b.createdAt.localeCompare(a.createdAt));
 qs('fileList').innerHTML=arr.length?arr.map(x=>`<div class="item"><strong>${esc(x.name)}</strong><div class="meta">${Math.round(x.size/1024)} KB｜${new Date(x.createdAt).toLocaleString()}</div><div class="row"><button onclick="downloadStoredFile('${x.id}')">下載</button><button class="danger" onclick="removeItem('files','${x.id}')">刪除</button></div></div>`).join(''):'<p class="small">還沒有檔案。</p>';
}
async function downloadStoredFile(id){const x=(await getAll('files')).find(v=>v.id===id);if(x)downloadBlob(new Blob([unb64(x.data)],{type:x.type}),x.name)}

async function saveSecret(){
 const title=qs('secretTitle').value.trim(),text=qs('secretText').value.trim();if(!text)return;
 const enc=await encryptText(text);await put('secrets',{id:uid(),title:title||'未命名秘密',enc,createdAt:nowISO()});
 qs('secretTitle').value='';qs('secretText').value='';await renderSecrets();await renderSummary();
}
async function renderSecrets(){
 if(!db)return;const arr=(await getAll('secrets')).sort((a,b)=>b.createdAt.localeCompare(a.createdAt));
 let html='';for(const x of arr){let txt='（解密失敗）';try{txt=await decryptText(x.enc)}catch(e){}
 html+=`<div class="item"><div class="meta">${new Date(x.createdAt).toLocaleString()}</div><strong>${esc(x.title)}</strong><div style="margin:8px 0">${esc(txt).replace(/\n/g,'<br>')}</div><button class="danger" onclick="removeItem('secrets','${x.id}')">刪除</button></div>`}
 qs('secretList').innerHTML=html||'<p class="small">還沒有秘密訊息。</p>';
}

async function removeItem(store,id){if(confirm('確定刪除？')){await del(store,id);await refreshAll()}}
async function renderSummary(){
 if(!db)return;const counts={};for(const s of ['chat','voice','events','files','secrets'])counts[s]=(await getAll(s)).length;
 qs('summary').textContent=`聊天 ${counts.chat}｜語音 ${counts.voice}｜行事曆 ${counts.events}｜檔案 ${counts.files}｜秘密 ${counts.secrets}`;
}
async function loadMeetingLink(){if(!db)return;const m=(await getAll('meta')).find(x=>x.id==='identity');qs('meetingLink').value=m?.meetingLink||''}
async function saveMeetingLink(){
 const link=qs('meetingLink').value.trim(),safe=link?safeMeetingURL(link):'';
 if(link&&!safe){alert('連結格式不允許。請使用 https、http、FaceTime、Zoom 或電話連結。');return}
 const all=await getAll('meta'),m=all.find(x=>x.id==='identity');if(!m){alert('找不到膠囊身分資料');return}
 m.meetingLink=safe||'';await put('meta',m);qs('meetingLink').value=m.meetingLink;alert('已保存');
}
function openMeetingLink(){
 const safe=safeMeetingURL(qs('meetingLink').value);if(!safe){alert('連結格式不允許或尚未設定。');return}
 location.assign(safe);
}

async function collectAll(){
 const data={format:'PhantomCapsule',version:1,exportedAt:nowISO(),stores:{}};
 for(const s of CAPSULE_STORES)data.stores[s]=await getAll(s);return data;
}
function downloadBlob(blob,name){
 const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name;a.hidden=true;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);
}
async function exportCapsule(){
 const data=await collectAll(),blob=new Blob([JSON.stringify(data)],{type:'application/json'});cachedExportFile=new File([blob],'🪞個人幻影膠囊備份.json',{type:'application/json'});
 downloadBlob(blob,cachedExportFile.name);qs('transferStatus').innerHTML='<div class="status ok">膠囊已匯出。</div>';
}
async function shareCapsule(){
 const data=await collectAll(),file=new File([JSON.stringify(data)],'🪞個人幻影膠囊備份.json',{type:'application/json'});
 try{
  if(navigator.canShare&&navigator.canShare({files:[file]}))await navigator.share({title:'個人幻影膠囊',files:[file]});
  else{downloadBlob(file,file.name);qs('transferStatus').innerHTML='<div class="status warning">此瀏覽器未提供檔案分享，已改為下載。</div>'}
 }catch(e){if(e.name!=='AbortError')qs('transferStatus').innerHTML='<div class="status dangerbox">分享失敗：'+esc(e.message||e)+'</div>'}
}
async function exportAIHandoff(){
 const chats=await getAll('chat'),events=await getAll('events');
 const text={type:'AI_HANDOFF',owner:currentOwner,createdAt:nowISO(),instruction:'請根據以下內容接續協助，但不要替使用者做決定。',chat:chats,calendar:events};
 downloadBlob(new Blob([JSON.stringify(text,null,2)],{type:'application/json'}),'🤖AI接續包.json');
}
async function importCapsuleFile(file,atLock){
 if(!file)return;
 try{
  const data=JSON.parse(await file.text());
  if(data.format!=='PhantomCapsule'||!data.stores||typeof data.stores!=='object')throw new Error('格式不符');
  await openDB();
  for(const s of CAPSULE_STORES){const arr=data.stores[s];if(arr===undefined)continue;if(!Array.isArray(arr))throw new Error(`${s} 資料格式不符`);for(const x of arr){if(!x||typeof x!=='object'||!x.id)throw new Error(`${s} 物件缺少 id`);await put(s,x)}}
  if(atLock){alert('已匯入。請用原本名字與密語解鎖。');location.reload()}else{await refreshAll();qs('transferStatus').innerHTML='<div class="status ok">匯入完成。</div>'}
 }catch(e){alert('匯入失敗：'+(e.message||e))}
}
async function eraseAll(){
 if(!confirm('這會清除本機全部膠囊資料。請先匯出備份。確定繼續？'))return;
 for(const s of CAPSULE_STORES)await clearStore(s);sessionStorage.removeItem('capsulePass');location.reload();
}
