'''
Created on Sep 24, 2013

@author: samshuster
'''
class Transition(object):
    def __init__(self, dest, inp, out=None, prob=None, prestate = False):
        self.inp = str(inp)
        self.out = out
        self.prob = prob
        if not prestate:
            self.dest = State(dest)
        else:
            self.dest = dest
        
    def __repr__(self):
        ret = "({0} {1}".format(self.dest.name, self.inp)
        if self.out is not None:
            ret += (' ' + str(self.out))
        if self.prob is not None:
            ret += (' %(prob)f'%{'prob':self.prob})
        return ret + ')'

class CountNode(object):
    def __init__(self, name):
        self.name = name.replace('(','OPAR')
        self.name = self.name.replace(')','CPAR')
        self.name = self.name.replace('"','')
        self.children = {}
        self.count = 0
        self.trans = []
    
    def incr(self,num = 1):
        self.count += num
       
       
    def get_prob(self, inp):
        ret = 0
        for t in self.trans:
            if t.inp == inp:
                return t.prob
        return ret

    def get_child(self, name, insert = False):
        if not self.children.has_key(name) and insert:
            self.children[name] = CountNode(self.name+'-'+name)
        elif not self.children.has_key(name):
            raise Exception()
        return self.children[name]
    
    def make_transitions(self, root, final):
        if self.children:
            self.trans.append(Transition(final,'*e*',1.0))
        for c in self.children:
            nc = self.children[c]
            nc.make_transitions(root, final)
            if nc.children:
                self.trans.append(Transition(nc.name,c,prob=nc.count/float(self.count)))
            else:
                cname = c.replace('(','OPAR')
                cname = cname.replace(')','CPAR')
                cname = cname.replace('"','')
                cname = root+"-"+cname
                self.trans.append(Transition(cname,c,prob=nc.count/float(self.count)))
    
    def friendly_repr(self):
        child = ' '.join([self.children[x].friendly_repr() for x in self.children])
        if child == '':
            child = '|'
        else:
            child = '->'+child
        return '('+self.name + ',' + str(self.count) + ')' + child
    
    def __repr__(self):
        ret = '('+self.name+' '
        trans = ' '.join([str(x) for x in self.trans])
        if trans == '':
            return ''
        ret += trans + ' )'
        ret += '\n'
        for c in self.children:
            ret += str(self.children[c])
        return ret

class CountTree(object):
    ROOT = 'R*'
    FINAL = '*FINAL*'
    def __init__(self):
        self.root = CountNode(self.ROOT)
    
    def insert(self, observed_path):
        self.root.incr()
        self._insert(observed_path,self.root,'')
    
    def get(self, observed_path):
        cur_node = self.root
        for t in observed_path:
            cur_node = cur_node.get_child(t)
        return cur_node
    
    def get_prob(self, observed_path):
        cur_node = self.get(observed_path[:-1])
        return cur_node.get_prob(observed_path[-1])
        
    def gen_prob_matrix(self, dic, prob):
        if not dic:
            return prob
        ret = {}
        for t in dic:
            ret[t.inp] = self.gen_prob_matrix(t.dest.trans,t.prob)
        return ret
    
    def _insert(self, observed_path, parent, name):
        tokens = observed_path[0]
        if type(tokens) != tuple:
            tokens = (tokens,)
        incr = len(tokens)-1
        parent.incr(incr)
        for tok in tokens:
            cur_node = parent.get_child(tok,True)
            cur_node.incr()
            #base case
            if len(observed_path) <= 1:
                return
            else:
                self._insert(observed_path[1:], cur_node, tok)
    
    def compile_carmel(self):
        self.root.make_transitions(self.ROOT, self.FINAL)
    
    def friendly_repr(self):
        return self.root.friendly_repr()
    
    def __repr__(self):
        return str(self.root)

class State(object):
    def __init__(self, name):
        self.name = name
        self.trans = []
        
    def add_transition(self, name, inp, output=None, prob=None, prestate = False):
        self.trans.append(Transition(name,inp,output,prob,prestate))
        
    def __repr__(self):
        ret = '('+self.name+' '
        trans = ' '.join([str(x) for x in self.trans])
        ret += trans + ' )\n'
        for x in self.trans:
            if x.dest.trans:
                ret += str(x.dest)
        return ret
        
    def __getitem__(self,inp):
        ret = []
        for t in self.trans:
            if t.inp == inp:
                ret.append(t)
        return ret
    
    def gen_prob_matrix(self, dic, prob):
        if not dic:
            return prob
        ret = {}
        for t in dic:
            ret[t.inp] = self.gen_prob_matrix(t.dest.trans,t.prob)
        return ret
    
    def get_prob(self, inp, out = None):
        ret = 0
        for t in self.trans:
            if t.inp == inp:
                if out is not None:
                    if t.out == out:
                        return t.prob
        return ret
    
    def __setitem__(self,name,obj):
        pass

def build_ngram(db, n):
    tree = CountTree()
    for ind in range(len(db)-n):
        seq = [db[x] for x in range(ind,ind+n)]            
        tree.insert(seq)
        #list of tuples containing tags that were present in sequence
    return tree

def write_to_carmel(fs, f, final = '*FINAL*'):
    with open(f, 'w') as out:
        out.write(final)
        out.write('\n')
        out.write(str(fs))
        
