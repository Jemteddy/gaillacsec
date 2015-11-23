import os
import numpy as np
import gensim as gs

import nltk.tokenize as nt
import auxFunctions as aux
import wikipedia as wk



class WordVectorModel(object):

    def __init__(self,files_path="../Ressources/",name='word2Vec',save_path='../Models/',existing_model=False):
        self.name = name
        self.files_path = files_path
        self.save_path = save_path
        if existing_model:
            self.model = gs.models.Word2Vec.load(save_path+'model_w2v_'+name)
        else:
            self.model = []


    def train(self,path='../Ressources/',modelName='word2Vec',min_count=5,workers=5,end_train=True):
        sentences = aux.MySentences(path)
        self.model = gs.models.Word2Vec(sentences,min_count=min_count,workers=workers)
        if end_train:
            self.model.init_sims(replace=True)
        print 'model trained'

    def save(self):
        self.model.save(self.save_path+'model_w2v_'+self.name)

    def find_wiki_topics(self,nb_max=100,wikiTopics=['zoology','proteins','neuroscience','biochemistry','evolution','chemical interactions','immunology','taxonomy (biology)','bacteriology','botany','genetics']):
        n_dict=len(self.model.index2word)
        for topic in wikiTopics:
           if len(wikiTopics) >=nb_max :
               break
           try:
               l=self.model.most_similar([w for w in nt.word_tokenize(str(wk.page(topic).summary).lower()) if w in self.model],topn=n_dict)
           except:
               print topic+' not found'
               continue
           for word,r in l:
               if not word.lower() in wikiTopics:
                   wikiTopics.append(word.lower())
                   break
           for word,r in reversed(l):
               if not word.lower() in wikiTopics:
                   wikiTopics.append(word.lower())
                   break

        return wikiTopics


    def predict_answer(self, source='training',result_file='answers.csv'):
        # source must be 'training' or 'validation'
        res = np.zeros([2, 3]).astype('int')
        data_set = aux.preprocessData('../Data/'+source+'_set.tsv')
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


    def predict_prob(self, source='training',result_file='answers.csv'):
        # source must be 'training' or 'validation'
        data_set = aux.preprocessData('../Data/'+source+'_set.tsv')
        replies = ['A', 'B', 'C', 'D']
        probs=[]
        for index, row in data_set.iterrows():
            prob=[]
            r = -1
            row['question'] = row['question'].replace('. ', ' . ').replace('-', ' - ').replace('.', ' .').replace('_', ' ').lower()
            if (row['question'][-1]=='.'):
                row['question']=row['question'][:-1]+' . '
            for word in nt.word_tokenize(row['question']):
                try:
                    self.model[word]
                except:
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
                        ans = ans.replace(word, '')
                try:
                    ans = nt.word_tokenize(ans)
                    if ans==[]:
                        continue
                    if row['type'] != 1:
                        quest = nt.word_tokenize(row['question'])
                        r_current = np.exp(self.model.n_similarity(quest, ans))
                    else:
                        ind = row['question'].find('   ')

                        if row['question'][ind + 1:].split() == []:
                            r_current = np.exp(self.model.n_similarity(nt.word_tokenize(row['question']), ans))

                        elif row['question'][0:ind].split() == []:
                            r_current = np.exp(self.model.n_similarity(nt.word_tokenize(row['question'][ind:]), ans))

                        else:
                            r_current = np.exp(self.model.n_similarity(nt.word_tokenize(row['question'][0:ind]),
                                                           ans)) * np.exp(self.model.n_similarity(nt.word_tokenize(row['question'][ind:]),
                                                                                     ans))
                except:
                    ()
                prob.append(r_current)
                if r_current > r:
                    r = r_current
                # c
            ptot = sum(prob)
            prob= [ p/ptot for p in prob]
            probs.append(prob)


        return probs