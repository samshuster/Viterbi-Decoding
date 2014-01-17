'''
Created on Sep 24, 2013

@author: samshuster
'''
import carmel_classes as cc
import viterbi_impl as vit

DFile = 'train-data'
TestFile = 'test-data-1.sent'

def add_to_db(key, value, db):
    if not db.has_key(key):
        db[key] = {}
    poss = db[key]
    if not poss.has_key(value):
        poss[value] = 1
    else:
        poss[value] += 1

def construct_db(f,db):
    for line in f:
        try:
            word, tag = line.split('/')
        except:
            print line
        else:
            tags = tag.split('|')
            for tag in tags:
                add_to_db(tag.strip(),word.strip(),db)

def construct_wfst(db):
    ROOT = '*ROOT*'
    FINAL = '*FINAL*'
    emp = '*e*'
    fst = cc.State(ROOT)
    fst.add_transition(FINAL,emp,emp,1.0)
    for key in db:
        poss = db[key]
        total = 0
        for val in poss:
            total += poss[val]
        for val in poss:
            fst.add_transition(ROOT,'"'+key+'"','"'+val+'"',poss[val]/float(total))
    return fst
            
def write_fst(f, fst):
    f.write('*FINAL*\n')
    f.write(str(fst))       
        
def preprocess_file(f):
    sequence = []
    for line in f:
        _,tag = line.split('/')
        tags = tag.split('|')
        seq_tag = tuple('"'+t.strip()+'"' for t in tags)
        sequence.append(seq_tag)
    return sequence

def fst_input_output_matrix(fst):
    ret = {}
    for t in fst.trans:
        ret[t.inp+'|'+t.out] = t.prob
    return ret
    
    
db = {}        
construct_db(open(DFile,'r'), db)
fst = construct_wfst(db)
seq = preprocess_file(open(DFile,'r'))
fr2 = cc.build_ngram(seq,2)
fr2.compile_carmel()
fr2.root.trans.append(cc.Transition('*FINAL*','*e*',prob = 1.0))
fst_matrix = fst_input_output_matrix(fst)
vit.run(fr2,fst_matrix, TestFile)
