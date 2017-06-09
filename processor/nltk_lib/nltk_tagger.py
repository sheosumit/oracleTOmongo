import nltk



def taggerFunc(write_file, line):
    #	write_file='output.txt'
    text = nltk.word_tokenize(line)
    tokenize_data=[]    
    for x in text:
        tokenize_data.append(x)
        
    taggedLine = nltk.pos_tag(tokenize_data)
    w = open(write_file, 'w')
    for i in taggedLine:
        w.write(i[0] + '\t' + i[1] + '\n')
    w.close()

