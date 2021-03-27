#!/usr/bin/env python
# coding: utf-8

# ## Side project: Analysis tool to determine which tags have which kids

# Use whichever hashing library is available. 
try:
    import mmh3 as mmh
except ModuleNotFoundError:
    import murmurhash as mmh

from bs4 import element as bel


class tag_index:
    __slots__ = ['navstring','name','properties','values','_hash']
    
    # Object is immutable, so hash is calculated on initialization
    # and never changes. 
    def __hash__(self):
        return self._hash
    
    def __eq__(self,other):
        return (self._hash == other._hash)
     
    def __ne__(self,other):
        return (self._hash == other._hash)
    
    def _genhash(self):
        properties_bytes = b'\xFE'+b'\xFF'.join(self.properties)
        values_bytes     = b'\xFE'+b'\xFF'.join(self.values)
        
        ready4hash =(
                    bytes(self.navstring) 
                    + self.name             
                    + properties_bytes      
                    + values_bytes
                    )
        gen_hash = mmh.hash(ready4hash)
        #print(f'hash of {gen_hash} from \n{ready4hash}')
        
        return gen_hash
        
        
    
    def __init__(self, tag):
        if type(tag) is bel.NavigableString:
            self.navstring = True
            self.name = b"<...>"
            self.properties = tuple()
            self.values = tuple()
        else:
            self.navstring = False
            self.name = bytes(tag.name,'utf-8')
            
            props = list()
            vals  = list()
            for key, values in tag.attrs.items():
                if type(values) is list:
                    values = " ".join(values)
                props.append(bytes(key,'utf-8'))
                vals.append(bytes(values,'utf-8'))
            thing = bytes('href','utf-8')
            if thing in props:
                idx = props.index(thing)
                props.pop(idx)
                vals.pop(idx)
                
            self.properties = tuple(props)
            self.values     = tuple(vals)
        self._hash = self._genhash()
    
    def __set__(self,instance,value):
        raise AttributeError("Can't change these values!")
        self.name = tag.name


# In[18]:


class leaf:
    __slots__ = ['hits','children']
    
    def __init__(self,node):
        self.hits = 1       
        # for each child node, generate a index for it, then
        # have it construct itself. This will continue recursively
        if type(node) is bel.NavigableString:
            #print("NAVSTRING!")
            self.children = None
        elif len(node.contents) == 0:
            #print("NOKIDS!")
            self.children = None
        else:
            self.children = dict()
            for child in node.children:
                #print(child)
                idx = tag_index(child)
                lef = leaf(child)
                self.children[idx] = lef
                     
    # Called to see what members two trees share in common
    def merge (self,otherleaf):
        # the fact that this method is being called, implies
        # the other tree contains this node.
        self.hits += 1
        if self.children is None:
            self.children = otherleaf.children
            return
        if otherleaf.children is None:
            return
        for index, child in otherleaf.children.items():
            # If this is a new entry, add it in
            if index not in self.children:
                self.children[index] = child
            # If we've seen it before, call recursively.
            else:
                self.children[index].merge(child)
    
    def displaytree (self, indxobject, indent = 0):
        rootname = indxobject.name.decode()
        properties = ",".join([f"{i.decode():.15}"for i in indxobject.values])
        retstring = ("-"*2*indent)+rootname+":"+str(self.hits)+":"+properties+'\n'

        if self.children is not None:
            childlist = self.children.items()
            for idx,child_pair in enumerate(childlist):
                indexobject, leafobject = child_pair
                retstring += leafobject.displaytree(indexobject, indent+1)
        return retstring