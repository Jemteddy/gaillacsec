import os
import pandas as pd
import wikipedia as wk



## get questions' type
def processData(path='../Data/training_set.tsv'):
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


