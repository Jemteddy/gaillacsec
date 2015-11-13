# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:56:52 2015

@author: jeremyt909
"""

try:
    import luceneSearch as ls
    print 'luceneSearch imported'
except:
    ()
try:        
    import wordVector as wv
    print 'wordVector imported'
except:
    ()

try:        
    import auxFunctions as aux
    print 'auxFunctions imported'
except:
    ()


#### word2vec model 
word_vector= wv.WordVectorModel()
word_vector.train()
#wt = word_vector.find_wiki_topics(nb_max=500)
#aux.getWikiTopics(wt)
[goodAnswersCount,unknowWordsCount,unknowWords,res]=word_vector.predict_answer()#source='validation')
print unknowWordsCount
print goodAnswersCount
print res

#### lucene model
search_engine = ls.SearchEngine()
search_engine.index()
[goodAnswersCount,res] = search_engine.predict_answer(maxs=[3])#,source='validation')
print goodAnswersCount
print res



