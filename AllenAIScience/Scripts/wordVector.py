import os
import numpy as np
import gensim as gs

import nltk.tokenize as nt
import auxFunctions as aux

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


class WordVectorModel(object):

    def __init__(self,files_path="../Ressources/",name='word2Vec',save_path='../Models/'):
        self.name = name
        self.files_path = files_path
        self.save_path = save_path
        self.model=[]


    def train(self,path='../Ressources/',modelName='word2Vec',min_count=5,workers=5):
        sentences = MySentences(path)
        self.model = gs.models.Word2Vec(sentences,min_count=min_count,workers=workers)
        print 'model trained'

    def save(self):
        self.model.save(self.save_path+'model_w2v_'+self.name)


    def predict_answer(self, source='training',result_file='answers.csv'):
        # source must be 'training' or 'validation'
        res = np.zeros([2, 3]).astype('int')
        data_set = aux.processData('../Data/'+source+'_set.tsv')
        replies = ['A', 'B', 'C', 'D']
        goodAnswersCount = 0
        unknowWordsCount = 0
        unknowWords=[]
        if (source=='validation'):
            answer = open('../Results/'+result_file, 'w')
            answer.write('id,correctAnswer\n')
        for index, row in data_set.iterrows():
            r = -1
            good = replies[0]
            res[0, row['type']] += 1
            row['question'] = row['question'].replace('. ', ' . ').replace('-', ' - ').replace('.', ' .').replace('_', ' ').lower()
            if (row['question'][-1]=='.'):
                row['question']=row['question'][:-1]+' . '
            for word in nt.word_tokenize(row['question']):
                try:
                    self.model[word]
                except:
                    unknowWordsCount += 1
                    if not word.lower() in unknowWords:
                        unknowWords.append(word.lower())
                    row['question'] = row['question'].replace(word, '')

            for reply in replies:
                r_current = -1
                ans = row['answer' + reply].replace('-', ' - ').replace('. ', ' . ').lower()
                if (ans[-1]=='.'):
                    ans=ans[:-1]+' . '
                for word in nt.word_tokenize(ans):
                    try:
                        self.model[word]
                    except:
                        unknowWordsCount += 1
                        if not word in unknowWords:
                            unknowWords.append(word)
                        ans = ans.replace(word, '')
                try:
                    ans = nt.word_tokenize(ans)
                    if ans==[]:
                        continue
                    if row['type'] != 1:
                        quest = nt.word_tokenize(row['question'])
                        r_current = self.model.n_similarity(quest, ans)
                    else:
                        ind = row['question'].find('   ')

                        if row['question'][ind + 1:].split() == []:
                            r_current = self.model.n_similarity(nt.word_tokenize(row['question']), ans)

                        elif row['question'][0:ind].split() == []:
                            r_current = self.model.n_similarity(nt.word_tokenize(row['question'][ind:]), ans)

                        else:
                            r_current = np.exp(self.model.n_similarity(nt.word_tokenize(row['question'][0:ind]),
                                                           ans)) * np.exp(self.model.n_similarity(nt.word_tokenize(row['question'][ind:]),
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
