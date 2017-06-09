import commands
import subprocess
from sys import platform

COMMAND_PATH = "crf_test -m models/model_migrate "

def crf_labeling(file_name):
    global COMMAND_PATH
        
    if platform == "linux" or platform == "linux2":
	# For Linux
	slots = commands.getstatusoutput(COMMAND_PATH + file_name)
	slots = slots[1]
    elif platform == "win32":
	# For windows
	p = subprocess.Popen(COMMAND_PATH + file_name,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if err != "":
	    print "Error is",err
	slots = out
	slots = slots.replace('\r','')
    else:
	print "Invalid Platform"
	slots = ""
    slots = slots.split('\n')

    #DELETE GENERATED FILE
    delete_tagged_file(file_name)
    return slots

def delete_tagged_file(file_name):
    if platform == "linux" or platform == "linux2":
	# For Linux
	DELETE_FILE = 'rm ' + file_name
	delete_status = commands.getstatusoutput(DELETE_FILE)
    elif platform == "win32":
	# For windows
	DELETE_FILE = 'del /F ' + file_name
	p = subprocess.Popen(DELETE_FILE , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if err != "":
	    print "Error is", err
    else:
	print "Invalid Platform"    
