import lucene
import os
import numpy as np
import shutil
 
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader
from org.apache.lucene.queryparser.classic import QueryParser

import auxFunctions as aux

class SearchEngine(object):

    def __init__(self,index_path="../Ressources/index",files_path="../Ressources/"):
        self.index_path = index_path
        self.files_path = files_path
        self.searcher = None
        self.analyzer = None
        lucene.initVM()


    def index(self):
        try:
            shutil.rmtree(self.index_path)
        except:
            print 'no index found'
        #### indexer
        indexDir = SimpleFSDirectory(File(self.index_path))
        writerConfig = IndexWriterConfig(Version.LUCENE_4_10_1, StandardAnalyzer())
        writerConfig.setWriteLockTimeout(long(10000))
        writer = IndexWriter(indexDir, writerConfig)

        print "%d docs in index" % writer.numDocs()
        print "Reading lines from "+self.files_path+" ..."
        n=0
        for fname in os.listdir(self.files_path):
           if (os.path.isfile(os.path.join(self.files_path, fname)) and fname!='.DS_Store'):
               n+=1
               f=open(os.path.join(self.files_path, fname),'r')
               doc = Document()
               doc.add(Field("text", f.read(), Field.Store.YES, Field.Index.ANALYZED))
               writer.addDocument(doc)
        print "Indexed %d lines from stdin (%d docs in index)" % (n, writer.numDocs())
        print "Closing index of %d docs..." % writer.numDocs()
        writer.close()


    #### retriever
    def search(self,text,m):
        if self.analyzer is None: 
            self.analyzer = StandardAnalyzer(Version.LUCENE_4_10_1)
        if self.searcher is None: 
            reader = IndexReader.open(SimpleFSDirectory(File(self.index_path)))
            self.searcher = IndexSearcher(reader)
        query = QueryParser(Version.LUCENE_4_10_1, "text", self.analyzer).parse(QueryParser.escape(text))
        hits = self.searcher.search(query, m)
        return hits
        
        
    def predict_answer(self,maxs=[1], source='training',result_file='answers.csv'):
       # source must be 'training' or 'validation'
        res = np.zeros([len(maxs)+1, 3]).astype('int')
        data_set = aux.processData('../Data/'+source+'_set.tsv')
        replies = ['A', 'B', 'C', 'D']
        goodAnswersCount = 0
        res_ind=0
#        lucene.initVM()
        if (source=='validation'):
            answer = open('../Results/'+result_file, 'w')
            answer.write('id,correctAnswer\n')
            
        for m in maxs:   
            res_ind += 1
            for index, row in data_set.iterrows():
                r = -1
                good = replies[0]
                res[0, row['type']] += 1
                row['question'] = row['question'].replace('_', ' ')
        
                for reply in replies:
                    r_current = 0
                    ans = row['answer' + reply]
        
                    if row['type'] != 1:
                        text = row['question']+' '+ans
                    else:
                        ind = row['question'].find('   ')
                        text=row['question'][0:ind]+' ' + ans+ ' '+ row['question'][ind:]            
                    try:
                        hits = self.search(text, m)
                        r_current = np.mean([hits.scoreDocs[i].score for i in range(len(hits.scoreDocs))])
                    except:
                        print text
                        r_current=0
        
                    if r_current > r:
                        r = r_current
                        good = reply
                if (source=='validation'):
                    answer.write(str(row['id']) + ',' + good + '\n')
                elif (source=='training'):
                    if (good==row['correctAnswer']):
                           goodAnswersCount+=1
                           res[res_ind,row['type']]+=1
        return [goodAnswersCount,res]
         