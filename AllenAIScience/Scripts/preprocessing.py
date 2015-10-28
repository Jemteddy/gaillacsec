# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:56:52 2015

@author: jeremyt909
"""
import os
import numpy as np
import pandas as pd
import gensim as gs
import wikipedia as wk

import nltk.tokenize as nt



### previous processing
# def processClassBook(oldPath='../Ressources/Concepts-CK-12Foundation.txt',newPath='../Ressources/new.txt'):
#    old = open(oldPath,'r')
#    new = open(newPath,'a')
#
#    #c=0
#    for line in old:
#    #    c+=1
#    #    if c==100:
#    #        break
#        if line == '\n':
#            continue
#        line=line.replace('\n',' ')
#        line=line.replace('. ','\n')
#        line=line.replace('? ','\n')
#        line=line.replace('! ','\n')
#        line=line.replace(', ',' , ')
#        line=line.replace(': ',' : ')
#        line=line.replace('; ',' ; ')
#        line=line.replace('"',' " ')
#        line=line.replace("'"," ' ")
#        line=line.replace(")"," ) ")
#        line=line.replace("(","( ")
#        line=line.replace("-"," - ")
#        line=line.lower()
#        new.write(line)


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


## iterator for files in ressources
class MySentences(object):

    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield nt.word_tokenize(line.replace('. ', ' . ').lower())


## first source of wikiTopics
# wikiTopics=['zoology','proteins','neuroscience','biochemistry','evolution','chemical interactions','immunology','taxonomy (biology)','bacteriology','botany','genetics']
# n_dict=len(model.index2word)
# for topic in wikiTopics:
#    if len(wikiTopics)>=50:
#        break
#    try:
#        l=model.most_similar([w for w in nt.word_tokenize(str(wk.page(topic).summary).lower()) if w in model],topn=n_dict)
#    except:
#        print topic+' not found'
#        continue
#    for word,r in l:
#        if not word.lower() in wikiTopics:
#            wikiTopics.append(word.lower())
#            break
#    for word,r in reversed(l):
#        if not word.lower() in wikiTopics:
#            wikiTopics.append(word.lower())
#            break




def trainWord2Vec(wikiTopics=[],path='../Ressources/',modelName='word2Vec'):
    getWikiTopics(topics=wikiTopics,path='../Ressources/')
    sentences = MySentences('../Ressources/')
    model = gs.models.Word2Vec(sentences,min_count=5,workers=5)
    model.save('../Models/model_'+modelName)

def applyWord2Vec(modelName='word2Vec', source='training'):
    # source must be 'training' or 'validation'
    model= gs.models.Word2Vec.load('../Models/model_'+modelName)
    res = np.zeros([2, 3]).astype('int')
    data_set = processData('../Data/'+source+'_set.tsv')
    replies = ['A', 'B', 'C', 'D']
    goodAnswersCount = 0
    unknowWordsCount = 0
    unknowWords=[]
    answer = open('../Results/answers.csv', 'w')
    answer.write('id,correctAnswer\n')
    for index, row in data_set.iterrows():
        r = -1
        good = replies[0]
        res[0, row['type']] += 1
        row['question'] = row['question'].replace('. ', ' . ').replace('_', ' ').lower()
        for word in nt.word_tokenize(row['question']):
            try:
                model[word]
            except:
                unknowWordsCount += 1
                if not word.lower() in unknowWords:
                    unknowWords.append(word.lower())
                row['question'] = row['question'].replace(word, '')

        for reply in replies:
            r_current = -1
            ans = nt.word_tokenize(row['answer' + reply].lower())
            try:
                if row['type'] != 1:
                    quest = nt.word_tokenize(row['question'])
                    r_current = model.n_similarity(quest, ans)
                else:
                    ind = row['question'].find('   ')

                    if row['question'][ind + 1:].split() == []:
                        r_current = model.n_similarity(nt.word_tokenize(row['question']), ans)

                    elif row['question'][0:ind].split() == []:
                        r_current = model.n_similarity(nt.word_tokenize(row['question'][ind:]), ans)

                    else:
                        r_current = np.exp(model.n_similarity(nt.word_tokenize(row['question'][0:ind]),
                                                       ans)) * np.exp(model.n_similarity(nt.word_tokenize(row['question'][ind:]),
                                                                                 ans))
            except:
                unknowWordsCount += 1
            if r_current > r:
                r = r_current
                good = reply
            # c
        if (source=='validation'):
            answer.write(str(row['id']) + ',' + good + '\n')
        elif (source=='training'):
            if (good==row['correctAnswer']):
                   goodAnswersCount+=1
                   res[1,row['type']]+=1

    return [goodAnswersCount,unknowWordsCount,unknowWords,res]

# trainWord2Vec()
[goodAnswersCount,unknowWordsCount,unknowWords,res]=applyWord2Vec()
print goodAnswersCount
print unknowWordsCount
print res