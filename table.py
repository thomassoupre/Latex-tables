# -*- coding: utf-8 -*-
# Author: Thomas Soupre

import argparse
import sys
from collections import defaultdict

class Table(object):
    """Object for generating LaTeX tables using multirow as needed/asked from a raw data format"""

    def __init__(self, args):

        parser = argparse.ArgumentParser(description='Generating Latex multirow from file',
            epilog="don't forget to \\usepackage{multirow}")
        parser.add_argument('filename', metavar='path', type=str, nargs=1,
                            help='path to data')
        parser.add_argument('-c','--columns', metavar='N', type=int, nargs=1,
                    help='range of columns which you want to make multirows')
        parser.add_argument('-t','--truncate', metavar='T', type=int, nargs='?',const = -1,
                    help='truncate to T values after the decimal point, by default automatic formating to minimal number of zeros')
        parser.add_argument('-s','--save', metavar='savePath', type=str, nargs=1,
                    help='to save the table in a file at savePath, turns the program silent')

        self.args = parser.parse_args()
        with open(self.args.filename[0],'r') as f:
            self.data = [line.strip().replace('\t',' ').split() for line in f.readlines()] # getting data from file
        self.nbc = len(self.data[0])-1 if self.args.columns is None else min(self.args.columns[0],len(self.data[0])-1) # number of column where we should look for mulrirow
        if self.args.truncate is not None:
            self.formatData() # trucates floats
        self.constructGraph() # contruction of the graph of data
        self.generateLatex() # generate LaTeX code from graph
        if self.args.save is not None: # save table
            with open(self.args.save[0],'w') as f:
                f.write(self.latex)
            print "LaTeX code is in %s"%self.args.save[0]
        else:
            print self.latex

    def constructGraph(self):
        """
            Creates a graph from the data up to the wanted number of columns
        """
        if self.nbc == 0:
            self.graph = (self.data[1:],len(self.data)-1)
            return
        graphAndNbOfLeaves = lambda x : (x,sum(l for o,l in x.itervalues())) # returns a tuple of the graph and the nb of leaves
        def constructNode(lines,c,maxv):
            """
                Recursive fonction creating a node of the graph
            """
            if c>=maxv:
                return (lines,len(lines))
            reval=defaultdict(list)
            for line in lines:
                reval[line[0]].append(line[1:]) # creating the leaves
            return graphAndNbOfLeaves({line:constructNode(revalLine,c+1,maxv) for line,revalLine in reval.iteritems()})
        self.graph = defaultdict(list)
        for d in self.data[1:]:
            self.graph[d[0]].append(d[1:]) # creating the first sons
        self.graph = graphAndNbOfLeaves({k:constructNode(form,1,self.nbc) for k,form in self.graph.iteritems()})

    def formatData(self):
        """
            format floats to minimal or wanted values after zeros
        """
        def formatColumn(dat,col,truncate):
            if truncate < 0: # Automatic truncate
                nbMaxDec = max('{0:g}'.format(float(val))[::-1].find('.') for val in (line[col] for line in dat)) # getting needed zeros for truncating
                form =  '{:.%df}'%max(0,nbMaxDec)
                for i in xrange(len(dat)):
                    dat[i][col] = form.format(float(dat[i][col]))
            else:
                form =  '{:.%df}'%truncate
                for i in xrange(len(dat)):
                    dat[i][col] = form.format(float(dat[i][col]))
        for i,val in enumerate(self.data[1]):
            try:
                formatColumn(self.data[1:],i,self.args.truncate)
            except Exception as e:
                continue

    def generateLatex(self):
        """
            generating latex table from graph of data
        """
        def handleNode(node,c0,i0,mat,nbColMultiRow):
            firstspacer = ' & ' if c0>0 else '' # should be optimized
            if node[0] and isinstance(node[0],list): # if leaf of graph treat as line of values
                for i,no in enumerate(node[0]):
                    for c,val in zip(range(c0+1,len(mat[0])),no[1:]):
                        mat[i+i0][c]= ' & '+val
                    mat[i+i0][c0]= firstspacer+no[0]
            else:
                cursum = i0
                for key,val in node[0].iteritems(): # iterating over sons
                    val,lenval = val # simplicating futher use of val
                    if lenval > 1:
                        mat[cursum][c0] = '%s\\multirow{%d}{*}{%s}'%(firstspacer,lenval,key)
                        nbColMultiRow = max(c0,nbColMultiRow) # knowing automatic max number of multirows
                    else:
                        mat[cursum][c0] = '{}{}'.format(firstspacer,key)
                    
                    spacer = (len(mat[cursum][c0]))*' '
                    for i in range(1,lenval):
                        mat[cursum+i][c0] = firstspacer+spacer+'PLACEHOLDER' # place holder for future indentation. to be fixed
                    nbColMultiRow = max(nbColMultiRow,handleNode((val,lenval),c0+1,cursum,mat,nbColMultiRow))
                    cursum += lenval
            return nbColMultiRow

        def placeClines(mat):
            """
                placing lines of table acording to placeholders
            """
            for i,line in enumerate(mat):
                tmp = 0
                while 'PLACEHOLDER' in line[tmp]:
                    mat[i][tmp] = mat[i][tmp].replace('PLACEHOLDER','')
                    tmp+=1
                mat[i][0] = '\\cline{%d-%d}%s'%(tmp+1,len(line),line[0])
                mat[i][-1] += '\\\\' 

        mat = [[str() for _ in xrange(len(self.data[0]))] for _ in xrange(len(self.data)-1)]
        self.nbColMultiRow = handleNode(self.graph,0,0,mat,0)+1
        placeClines(mat)
        # creating LaTeX code
        self.latex = '\\begin{table}[H]\n\\begin{center}\n\\begin{tabular}{'+'|c'*self.nbColMultiRow+'||'+'r|'*(len(self.data[0])-self.nbColMultiRow+1)+'}\n\\hline '+' & '.join(self.data[0])+'\\\\\n'+'\n'.join(''.join(l) for l in mat)+"\\hline\n\\end{tabular}\n\\end{center}\n\\caption{CAPTION}\n\\label{tab:tab1}\n\\end{table}\n"

if __name__ == '__main__':
    Table(sys.argv)
