import os
import pandas as pd
import wikipedia as wk
import gensim as gs
import nltk.tokenize as nt

from multiprocessing import Pool    


## iterator for files in ressources
class MySentences(object):

    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            if (os.path.isfile(os.path.join(self.dirname, fname)) and fname!='.DS_Store'):
                for line in open(os.path.join(self.dirname, fname)):
                    if (line[-1]=='.'):
                        line=line[:-1]+' . '
                    yield nt.word_tokenize(line.replace('-', ' - ').replace('. ', ' . ').lower())

## get questions' type
def preprocessData(path='../Data/training_set.tsv'):
    train_set = pd.read_csv(path, sep='\t')
    types = [max(min(question.find('____') + 1, 1), 2 * min(question.find('?') + 1, 1)) for question in
             train_set['question']]
    train_set['type'] = pd.Series(types, index=train_set.index)
    return train_set


## get the wikipedia article and save it in text file
def getWikiTopics(topics=[], path='../Ressources/'):
    existing_files = os.listdir(path)
    for topic in topics:
        s = wk.search(topic)
        for top in s:
            try:
                fname = 'wiki_' + str(top) + '.txt'
                if fname in existing_files:
                    break
                text = str(wk.page(top).content)
                new = open(path + fname, 'w')
                new.write(text)
                break
            except:
                print topic


## retrieve random wiki articles
def randomWikiTopics(nb_max=1000, path='../Ressources/'):
    wk.set_lang('en')
    existing_files = os.listdir(path)
    pages=wk.random(nb_max)
    for page in pages:       
        try:
            print page
            fname = 'wiki_' + str(page) + '.txt'
            if fname in existing_files:
                break
            text = str(wk.page(page).content)
            new = open(path + fname, 'w')
            new.write(text)
        except:
            ()

### do a search and then get the nb_res first results
def getWikiQuery(query,path_ressources='../Ressources/',nb_res=3):
    print query
    try:
        pages = wk.search(query,results=nb_res)
    except:
        print 'FAUX'
        return
    existing_files = os.listdir(path_ressources)
    for page in pages:     
        try:
            fname = 'wiki_' + str(page) + '.txt'
            existing_files = os.listdir(path_ressources)
            if fname in existing_files:
                break
            text = str(wk.page(page).content)
            new = open(path_ressources + fname, 'w')
            new.write(text)
        except:
            ()                

### get the doc for the questions in the data_set            
def wikiTopicQuestions(path_data='../Data/training_set.tsv',path_ressources='../Ressources/',proc=2):
    data_set = pd.read_csv(path_data, sep='\t')
    questions=[q for q in data_set['question']]
    pool = Pool(processes=proc)        
    pool.map(getWikiQuery,questions)
            
            
            
### get the doc for the answerss in the data_set            
def wikiTopicAnswers(path_data='../Data/training_set.tsv',path_ressources='../Ressources/',proc=2):
    data_set = pd.read_csv(path_data, sep='\t')
    answers = [q for q in data_set['answerA']]
    answers +=  [q for q in data_set['answerB']]
    answers += [q for q in data_set['answerC']]
    answers += [q for q in data_set['answerD']]
    pool = Pool(processes=proc)        
    pool.map(getWikiQuery,answers)
  



def buildDataSet(model_path,path_ressources='../Ressources/',len_vocab=150000):
    data_set=[]
    model = gs.models.Word2Vec.load(model_path)
    sentences = MySentences(path_ressources)
    c=0
    vocab = dict()
    ind = 0
 
    for word in model.index2word:
        if ind < len_vocab : 
            vocab[word]=ind
            ind += 1
        else:
            break
    for sentence in sentences:        
        if c%1000 ==0:
            print c
        if len(sentence)>5:
            sen=[]
            c += 1
            for word in sentence:
                if word in vocab:
                    sen.append(vocab[word])
                else:
                    sen.append(-1)
            data_set.append(sen)
    return [vocab,data_set]
                    
                    
                    
def findPatternIndex(sentence,pattern):
    lenPattern = len(pattern)
    ind = []
    for i in range(len(sentence)-lenPattern+1):
        if (sentence[i]==pattern[0]) and sentence[i:i+lenPattern]==pattern:
            ind.append(i)
    if len(ind)>0:
        return ind
    return False

#[vocab,data]=buildDataSet('../Models/'+'model_w2v_'+'word2Vec')


def transformDoc(vocab,doc,size_max=3):
    transformedDoc=[]
    for line in doc.split('\n'): 
        line = nt.word_tokenize(line.replace('-', ' - ').replace('. ', ' . ').lower())
        if len(line)>size_max:
            sen=[]
            for word in line:
                if word in vocab:
                    sen.append(vocab[word])
                else:
                    sen.append(-1)
            transformedDoc.append(sen)
    return transformedDoc



def answerInDoc(vocab,answer,search_engine,nbDocs=4):
    hits = search_engine.search(answer,nbDocs)
    ansDoc=[]
    for ans in hits.scoreDocs :
        ansDoc.append(ans.doc)
    docs=[]
    for d in ansDoc:
        docs.append(search_engine.searcher.doc(d))
    docsTransformed=[]
    for d in docs:
        transformedDoc = transformDoc(vocab,d.get('text'))
        docsTransformed.append(transformedDoc)
    answerTransformed =  transformDoc(vocab,answer,size_max=-1)[0]
    res = [findPatternIndex(s,answerTransformed) for d in docsTransformed for s in d]
    return res
    

#
#for line in a.toString():
#    print line




