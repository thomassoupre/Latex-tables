# -*- coding: utf-8 -*-
# Author: Thomas Soupre

import argparse
import sys
from collections import defaultdict

class Table(object):
    """Table for Latex"""

    def __init__(self, args):

        parser = argparse.ArgumentParser(description='Generating Latex multirow from file',
            epilog="don't forget to \\usepackage{multirow}")
        parser.add_argument('filename', metavar='path', type=str, nargs=1,
                            help='path to data')
        parser.add_argument('-c','--columns', metavar='N', type=int, nargs=1,
                    help='range of columns which you want to make multirows')

        self.args = parser.parse_args()

        print self.args.filename
        with open(self.args.filename[0],'r') as f:
            self.data = [line.strip().replace('\t',' ').split() for line in f.readlines()]

        self.currentTex ="\\begin{table}[H]\n\\begin{center}"
        self.nc = len(self.data[0])
        print parser
        print self.data
        self.constructGraph()
        self.generateLatex()
        print self.graph

    def constructGraph(self):
        def constructNode(lines,c,maxv = 2):
            if c>=maxv:
                return lines
            reval=defaultdict(list)
            for line in lines:
                reval[line[0]].append(line[1:])
            for line,revalLine in reval.iteritems():
                reval[line] = constructNode(revalLine,c+1)
            return reval
        self.graph = defaultdict(list)
        for d in self.data[1:]:
            self.graph[d[0]].append(d[1:])
        for k,form in self.graph.iteritems():
            self.graph[k]=constructNode(form,1)

    def generateLatex(self):
        hlines = [1 for _ in xrange(len(self.data)+1)]
        def handleNode(node,c0,i0,mat):
            firstspacer = ' & ' if c0>0 else ''
            if node and isinstance(node,list):
                for c,val in zip(range(c0+1,len(mat[0])),node[0][1:]):
                    mat[i0][c]= ' & '+val
                print i0,c0 , 'low recursion' 
                mat[i0][c0]= firstspacer+node[0][0]
            else:
                cursum = i0
                print'node', node
                for key,val in node.iteritems():
                    print i0,c0
                    if len(val) > 1:
                        mat[cursum][c0] = '%s\\multirow{%d}{%s}'%(firstspacer,len(val),key)
                    else:
                        mat[cursum][c0] = '%s%s'%(firstspacer,key)
                    hlines[cursum] = max(hlines[cursum],c0+1)
                    print 'HEREEEEEEEEEEEEE',c0,hlines[cursum]
                    
                    spacer = (len(mat[cursum][c0]))*' '
                    print 'a%sa'%spacer
                    for i in range(1,len(val)):
                        print 'here ',cursum+i-1
                        mat[cursum+i][c0] = firstspacer+spacer
                        hlines[cursum+i] = max(hlines[cursum+i],c0+2)
                    print key,val
                    print c0+1,cursum
                    handleNode(val,c0+1,cursum,mat)
                    cursum += len(val)
        #create matrix
        mat = [[str() for _ in xrange(len(self.data[0]))] for _ in xrange(len(self.data))]
        handleNode(self.graph,0,0,mat)
        for l in mat:
            print ''.join(l)
        print mat
        print hlines
        #concatenate matrix
"""
    def calculateColumsNumber(self):
        self.nc = len(self.data[0])
        if self.args.columns:
            self.currentTex+='\n\\begin{tabular}{'+'|c'*self.columns[0]+'||'+'r|'*(nc-self.columns[0]+1)'|}'
        else:
            self.currentTex+='\n\\begin{tabular}{'+'|c'*self.columns[0]+'||'+'r|'*(nc-self.columns[0]+1)'}'

"""

"""

\begin{table}[H]
\begin{center}
\begin{tabular}{|c||r|r|}
\hline
taille & PI & MeanItPI\\
\cline{1-3}\multirow{1}{*}{(10,10)} & 0.176 & 14.00\\
\cline{1-3}\multirow{1}{*}{(10,15)} & 0.437 & 20.14\\
\cline{1-3}\multirow{1}{*}{(15,20)} & 1.486 & 19.43\\
\hline
\end{tabular}
\end{center}
\caption{Temps d’exécution moyen pour 7 instances aléatoires en fonction de la taille de l'instance}
\label{tab:tab2}
\end{adjustwidth}
\end{table}

"""
if __name__ == '__main__':
    Table(sys.argv)
