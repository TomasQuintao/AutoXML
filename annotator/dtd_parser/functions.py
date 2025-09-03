from .dtd_yacc import dtd_parser

def parseDTD(dtd):
    
    if (dtd[-4:] == ".dtd"):
        with open(dtd, 'r', encoding='utf-8') as f:
            dtd = f.read()
    
    info = dtd_parser.parse(dtd)
    
    # Storing the attributes in the corresponding element and finding the root
    all_children = []
    for key in list(info.keys()): #The list allows deleting keys from the dict
        if key[0]=='_':
           info[key[1:]]['attributes'] = info[key]
           del info[key]
        
        elif info[key]['content_type'] != 'text_only':
            all_children += info[key]['children']
    
    for key in info:
        if key not in all_children:
            root_tag = key
            
    info['root'] = info.pop(root_tag)
    info['root']['tag'] = root_tag
            
    return info

def add_attributes(dtd_file, element, attributes, outpath="default"):

    with open(dtd_file, 'r', encoding='utf-8') as f:
        dtd = f.read()
    
    for (name, att_type, value_decl) in attributes:
        dtd += f"\n<!ATTLIST {element} {name} {att_type} {value_decl}>"
        
    if (outpath=="default"):
        outpath = dtd_file
        
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(dtd)
    
    return outpath

def get_labels(dtd):
    doc_tag = dtd['root']['children'][0]
    
    labels = list(dtd.keys())
    labels.remove('root')
    labels.remove(doc_tag)
    
    return labels

def assignLayer(dtd_tree):
    
    labels = get_labels(dtd_tree)
    doc_name = dtd_tree['root']['children'][0]

    layers = {}
    for label in labels:
  
        layer = max_depth(label, dtd_tree, doc_name)
        layers[label] = layer    
    
    return layers

def max_depth(label, dtd, doc_name):

    parents = parentsOf(label, dtd)
    
    depth = lambda x: 1 if x == doc_name else 1 + max_depth(x, dtd, doc_name)
    depths = list(map(depth, parents))
    
    return max(depths)


def parentsOf(label, dtd):

    parents = []
    
    for key in dtd:
        info = dtd[key]
        if info['content_type'] != 'text_only':
            
            if label in info['children']:
                parents.append(key)
   
    return parents 
    
    
