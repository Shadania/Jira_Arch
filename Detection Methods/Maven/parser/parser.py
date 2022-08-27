import csv
import sys
import getopt
import nltk, re, string, collections
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt 
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from itertools import combinations
from collections import Counter
from scipy.stats import chi2_contingency
from nltk import *

# The dictionary with the list of documents
issues = {}
sentences = {}

# Store word counts (keywords)
word_count = {}
lemmatizer = WordNetLemmatizer()

# Filter for unimportant words
word_filter = set(stopwords.words('english'))
word_filter.update({
    ".",",","I","'","(",")",":","<",">","``","’","''","?","..","We","[",
    "]","|","$","=","The","{","}","*","It","-",";","+","~","#","A","7",
    "8","1","@","&","%","71","39","45","In","2","This","main/","na",
    "na:1.8.0_111","3.0"
})

def printWordCountBoxPlot():
    uniqueValues = list(sentences.keys())
    counter = 0
    matrix = []
    xaxis = []

    # design decision rationale
    matrix.append(sentences["Risks"])
    xaxis.append("Risks")
    matrix.append(sentences["Trade-offs"])
    xaxis.append("Trade-offs")
    matrix.append(sentences["Assumptions"])
    xaxis.append("Assumptions")
    matrix.append(sentences["Architectural solution benefits and drawbacks"])
    xaxis.append("Architectural solution benefits and drawbacks")

    # architectural solution
    matrix.append(sentences["Technology solution"])
    xaxis.append("Technology solution")
    matrix.append(sentences["Architectural tactics"])
    xaxis.append("Architectural tactics")
    matrix.append(sentences["Architectural design configuration"])
    xaxis.append("Architectural design configuration")
    matrix.append(sentences["Architectural component behavior and structure"])
    xaxis.append("Architectural component behavior and structure")
    matrix.append(sentences["Other system architectural solutions"])
    xaxis.append("Other system architectural solutions")

    # design issue
    matrix.append(sentences["Contextual constraints"])
    xaxis.append("Contextual constraints")
    matrix.append(sentences["Run-time quality issues"])
    xaxis.append("Run-time quality issues")
    matrix.append(sentences["Technical debt"])
    xaxis.append("Technical debt")
    matrix.append(sentences["Existing system architecture description"])
    xaxis.append("Existing system architecture description")
    if "Quality Attribute requirement" in sentences:
        matrix.append(sentences["Quality Attribute requirement"])
        xaxis.append("Quality Attribute requirement")
    matrix.append(sentences["User requirement"])
    xaxis.append("User requirement")
    matrix.append(sentences["Motivation of design issue"])
    xaxis.append("Motivation of design issue")
        
    mpl.use('agg')
    
    # Create a figure instance
    fig = plt.figure(1, figsize=(9, 6))

    # Create an axes instance
    ax = fig.add_subplot(111)

    # Create the boxplot
    bp = ax.boxplot(matrix, showfliers=False, patch_artist=True, vert=False)

    ax.set_yticklabels(xaxis)
    
    for median in bp['medians']:
        median.set(color='#000000', linewidth=2)


    for box in bp['boxes']:
        # change fill color
        box.set( facecolor = '#D3D3D3' )

    # Save the figure
    fig.savefig('fig1.png', bbox_inches='tight')

# write keywords to output file
def writeKeywords():
    keywordFile = open("keywords.txt", "w")
    for key in sorted(word_count):
        fdist = FreqDist(word_count[key])
        keywordFile.write(key + '\n')
        for item in fdist.most_common():
            keywordFile.write(item[0] + ", " + str(item[1]) + '\n')
            # use for LaTeX table
            # keywordFile.write(item[0] + " & " + str(item[1]) + " \\\\\\hline\n")
        keywordFile.write('\n')
    
def countSentPure(sent): 
    word_tokens = word_tokenize(sent)  
    filtered_sentence = [w for w in word_tokens if not w in word_filter]    
    return len(list(filtered_sentence))
  

# Prints the split groups of annotations
def printIssues():
    for issue in issues:
        print("File: ", issue)
        for index, annotation in enumerate(issues[issue]["groups"]):
            if index == 0:
                print("Summary and description:")
            else:
                print("Username:", issues[issue]["owners"][index])
            print(annotation, "\n")

# Calculate the ngram for this string
def printNgrams(inputStr,section):
    tokenized = inputStr.split()
    bigrams = ngrams(tokenized,2)
    bigramsFreq = collections.Counter(bigrams)
    trigrams = ngrams(tokenized,3)
    trigramsFreq = collections.Counter(trigrams)
    fourgrams = ngrams(tokenized,4)
    fourgramsFreq = collections.Counter(fourgrams)
    fivegrams = ngrams(tokenized,5)
    fivegramsFreq = collections.Counter(fivegrams)     
    writengrams(bigramsFreq.most_common(100), section + "_bigrams.csv")
    writengrams(trigramsFreq.most_common(100), section + "_trigrams.csv")
    writengrams(fourgramsFreq.most_common(100), section + "_fourgrams.csv")
    writengrams(fivegramsFreq.most_common(100), section + "_fivegrams.csv")

def writengrams(ngrams,csvfile):
    with open(csvfile, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in ngrams:
            writer.writerow([key, value])

def createCoocurenceMatrix(sentences):
    vocab = set(word_tokenize(' '.join(sentences)))
    print('Vocabulary:\n',vocab,'\n')
    token_sent_list = [word_tokenize(sen) for sen in sentences]
    print('Each sentence in token form:\n',token_sent_list,'\n')

    co_occ = {ii:Counter({jj:0 for jj in vocab if jj!=ii}) for ii in vocab}

    for sen in token_sent_list:
        for ii in range(len(sen)):
            k = len(sen)
            if ii < k:
                c = Counter(sen[0:ii+k+1])
                del c[sen[ii]]
                co_occ[sen[ii]] = co_occ[sen[ii]] + c
            elif ii > len(sen)-(k+1):
                c = Counter(sen[ii-k::])
                del c[sen[ii]]
                co_occ[sen[ii]] = co_occ[sen[ii]] + c
            else:
                c = Counter(sen[ii-k:ii+k+1])
                del c[sen[ii]]
                co_occ[sen[ii]] = co_occ[sen[ii]] + c

    # Having final matrix in dict form lets you convert it to different python data structures
    co_occ = {ii:dict(co_occ[ii]) for ii in vocab}
    return co_occ
    #print(co_occ)

def writeCoocc(co_occ,csv_file):
    uniqueValues = list(co_occ.keys())
    csv_columns = list(co_occ.keys())
    csv_columns.insert(0,"")
    matrix = {}
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_columns)
            #for key, value in co_occ.items():
            for key in uniqueValues:
                row = [key]
                matrix[key] = {}
                for con in uniqueValues:
                    if con in co_occ[key]:
                        row.append(co_occ[key][con])
                        matrix[key][con] = co_occ[key][con]
                    else:
                        row.append(0)
                        matrix[key][con] = 0
                writer.writerow(row)
                #print(matrix[key].values())
    except IOError:
        print("I/O error")
    return matrix,uniqueValues

# Capture sequences of codes
def getSequences():
    # variables to calculate ngram
    desc = ""
    comments = ""
    commentsWithUsers = ""
    counter = 0
    
    # variables to calculate coocurences
    descList = []
    commentsList = []
    
    for issue in issues:
        usersdic = {}
        counter = 1
        print("File: ", issue)
        for index, annotation in enumerate(issues[issue]["groups"]):
            annotationStr = getCodeChain(annotation)
            if index == 0:              
                # Here create the sequences for the summary and description  
                desc = desc + " END " + annotationStr
                descList.append(annotationStr)
            else:
                
                comments = comments + " END " + annotationStr
                commentsList.append(annotationStr)
                if issues[issue]["owners"][index] in usersdic:
                    user = usersdic[issues[issue]["owners"][index]]
                else:
                    user = "user" + str(counter)
                    usersdic[issues[issue]["owners"][index]] = user
                    counter += 1
                commentsWithUsers = commentsWithUsers + " " + getCodeChainWithUser(annotation,user)
    
    createAndWriteCoocurence(commentsList,descList)
    printNgrams(desc,"description")
    printNgrams(comments,"comments")
    printNgrams(commentsWithUsers,"commentsWithUsers")


# The method creates and write the coocurence matrix and its chi square 
def createAndWriteCoocurence(commentsList,descList):
    co_occComm = createCoocurenceMatrix(commentsList)
    matrix, concepts = writeCoocc(co_occComm,"Cooc_comments.csv")
    chimatrix = calculateChiSquare(matrix,concepts)
    writeChiMatrix(chimatrix, concepts, "Cooc_comments_chisquare.csv")
    co_occComm = createCoocurenceMatrix(descList)
    matrix, concepts = writeCoocc(co_occComm,"Cooc_desc.csv")
    chimatrix = calculateChiSquare(matrix,concepts)
    writeChiMatrix(chimatrix, concepts, "Cooc_desc_chisquare.csv")

def calculateChiSquare(dic,concepts):
    matrix = np.array(pd.DataFrame.from_dict(dic))
    print (matrix)
    length = len(list(concepts))
    chimatrix = np.zeros((length,length))
    row = 0
    column = 0
    while row < length:
        while column < length:
            contig = np.zeros((2,2))
            contig[0,0] = matrix[row,column]
            contig[0,1] = np.sum(matrix[row,:]) - contig[0,0]
            contig[1,0] = np.sum(matrix[:,column]) - contig[0,0]
            contig[1,1] = np.sum(matrix) - contig[0,1] - contig[1,0] + contig[0,0]
            
            if np.sum(contig[0,:]) == 0 or np.sum(contig[1,:]) == 0 or np.sum(contig[:,0]) == 0 or np.sum(contig[:,1]) == 0:
                chimatrix[row,column] = 0
                column += 1
                continue
            
            print("row: " + str(row) + " column: " + str(column))
            print(contig)
            c, p, dof, expected = chi2_contingency(contig)
            chimatrix[row,column] = round(c,4)
            
            column += 1
        column = 0
        row += 1
    return chimatrix
    

def writeChiMatrix(chimatrix, concepts, csv_file):
    try:
        with open(csv_file, 'w') as csvfile:
            csv_columns = list(concepts)
            csv_columns.insert(0,"")
            writer = csv.writer(csvfile)
            writer.writerow(csv_columns)
            conceptslist = list(concepts)
            length = len(conceptslist) 
            row = 0
            while row < length:
                chirow = chimatrix[row,:]
                chirowlist = chirow.tolist()
                chirowlist.insert(0,conceptslist[row])
                writer.writerow(chirowlist)
                row += 1
                #print(matrix[key].values())
    except IOError:
        print("I/O error")

def getCodeChainWithUser(annotation, user):
    codes = ""
    previousCode = ""
    for code in annotation:
        newCode = user + code.replace(" ", "")
        if newCode == previousCode:
            continue
        codes = codes +  " " + newCode
        previousCode = newCode
    return codes
    
# Transform an array of codes into a string
def getCodeChain(annotation):
    codes = ""
    for code in annotation:
        codes = codes +  " " + code.replace(" ", "")
    return codes


# Reads the input file and splits the groups of annotations
def readFile(file):

    # Name of the code used to split multiple annotations
    ANNOTATION_SPLIT_ID = "Comment"

    with open(file, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0

        for row in csv_reader:
            if count == 0:
                count += 1
            else:
                issueId = row[2]

                # Seperate groups of annotations per document
                # Each document has groups of annotations and each group has an owner. 
                # This is maintained by keeping to same size arrays.
                if issueId not in issues:
                    issues[issueId] = {
                        "groups": [[]],
                        "owners": ['']
                    }
                
                # Check if the current comment is indicating a split
                if row[5] != ANNOTATION_SPLIT_ID:

                    # Some annotations might have multiple codes
                    codes = row[5].splitlines()
                    for code in codes:  
                        if code.isspace():
                            continue
                        # Append code to the current group
                        issues[issueId]["groups"][-1].append(code)

                        if code not in sentences:
                            sentences[code] = []
                            word_count[code] = FreqDist()

                        sentences[code].append(countSentPure(row[3]))

                        word_tokens = word_tokenize(row[3])  
                        filtered_sentence = [w for w in word_tokens if not w in word_filter]
                        for word in filtered_sentence:
                            word_count[code][lemmatizer.lemmatize(word)] += 1
                else: 

                    # Add new group is new comment is found and the previous group is not empty
                    if (len(issues[issueId]["groups"][-1]) > 0):
                        issues[issueId]["groups"].append([])

                        # Strip username of whitespace and semicolon
                        owner = row[3]
                        owner = owner.replace(" ", "")
                        owner = owner.replace(":", "")

                        issues[issueId]["owners"].append(owner)

                count += 1


if __name__ == "__main__":
    inputfile = ''
    outputfile = ''

    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('parser.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('parser.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is "', inputfile)
    print('Output file is "', outputfile)

    readFile(inputfile)
    print(sentences)
    #printIssues()
    getSequences()
    printWordCountBoxPlot()
    writeKeywords()
