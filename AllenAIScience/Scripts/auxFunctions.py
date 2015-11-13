import os
import pandas as pd
import wikipedia as wk


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

