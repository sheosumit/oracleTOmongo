
from labels import label_marker
from nltk_lib import nltk_tagger
import input_processor
from datetime import datetime, date
import parsedatetime as pdt
import time
import json,re

def extract_information(line):
    file_name = 'tmp' + str(time.time()) + '.txt'
            
    nltk_tagger.taggerFunc(file_name, line)
    slots = label_marker.crf_labeling(file_name)
    tagged_data=input_processor.process_input(slots)        
    return tagged_data

def analyze_input(line):
    info = extract_information(line)
    return info 

def identify_intent(message):
    
    info = analyze_input(message)
    
    #print info
    return info
  
       
    


    
