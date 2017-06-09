from sys import argv
import re
from processor import intent_identifier
from pythonds.basic.stack import Stack
import os
from os import walk

script, inputdir, outputdir = argv

keywords = open('oracle_keywords.txt').read().replace("\n", "|").strip()

keywords_newline = open('oracle_keywords_newline.txt').read().replace("\n", "|").strip()





def getOrderExp(input, key):
       out = ''
       for  index,value in input.iteritems():
        if index > key+1:
            out+= input[index]['value']+" "
       return out



operators = ["INTERVAL", "BINARY", "COLLATE", "!", "-", "~", "\\^", "\\* ", "/", "DIV", "%", "MOD", "\\+", "<<", ">>", "&", "=", "<=>", ">=", ">", "<=", "<", "<>", "!=", "IS", "LIKE", "REGEXP", "IN", "BETWEEN", "CASE", "WHEN", "THEN", "ELSE", "NOT", "AND", "&&", "XOR", "OR", ":="]
def evalmongoops(left, right, operator):
    operator = operator.strip()
    if operator == '=':
        return left +':'+right
    elif operator == '!=':
        return left +':{$ne:'+right +"}"
    elif operator == '>':
        return left +':{$gt:'+right +"}" 
    elif operator == '>=':
        return left +':{$gte:'+right +"}"   
    elif operator == '<':
        return left +':{$lt:'+right +"}" 
    elif operator == '<=':
        return left +':{$lte:'+right +"}"  
    elif operator == 'IN':
        return left +':{$in:['+right[1:-1] +"]}"     
    #elif operator == 'LIKE':
     #   return left +':{$lte:'+right +"}"            
    elif operator == 'AND':
        return '$and:[{'+ left + '},{' + right+ '}]'
    elif operator == 'OR':    
        return '$or:[{'+ left + '},{' + right+ '}]'  

def evalPostfix(expression):
    
    opStack = Stack()
    for i in expression:
        if i not in operators:
            opStack.push(i)
        else:
            if(not opStack.isEmpty()):
                right = opStack.pop()
            if(not opStack.isEmpty()):    
                left = opStack.pop() 
            opStack.push(evalmongoops(left,right,i)) 
        #print opStack.peek()  
    return opStack.pop()       

def infixToPostfix(infixexpr):
    
    prec = {}
    prec["!"] = 16
   # prec["-"] = 15
    prec["~"] = 15
    prec["^"] = 14
    prec["%"] = 13
    prec["/"] = 13
    prec["*"] = 13
    prec["-"] = 12
    prec["+"] = 12
    prec["<<"] = 11
    prec[">>"] = 11
    prec["&"] = 10
    prec["|"] = 9
    prec["="] = 8
    prec["<=>"] = 8
    prec[">="] = 8
    prec[">"] = 8
    prec["<="] = 8
    prec["<"] = 8
    prec["<>"] = 8
    prec["!="] = 8
    prec["IS"] = 8
    prec["LIKE"] = 8
    prec["REGEXP"] = 8
    prec["IN"] = 8
    prec["BETWEEN"] = 7
    prec["CASE"] = 7
    prec["WHEN"] = 7
    prec["THEN"] = 7
    prec["ELSE"] = 7
    prec["NOT"] = 6
    prec["AND"] = 5
    prec["&&"] = 5
    prec["XOR"] = 4
    prec["||"] = 3
    prec["OR"] = 3
    prec[":="] = 2
    prec["("] = 1
    opStack = Stack()
    postfixList = []
    opl = ""
    for op in operators:
        opl+=op+'|'
    opl= opl[:-1]
    
    tokenList = infixexpr.split(" ")
    varList = re.split(opl,infixexpr)
    for index,var  in enumerate(varList):
        varList[index]= var.strip()

    
    for token in tokenList:
        
        #print token
        if token in varList:
            postfixList.append(token)
        elif token == '(':
            opStack.push(token)
        elif token == ')':
            topToken = opStack.pop()
            while topToken != '(':
                postfixList.append(topToken)
                topToken = opStack.pop()
        elif token in operators:
            while (not opStack.isEmpty()) and \
               (prec[opStack.peek()] >= prec[token]):
                  postfixList.append(opStack.pop())
            opStack.push(token)

    while not opStack.isEmpty():
        postfixList.append(opStack.pop())
    return postfixList

#print(evalPostfix(infixToPostfix("SALES IN (a,b)")))
#print(infixToPostfix("( Ajkhjkh + Bkjjkjkhjhkkhjk ) * uiuitC - ( Duiuiiyit - Esyuruy ) * ( ioioioF + Gpoioppi )"))





def mergelines(text):
                text = text.replace('\n',' ').replace(' ','  ')
                return '  ' + text
                
def upper_repl(match):
     return match.group(1) + match.group(2).upper() + match.group(3)
                
def newline_upper_repl(match):
     return '\n' + match.group(1) + match.group(2).upper()  + match.group(3)
                
def indentkeywords(text):
                replaced = re.sub('(\s?)('+keywords+')(;|\s+|\()', upper_repl, text, flags=re.I)
                return replaced 
                
def prependnewline(text):
                replaced = re.sub('( ?)('+keywords_newline+')(\s+|\(|;)', newline_upper_repl, text, flags=re.I)
                return replaced 
                
def removelinecomments(text):
                replaced = re.sub('--.*\n', '\n', text)
                return replaced
                
                
def removeblockcomments(text):           
                replaced = re.sub('/\*.*\*/', '', text)
                return replaced

def parseinsertstmt(input):
                table_name = ''
                values = []
                columns = []
                #print input
                for key,value in input.iteritems():
                    intent_val = value['intent']
                    val = value['value']
                    if intent_val in ['table_name','aggregate']:
                        table_name=val
                    elif intent_val in ['variable','aggregate_variable']:
                        columns.append(val)
                    elif intent_val in ['insert_col_val']:
                        values.append(val)  
                js='db.'+ table_name + '.insertOne({'    
                for index,val in enumerate(columns):
                    js+=val+' : ' + values[index] + ","
                js = js[:-1]+"})"
                return js

def parsedeletestmt(input):
                js = ''
                isWherePresent = 0
                whereExpression = ''
                tables=[]
                #print input
                for key,value in input.iteritems():
                    intent_val = value['intent']
                    val = value['value']
                    if intent_val in ['where_expression']:  
                        isWherePresent = 1 
                        whereExpression+=val+ " "
                    elif intent_val in ['table_name']:  
                        tables.append(val)  
                js_where = ''                
                if isWherePresent != 0:
                    #print whereExpression         
                    js_where = '{' + evalPostfix(infixToPostfix(whereExpression)) + '}'  
                else:
                    js_where = '{}'  

                js='db.' + tables[0] + '.deleteMany('+js_where+')'
                return js  

def parsedropstmt(input):
                js = ''
                tables=[]
                #print input
                for key,value in input.iteritems():
                    intent_val = value['intent']
                    val = value['value']
                    if intent_val in ['table_name']:  
                        tables.append(val)  

                js='db.' + tables[0] + '.drop()'
                return js  


def parseselectstmt(input):
                js = ''
                isAggregate = 0
                isSelectVarList = 0
                select_vars =[]
                isWherePresent = 0
                whereExpression = ''
                isOrderByPresent = 0
                isGroupByPresent = 0
                orderExpression =''
                js_order = ''
                tables=[]
                #print input
                for key,value in input.iteritems():
                                                intent_val = value['intent']
                                                val = value['value']
                                                if intent_val in ['aggregate', 'group' , 'having']:
                                                    isAggregate = 1
                                                elif intent_val in ['variable']:  
                                                    isSelectVarList = 1
                                                    select_vars.append(val) 
                                                elif intent_val in ['where_expression']:  
                                                    isWherePresent = 1 
                                                    whereExpression+=val+ " "
                                                elif intent_val in ['order']:  
                                                    isOrderByPresent = 1
                                                    orderExpression = getOrderExp(input, key)  
                                                elif intent_val in ['group']:  
                                                    isGroupByPresent = 1  
                                                elif intent_val in ['table_name']:  
                                                    tables.append(val)                  
                if isOrderByPresent== 1:
                        js_order = ".sort("
                        order_var = orderExpression.split(',')
                        for item in order_var:
                            col =''
                            item = item.strip()
                            if item[-5:] == " DESC" or item[-5:] ==" desc":
                                col = '{'+item[:-5] +':-1 }'
                            elif item[-4:]==" ASC" or item[-4:]==" asc":
                                col = '{'+item[:-4] +':1 }'
                            else:
                                col = '{'+item +':1 }'
                            js_order+= col+','
                        js_order = js_order[:-1]+')'

                js_select = '{'                
                if isSelectVarList == 1:         
                                for l in select_vars:
                                    js_select+=  l + ": 1,"
                                js_select=    js_select[:-1] +'}'
                                #print js_select
                js_where = ''                
                if isWherePresent != 0:
                    #print whereExpression         
                    js_where = '{' + evalPostfix(infixToPostfix(whereExpression)) + '}'  
                else:
                    js_where = '{}'    


                if isAggregate == 1:         
                                js = 'db..aggregate([])'

                else:
                                 
                                js = 'db.' + tables[0] + '.find(' + js_where
                                if isSelectVarList == 1:
                                    js+=','+js_select
                                js+=')'+js_order   

                #print js
                return js
                                                
                                                                                

def createjs(array):
    final =''
    for line in array:
        print line
        temp = ''
        for keyword in line:
                                
                                if line[keyword]['intent'] == 'create_procedure':
                                   temp+='function '
                                elif line[keyword]['intent'] == 'proc_name':
                                  temp+=line[keyword]['value']+'()'
                                elif line[keyword]['intent'] == 'proc_param':
                                   if temp[-2]== '(':
                                                temp=temp[:-1] + line[keyword]['value']+ ')'   
                                   else:
                                                temp=temp[:-1] + ', ' + line[keyword]['value']+ ')'  
                                elif line[keyword]['intent'] == 'begin':
                                   temp+='{\n'                    
                                elif line[keyword]['intent'] == 'end':
                                   temp+='\n}\n'                                   
                                elif line[keyword]['intent'] == 'select_data':
                                  temp+= parseselectstmt(line)
                                elif line[keyword]['intent'] == 'insert':
                                  temp+= parseinsertstmt(line)   
                                elif line[keyword]['intent'] == 'delete_data':
                                  temp+= parsedeletestmt(line)
                                elif line[keyword]['intent'] == 'drop_table':
                                  temp+= parsedropstmt(line)
                                                 
                                # elif line[keyword]['intent'] == 'variable':
                                #    if temp[-3:]== '{})':
                                #                 temp=temp[:-1] +  ',{' +line[keyword]['value']  + ':1' + '})'   
                                #    else:
                                #                 temp=temp[:-2] + ', ' + line[keyword]['value'] + ':1' + temp[-2:]
                                # elif line[keyword]['intent'] == 'table_name':
                                #    temp=temp[:3] + line[keyword]['value'] + temp[3:]   
        final += temp+'\n'
    print final
    return final

files = []
for (dirpath, dirnames, filenames) in walk(inputdir):
    files.extend(filenames)

print files
for filename in files:
    f = open(os.path.join(inputdir,filename))
    outputfile = open(os.path.join(outputdir,filename),"w") 

    text = f.read()
    text = removelinecomments(text)          
    text = mergelines(text)
    text = removeblockcomments(text)
    text = indentkeywords(text)
    text = prependnewline(text)

                    

    a = text.split('\n')

    #print a
    b = []
    for l in a :
                    b.append(intent_identifier.identify_intent(l))

    outputfile.write(createjs(b))
    outputfile.close()
    #print b
    



