# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:56:52 2015

@author: jeremyt909
"""

import luceneSearch as ls
import wordVector as wv



#### word2vec model 
word_vector= wv.WordVectorModel()
word_vector.train()
[goodAnswersCount,unknowWordsCount,unknowWords,res]=word_vector.predict_answer()#source='validation')
print unknowWordsCount
print goodAnswersCount
print res

#### lucene model
search_engine = ls.SearchEngine()
[goodAnswersCount,res]=search_engine.predict_answer(maxs=[2])#,source='validation')
print goodAnswersCount
print res


