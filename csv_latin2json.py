#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import json
import os
import pandas
import math


# In[2]:


class Node:
    idnode = -1 #no id assigned
    kb = ""
    label = ""
    properties = {}

    def __init__(self, idnode, label, kb = "Latin WordNet", properties = {}):
        self.idnode = str(idnode)
        self.label = str(label)
        self.kb = kb
        self.properties = properties
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.idnode == other.idnode

    def set_properties(self, **kwargs):
        for k in kwargs:
            properties[k] = kwargs[k]

    def __str__(self):
        return f"{self.label}({self.name})"


# In[3]:


class Relationship:
    id_subject = ""
    id_object = ""
    properties = {}
    kb = ""
    
    def __init__(self, id_subject, id_object, name, kb = "Latin WordNet", properties={}):
        self.id_subject = str(id_subject)
        self.id_object = str(id_object)
        self.name = str(name)
        self.kb = kb
        self.properties = properties
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id_subject == other.id_subject and self.id_object == other.id_object and self.name == other.name

    def set_properties(self,**kwargs):
        for k in kwargs:
            properties[k] = kwargs[k]
            
    def __str__(self):
        return f"{self.label}({self.name})"


# In[4]:


def isNan(string):
    return string != string


# In[5]:


def print_json(file_path, nodes, relationships):
    print(len(nodes))
    print(len(relationships))
    file_json = file_path.split(".")[0] + "-json.json"   # file json di export
    write_json(file_json, nodes, relationships)
    print(file_json)

#file_path è il file json da scrivere, percorso assoluto
def write_json(file_path, nodes, relationships):
    with open(file_path, 'w+') as f:
        for n in nodes:
            f.write(json.dumps({
                'jtype': 'node',
                'identity': n.idnode,
                'label': n.label,
                'kb': n.kb,
                'properties': n.properties
            })+'\n')
            #rels = rels + node.relationships

        for r in relationships:
            f.write(json.dumps({
                'jtype': 'relationship',
                'subject': r.id_subject,
                'object': r.id_object,
                'name': r.name,
                'kb': r.kb,
                'properties': r.properties
            })+'\n')


# In[6]:


def map2json_1(file_path, mapped_names, label):
    nodes = []
    relationships = []
    
    print(file_path)
    df = pandas.read_csv(file_path)
    df_header = list(df.columns.values)
    
    for index, row in df.iterrows():
        properties = {}
        id_node = row[0] #id node

        for column in df_header:  # per tutte le colonne in realtà
            attribute = row[column]
            if(isNan(attribute)):     # se è NaN l'export in JSON viene danneggiato
                attribute = ""
            if(column in mapped_names):      # se la colonna è da mappare
                column = mapped_names[column]  # ridenominazione attributo
            properties.update({column: attribute})

        node = Node(id_node, label, "Latin WordNet", properties)  #creazione nodo
        nodes.append(node)
    
    print_json(file_path, nodes, relationships)


# In[7]:


import math

def map2json_2(file_path, distinguishing_column, mapped_names, to_create, label, *args):
    nodes = []
    relationships = []    
    
    df = pandas.read_csv(file_path)
    df_header = list(df.columns.values)
    
    for index, row in df.iterrows():
        attributes_indexes = [i for i in range(0, len(df.columns)) if i not in args]  # conservare attributi da non mappare in relazioni
        properties = {}
        id_node = row[0] #id node
        value_pos = ""
        for i in attributes_indexes:          #uguale a caso 1
            attribute = row[i]
            if(isNan(attribute)):
                attribute = ""
            if(df_header[i] in mapped_names):
                df_header[i] = mapped_names[df_header[i]]
            properties.update({df_header[i]: str(attribute)})
#             if df_header[i] == 'pos':
#                 value_pos = row[i]
        
        node = Node(id_node, label, "Latin WordNet", properties)
        nodes.append(node)
        
        for i in args:     # per tutti gli attributi da mappare in relazioni
            value = row[i] #mapped_names[row[i]] 
            if(isNan(value)):
                value = ""
            value = str(value).replace("0.", "")
            if(df_header[i] in mapped_names):    # salvo errori, questo if sarà sempre vero per gli attributi da mappare
                new_label = mapped_names[df_header[i]].split('.')[0]   # etichetta nuovo nodo
                attribute = mapped_names[df_header[i]].split('.')[1]  # attributo in cui conservo il valore del nuovo nodo
                new_rel = mapped_names[df_header[i]].split('.')[2]   #nome relazione tra nodo di partenza e nuovo nodo
                id_new_node = value 
                if to_create == True:
                    node = Node(id_new_node, new_label, "WordNet", {attribute: value}) # non vengono gestite altre eventuali proprietà del nuovo nodo
                    if node not in nodes:
                        nodes.append(node)
                value = str(value)
                if value != "":
                    if ',' not in value:
                        relationship = Relationship(label + '.' + attribute + '.' + str(id_node).replace(".0", ""), new_label + '.' + attribute + '.' + str(id_new_node).replace(".0", ""), new_rel, "Latin WordNet") # non vengono gestite altre eventuali proprietà della relazione
                        if relationship not in relationships:
                                relationships.append(relationship)
                    else:
                        values = value.split(',')
                        for value in values:
                            relationship = Relationship(label + '.' + str(value).replace(".0", ""), new_label + '.' + attribute + '.' + str(id_node).replace(".0", ""), new_rel, "Latin WordNet") # non vengono gestite altre eventuali proprietà della relazione
                            if relationship not in relationships:
                                relationships.append(relationship)
    
    print_json(file_path, nodes, relationships)


# In[8]:


def map2json_3(file_path, subj_class, obj_class, discerning_column, mapped_names, added_attributes, *args):
    print(file_path)
    df = pandas.read_csv(file_path)
    df_header = list(df.columns.values)
    relationships = []
    
    for index, row in df.iterrows():
        attributes_indexes = [i for i in range(0, len(df.columns)) if i not in args]  # uguale a caso 1
        properties = {}
        source = 1
        name_rel = ''
        id_subject = ''
        id_object = ''
        for i in range(0, len(df_header)):
            if i not in attributes_indexes:
                if df_header[i] in mapped_names:
                    if '.' in mapped_names[df_header[i]]:
                        if source == 1:
                            source = 0
                            id_subject = mapped_names[df_header[i]].split('.')[1] + '.' + str(row[i])
                        else:
                            id_object = mapped_names[df_header[i]].split('.')[1] + '.' + str(row[i])
                elif df_header[i] == discerning_column:
                    name_rel = mapped_names[row[i]]
                        
        if name_rel == '':
            name_rel = mapped_names['name_rel']

        for i in attributes_indexes:
            attribute = row[i]
            if(isNan(attribute)):
                attribute = ""
            if(df_header[i] in mapped_names):
                df_header[i] = mapped_names[df_header[i]]
            properties.update({df_header[i]: attribute})
                
        for key in added_attributes:
            properties.update({key: added_attributes[key]})
            
        relationship = Relationship(subj_class + '.' + str(id_subject), obj_class + '.' + str(id_object), name_rel, "Latin WordNet", properties) # non vengono gestite altre eventuali proprietà della relazione
        relationships.append(relationship)
            
    print_json(file_path, [], relationships)


# In[88]:


def fromWN302WN16(dir_mapping):
    wn3016mapping = {}
    
    df = pandas.read_csv(dir_mapping + 'wn30-16.adj', sep=' ', index_col=False, converters={'WN16': str, 'WN30': str})
    for index, row in df.iterrows():
        wn3016mapping[row['WN30'] + '-a'] = row['WN16'] + '-a'
        
    df = pandas.read_csv(dir_mapping + 'wn30-16.adv', sep=' ', index_col=False, converters={'WN16': str, 'WN30': str})
    for index, row in df.iterrows():
        wn3016mapping[row['WN30'] + '-d'] = row['WN16'] + '-d'
        
    df = pandas.read_csv(dir_mapping + 'wn30-16.noun', sep=' ', index_col=False, converters={'WN16': str, 'WN30': str})
    for index, row in df.iterrows():
        wn3016mapping[row['WN30'] + '-n'] = row['WN16'] + '-n'
        
    df = pandas.read_csv(dir_mapping + 'wn30-16.verb', sep=' ', index_col=False, converters={'WN16': str, 'WN30': str})
    for index, row in df.iterrows():
        wn3016mapping[row['WN30'] + '-v'] = row['WN16'] + '-v'
        
    return wn3016mapping


# In[94]:


def paola2WN16(file_annotations, wn3016mapping):
    df = pandas.read_csv(file_annotations, index_col=None, converters={'WN1.6': str, 'WN3.0': str})
    
    wn16synsets = []
    for index, row in df.iterrows():
        if row['WN1.6'] != "":
            wn16synsets.append(row['WN1.6'])
        else:
            wn30 = row['WN3.0']
            if wn30 not in wn3016mapping:
                a_s = wn30.replace('s', 'a')
                if a_s in wn3016mapping:
                    wn16synsets.append(wn3016mapping[a_s])
                else:
                    print('Not found: ' + a_s)
            else:
                wn16synsets.append(wn3016mapping[wn30])
        
    return wn16synsets


# In[95]:


dir = 'C:\\Users\\ddipi\\Desktop\\Davide\\Dottorato\\Linguistica\\Latin WordNet\\'
wn3016mapping = fromWN302WN16(dir + 'mapping-30-16\\')
#print(wn3016mapping)
wn_synsets = paola2WN16(dir + 'wordnet_annotated_data.csv', wn3016mapping)
len(wn_synsets)


# In[96]:


wn_synsets


# In[97]:


'01211817-a' in wn_synsets #01263013 in WN 3


# In[98]:


def wn2latinwn(file_synset, wn_synsets):
    df = pandas.read_csv(file_synset, index_col=None, converters={'id': str, 'pos': str, 'offset': str})
    
    latin_wn_synsets = []
    for synset in wn_synsets:
        d2 = df[(df['offset'] + '-' + df['pos'] == synset)]
        if d2.empty == False:
            latin_wn_synsets.append(str(d2['id'].iloc[0]))
    
    return latin_wn_synsets


# In[99]:


latin_wn_synsets = wn2latinwn(dir + 'synset.csv', wn_synsets)
len(latin_wn_synsets)


# In[101]:


def getHyperons(file_semantic_relation, latin_wn_synsets):
    df = pandas.read_csv(file_semantic_relation, index_col=None, converters={'id': str, 'type': str, 'source': str, 'target': str})
    
    hyperons_1 = {}
    for synset in latin_wn_synsets:
        d2 = df[(df['type'] == '@') & (df['source'] == synset)]
        if d2['target'].empty == False:
            hyperons_1[synset] = str(d2['target'].iloc[0])
        else:
            hyperons_1[synset] = ""
    
    hyperons_2 = {}
    for synset in hyperons_1.values():
        d2 = df[(df['type'] == '@') & (df['source'] == synset)]
        if d2['target'].empty == False:
            hyperons_2[synset] = str(d2['target'].iloc[0])
        else:
            hyperons_2[synset] = ""
            
    hyperons_3 = {}
    for synset in hyperons_2.values():
        d2 = df[(df['type'] == '@') & (df['source'] == synset)]
        if d2['target'].empty == False:
            hyperons_3[synset] = str(d2['target'].iloc[0])
        else:
            hyperons_3[synset] = ""
    
    hyperons = dict(hyperons_1)
    hyperons.update(hyperons_2)
    hyperons.update(hyperons_3)
    return hyperons


# In[102]:


hyperons = getHyperons(dir + 'semantic_relation.csv', latin_wn_synsets)
nodeset = []
for synset in hyperons:
    if synset not in nodeset and synset != '':
        nodeset.append(synset)
    if hyperons[synset] not in nodeset and hyperons[synset] != "": 
        nodeset.append(hyperons[synset])
len(nodeset)


# In[103]:


hyperons


# In[166]:


def filter_relationships_json(semantic_relation_file, nodeset):
    json_file = []
    with open(semantic_relation_file, "r") as f:
        for row in f:
            line = json.loads(row)
            jtype = line['jtype']
            subj = line['subject']
            obj = line['object']
            name = line['name']
            if subj.replace('Category.id.', '') in nodeset and obj.replace('Category.id.', '') in nodeset and name == 'hasSubclass':
                if row not in json_file:
                    json_file.append(row)
    
    return json_file


# In[167]:


with open(dir + 'synset-relationship.json', 'w') as f:
    json_file = filter_relationships_json(dir + 'semantic_relation-json.json', nodeset)
    for row in json_file:
        f.write(row)
    f.close()


# In[109]:


wn1630mapping = dict([(value, key) for key, value in wn3016mapping.items()])


# In[123]:


wn1630mapping


# In[134]:


from nltk.corpus import wordnet
def getLemmaSynset(nodeset, file_synset, wn1630mapping):
    df = pandas.read_csv(file_synset, index_col=None, converters={'id': str, 'offset': str})
    
    synsetlemma = {}
    for synset in nodeset:
        d2 = df[(df['id'] == synset)]
        pos = str(d2['pos'].iloc[0])
        offset_lw16 = str(d2['offset'].iloc[0])
        print(pos + ',' + offset_lw16)
        if (offset_lw16 + '-' + pos) in wn1630mapping:
            offset_lw30 = str(wn1630mapping[offset_lw16 + '-' + pos][:-2])
#             print(pos + str(int(offset_lw30)))
            synsetlemma[synset] = str(wordnet.synset_from_pos_and_offset(pos, int(offset_lw30))) + str(wn1630mapping[offset_lw16 + '-' + pos])        
        
    return synsetlemma


# In[135]:


synsetlemma = getLemmaSynset(nodeset, dir + 'synset.csv', wn1630mapping)
synsetlemma


# In[139]:


with open(dir + 'synset-ridotto-lemma2.json', 'w') as fw:
    df = pandas.read_csv(dir + 'synset.csv', index_col=None, converters={'id': str, 'offset': str})
    
    properties = {}
    for n in nodeset:
        d2 = df[(df['id'] == n)] 
        properties['id'] = d2['id'].iloc[0]
        properties['pos'] = d2['pos'].iloc[0]
        properties['language'] = d2['language'].iloc[0]
        properties['description'] = d2['gloss'].iloc[0]
        if n in synsetlemma:
            synset = synsetlemma[n].split(')')[0].replace("Synset('", "").replace("'", "")
            idwn30 = synsetlemma[n].split(')')[1]
            properties['value'] = synset
            properties['idWN3'] = idwn30
        else:
            print(n)
        fw.write(json.dumps({
            'jtype': 'node',
            'identity': d2['id'].iloc[0],
            'label': 'node',
            'kb': 'Latin WordNet',
            'properties': properties
        })+'\n')


# In[73]:


with open(dir + 'synset-ridotto-lemma.json', 'w') as fw:
    with open(dir + 'synset-ridotto.json', 'r') as fr:
        for row in fr:
            line = json.loads(row)
            jtype = line['jtype']
            if jtype == 'node':
                properties = line['properties']
                if line['identity'] in synsetlemma:
                    synset = synsetlemma[line['identity']].split(')')[0].replace("Synset('", "").replace("'", "")
                    idwn30 = synsetlemma[line['identity']].split(')')[1]
                    properties["value"] = synset
                    properties["idWN3"] = idwn30
                fw.write(json.dumps({
                    'jtype': 'node',
                    'identity': line['identity'],
                    'label': line['jtype'],
                    'kb': line['kb'],
                    'properties': properties
                })+'\n')
            else:
                fw.write(row)


# In[79]:


def filter_nodes_json(synset_file, nodeset, lemmasynset):
    json_file = ""
    with open(synset_file) as f:
        for row in f:
            line = json.loads(row)
            jtype = line['jtype']
            if jtype == 'node':
                identity = line['identity']
                if identity in nodeset:
                    json_file += row
    
    return json_file


# In[171]:


ids = []
with open(dir + 'synset-ridotto-lemma.json', 'r') as f:
    for row in f:
        line = json.loads(row)
        jtype = line['jtype']
        if jtype == 'node':
            ids.append(line['identity'])
        else:
            id_subject = line['subject'].replace("Category.id.", "")
            id_object = line['object'].replace("Category.id.", "")
            if str(id_subject) not in ids:
                print(id_subject)
            if str(id_object) not in ids:
                print(id_object)
        


# In[59]:





# In[ ]:




