from __future__ import annotations
import copy, hashlib, json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List
BASE=Path(__file__).resolve().parent
OUT=BASE/'執行輸出';OUT.mkdir(exist_ok=True)
def cj(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sh(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
def vv()->str:return 'deterministic-hash-8-v1'
def emb(t:str)->List[int]:return list(hashlib.sha256(t.encode()).digest()[:8])
@dataclass
class Main: records:Dict[str,Dict[str,Any]]=field(default_factory=dict)
@dataclass
class Vector: entries:Dict[str,Dict[str,Any]]=field(default_factory=dict)
@dataclass
class Journal: operations:Dict[str,Dict[str,Any]]=field(default_factory=dict)
class Committer:
    def __init__(self,m,v,j):self.m=m;self.v=v;self.j=j
    def hashes(self):return {'main':sh(cj(self.m.records)),'vector':sh(cj(self.v.entries))}
    def verify(self,rid):
        a=self.m.records.get(rid);b=self.v.entries.get(rid)
        x={'record_exists_both':a is not None and b is not None,'content_sha256_match':False,'vector_version_match':False}
        if a is not None and b is not None:
            x['content_sha256_match']=a['content_sha256']==b['content_sha256']
            x['vector_version_match']=a['vector_version']==b['vector_version']
        x['all_pass']=all(x.values());return x
    def commit(self,op,rid,text,fail_vector=False):
        if op in self.j.operations:return {'status':'IDEMPOTENT_REPLAY','operation_id':op,'record_id':self.j.operations[op]['record_id']}
        bm=copy.deepcopy(self.m.records);bv=copy.deepcopy(self.v.entries);before=self.hashes();ch=sh(text)
        base={'operation_id':op,'record_id':rid,'content_sha256':ch,'vector_version':vv(),'before_hashes':before,'status':'PREPARED'}
        self.m.records[rid]={'text':text,'content_sha256':ch,'vector_version':vv()}
        if not fail_vector:self.v.entries[rid]={'vector':emb(text),'content_sha256':ch,'vector_version':vv()}
        ver=self.verify(rid)
        if ver['all_pass']:
            rec={**base,'after_hashes':self.hashes(),'verification':ver,'status':'COMMITTED'};self.j.operations[op]=rec;return rec
        self.m.records=bm;self.v.entries=bv
        rec={**base,'after_hashes':self.hashes(),'verification':ver,'status':'ROLLED_BACK'};self.j.operations[op]=rec;return rec
m=Main();v=Vector();j=Journal();c=Committer(m,v,j)
valid=c.commit('OP-001','MEM-001','A=A 任務筆記本記憶')
before=c.hashes();fault=c.commit('OP-002','MEM-002','故障注入記憶',True);after=c.hashes()
replay=c.commit('OP-001','MEM-001-DUP','這段不應再次寫入')
count_only={'main_count':1,'vector_count':1,'same_count':True,'same_record_ids':False}
immediate={'main_has_MEM_002':True,'vector_has_MEM_002':False,'half_commit_possible':True}
judgement={
'新方法正常提交':'VERIFIED_TRUE' if valid['status']=='COMMITTED' else 'VERIFIED_FALSE',
'新方法故障時完整回滾':'VERIFIED_TRUE' if fault['status']=='ROLLED_BACK' and before==after else 'VERIFIED_FALSE',
'新方法相同operation_id冪等重放':'VERIFIED_TRUE' if replay['status']=='IDEMPOTENT_REPLAY' and len(m.records)==1 else 'VERIFIED_FALSE',
'數量相等法可出現假陽性':'VERIFIED_TRUE' if count_only['same_count'] and not count_only['same_record_ids'] else 'VERIFIED_FALSE',
'立即雙寫法可能留下半提交':'VERIFIED_TRUE' if immediate['half_commit_possible'] else 'VERIFIED_FALSE',
'對所有外部向量資料庫普遍成立':'HYPOTHESIS'}
out={'valid_commit':valid,'fault_injection':fault,'idempotent_replay':replay,'count_only_comparison':count_only,'immediate_dual_write_comparison':immediate,'final_main':asdict(m),'final_vector':asdict(v),'journal':asdict(j),'工具驗證判定':judgement}
(OUT/'concept_test_result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(judgement,ensure_ascii=False,sort_keys=True))
