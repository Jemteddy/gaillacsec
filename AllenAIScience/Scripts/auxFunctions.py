import os
import pandas as pd
import wikipedia as wk

from multiprocessing import Pool    



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

def getTopicQuestion(question,path_ressources='../Ressources/',nb_res=3):
    print question
    try:
        pages = wk.search(question,results=nb_res)
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
            
def wikiTopicQuestions(path_data='../Data/training_set.tsv',path_ressources='../Ressources/',proc=2):
    data_set = pd.read_csv(path_data, sep='\t')
    questions=[q for q in data_set['question']]
    pool = Pool(processes=proc)        
    pool.map(getTopicQuestion,questions)
            
            
def wikiTopicAnswers(path_data='../Data/training_set.tsv',path_ressources='../Ressources/',proc=2):
    data_set = pd.read_csv(path_data, sep='\t')
    answers = [q for q in data_set['answerA']]
    answers +=  [q for q in data_set['answerB']]
    answers += [q for q in data_set['answerC']]
    answers += [q for q in data_set['answerD']]
    pool = Pool(processes=proc)        
    pool.map(getTopicQuestion,answers)
  

