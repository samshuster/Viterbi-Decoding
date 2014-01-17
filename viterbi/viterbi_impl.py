'''
Created on Sep 26, 2013

@author: samshuster
'''
import numpy as np

def viterbi_search(bigram, trans, POS, text):
    n = len(text)
    m = len(POS)
    Q = np.zeros(shape=(m,n))
    best_pred = np.zeros(shape=(m,n))
    for ind_p,pos in enumerate(POS):
        try:
            Q[ind_p,0] = trans[pos+'|'+text[0]] * bigram.get_prob([pos])
        except:
            Q[ind_p,0] = 0
        #print 'Word: {0} POS: {1} Q: {2}'.format(text[0],POS[ind_p],Q[ind_p,0])
    for word_i, word in enumerate(text[1:]):
        word_i += 1
        for pos_j, pos_cur in enumerate(POS):
            Q[pos_j,word_i] = 0
            best_pred[pos_j,word_i] = 0
            best_score = float('-inf')
            for pos_k, pos_prev in enumerate(POS):
                a = bigram.get_prob([pos_prev,pos_cur])
                try:
                    b = trans[pos_cur+'|'+word]
                except:
                    b = 0
                c = Q[pos_k,word_i-1]
                r = a*b*c
                #print pos_prev, pos_cur, word, a, b, c
                if r > best_score:
                    best_score = r
                    best_pred[pos_j,word_i] = pos_k
                    Q[pos_j,word_i] = r
            #print 'Word: {0} POS: {1} Q: {2}'.format(text[word_i],POS[pos_j],Q[pos_j,word_i])
    total = m*n
    count = 0
    for a in Q:
        for b in a:
            if b > 0 or b < 0:
                count += 1
    print count, total 
    final_best = 0
    final_score = float('-inf')
    for pos_j, pos in enumerate(POS):
        if Q[pos_j,n-1] > final_score:
            final_score = Q[pos_j,n-1]
            final_best = pos_j
    ret = []
    ret.insert(0,POS[int(final_best)])
    current = final_best
    for i in range(n-2,-1,-1):
        current = best_pred[current,i+1]
        ret.insert(0,POS[int(current)])
    print ret

def run(bigram, trans, f):
    with open(f,'r') as inp:
        for line in inp:
            sentence = line.strip().split(' ')
            POS = bigram.root.children.keys()
            viterbi_search(bigram,trans,POS,sentence)
    