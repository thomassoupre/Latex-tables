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
        parser.add_argument('-t','--truncate', metavar='T', type=int, nargs='?',const = 0,
                    help='truncate to T values after the decimal point, by default automatic formating to minimal number of zeros')

        self.args = parser.parse_args()
        with open(self.args.filename[0],'r') as f:
            self.data = [line.strip().replace('\t',' ').split() for line in f.readlines()]
        self.currentTex ="\\begin{table}[H]\n\\begin{center}"
        self.nc = len(self.data[0])
        self.nbc = self.nc-1 if self.args.columns is None else self.args.columns[0]
        self.formatData()
        # self.constructGraph()
        # self.generateLatex()
        self.constructGraph2()
        # print self.graph
        self.generateLatex2()
        with open(self.args.filename[0]+"_table.txt",'w') as f:
            f.write(self.currentTex)
        print self.nbc

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

    def constructGraph2(self):
        def constructNode(lines,c,maxv):
            if c>=maxv:
                return (lines,len(lines))
            reval=defaultdict(list)
            for line in lines:
                reval[line[0]].append(line[1:])
            cs = 0
            for line,revalLine in reval.iteritems():
                reval[line] = constructNode(revalLine,c+1,maxv)
                cs+=reval[line][1]
            return (reval,cs)
        self.graph = defaultdict(list)
        for d in self.data[1:]:
            self.graph[d[0]].append(d[1:])
        cs = 0
        for k,form in self.graph.iteritems():
            self.graph[k]=constructNode(form,1,self.nbc)
            cs += self.graph[k][1]
            # print self.graph[k]
        self.graph = (self.graph,cs)

    def formatData(self):
        def formatColumn(dat,col,truncate):
            if truncate < 1: #change this to 0
                nbMaxDec = max('{0:g}'.format(float(val))[::-1].find('.') for val in (line[col] for line in dat))
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
        # print self.data

    def generateLatex(self):
        hlines = [1 for _ in xrange(len(self.data))]
        def handleNode(node,c0,i0,mat,nbColMultiRow):
            firstspacer = ' & ' if c0>0 else ''
            if node and isinstance(node,list):
                for c,val in zip(range(c0+1,len(mat[0])),node[0][1:]):
                    mat[i0][c]= ' & '+val
                print i0,c0 , 'low recursion' 
                mat[i0][c0]= firstspacer+node[0][0]
            else:
                cursum = i0
                # print'node', node
                for key,val in node.iteritems():
                    print i0,c0
                    if len(val) > 1:
                        mat[cursum][c0] = '%s\\multirow{%d}{*}{%s}'%(firstspacer,len(val),key)
                        nbColMultiRow = max(c0,nbColMultiRow)
                        print 'HI HERE ',nbColMultiRow,c0
                    else:
                        mat[cursum][c0] = '%s%s'%(firstspacer,key)
                    hlines[cursum] = max(hlines[cursum],c0+1)
                    # print 'HEREEEEEEEEEEEEE',c0,hlines[cursum]
                    
                    spacer = (len(mat[cursum][c0]))*' '
                    # print 'a%sa'%spacer
                    for i in range(1,len(val)):
                        # print 'here ',cursum+i-1
                        mat[cursum+i][c0] = firstspacer+spacer+'PLACEHOLDER'
                        hlines[cursum+i] = max(hlines[cursum+i],c0+2)
                    # print key,val
                    # print c0+1,cursum
                    print 'HHANDLE %d'%handleNode(val,c0+1,cursum,mat,nbColMultiRow)
                    # nbColMultiRow = max(nbColMultiRow,handleNode(val,c0+1,cursum,mat,nbColMultiRow))
                    cursum += len(val)
            return nbColMultiRow
        def placeClines(mat):
            for i,line in enumerate(mat):
                tmp = 0
                while 'PLACEHOLDER' in line[tmp]:
                    mat[i][tmp] = mat[i][tmp].replace('PLACEHOLDER','')
                    tmp+=1
                mat[i][0] =  '\\cline{%d-%d}%s'%(tmp+1,len(line),line[0])
                mat[i][-1] += '\\\\' 
                # for x in line:
                #     print 'PLACEHOLDER' in x,i
                # print mat[i].index(next((x for x in line if 'PLACEHOLDER' in x),line[0]))+1
        #create matrix
        mat = [[str() for _ in xrange(len(self.data[0]))] for _ in xrange(len(self.data)-1)]
        self.nbColMultiRow = handleNode(self.graph,0,0,mat,0)+1
        print 'NBMIUL',self.nbColMultiRow
        tmp = '\n\\begin{tabular}{'+'|c'*self.nbColMultiRow+'||'+'r|'*(len(self.data[0])-self.nbColMultiRow+1)+'}'
        # print mat
        # print hlines
        placeClines(mat)
        # print mat
        # print '\n'.join(''.join(l) for l in mat)+'\\hline'
        self.currentTex += tmp+'\n'+'\n'.join(''.join(l) for l in mat)+'\\hline'
        self.currentTex += "\n\\end{tabular}\n\\end{center}\n\\caption{CAPTION}\n\\label{tab:tab1}\n\\end{table}\n"

        print self.currentTex

    def generateLatex2(self):
        hlines = [1 for _ in xrange(len(self.data))]
        def handleNode(node,c0,i0,mat,nbColMultiRow):
            print node
            firstspacer = ' & ' if c0>0 else ''
            if node[0] and isinstance(node[0],list):
                node = node[0]
                for i,no in enumerate(node):
                    for c,val in zip(range(c0+1,len(mat[0])),no[1:]):
                        mat[i+i0][c]= ' & '+val
                    print i0,c0 , 'low recursion' 
                    mat[i+i0][c0]= firstspacer+no[0]
            else:
                cursum = i0
                print'NODEEEEEE', node
                print type(node)
                for key,val in node[0].iteritems():
                    print i0,c0
                    print key,val
                    val,lenval=val
                    if lenval > 1:
                        mat[cursum][c0] = '%s\\multirow{%d}{*}{%s}'%(firstspacer,lenval,key)
                        nbColMultiRow = max(c0,nbColMultiRow)
                        # print 'HI HERE ',nbColMultiRow,c0
                    else:
                        mat[cursum][c0] = '%s%s'%(firstspacer,key)
                    hlines[cursum] = max(hlines[cursum],c0+1)
                    # print 'HEREEEEEEEEEEEEE',c0,hlines[cursum]
                    
                    spacer = (len(mat[cursum][c0]))*' '
                    # print 'a%sa'%spacer
                    for i in range(1,lenval):
                        # print 'here ',cursum+i-1
                        mat[cursum+i][c0] = firstspacer+spacer+'PLACEHOLDER'
                        hlines[cursum+i] = max(hlines[cursum+i],c0+2) #REMOVE ME
                    # print key,val
                    # print c0+1,cursum
                    print 'HHANDLE %d'%handleNode((val,lenval),c0+1,cursum,mat,nbColMultiRow)
                    # nbColMultiRow = max(nbColMultiRow,handleNode(val,c0+1,cursum,mat,nbColMultiRow))
                    cursum += lenval
            return nbColMultiRow

        def placeClines(mat):
            for i,line in enumerate(mat):
                tmp = 0
                while 'PLACEHOLDER' in line[tmp]:
                    mat[i][tmp] = mat[i][tmp].replace('PLACEHOLDER','')
                    tmp+=1
                mat[i][0] =  '\\cline{%d-%d}%s'%(tmp+1,len(line),line[0])
                mat[i][-1] += '\\\\' 

        #create matrix
        mat = [[str() for _ in xrange(len(self.data[0]))] for _ in xrange(len(self.data)-1)]

        self.nbColMultiRow = handleNode(self.graph,0,0,mat,0)+1

        print 'NBMIUL',self.nbColMultiRow

        placeClines(mat)
        tmp = '\n\\begin{tabular}{'+'|c'*self.nbColMultiRow+'||'+'r|'*(len(self.data[0])-self.nbColMultiRow+1)+'}'
        self.currentTex += tmp+'\n\\hline '+' & '.join(self.data[0])+'\\\\\n'+'\n'.join(''.join(l) for l in mat)+'\\hline'
        self.currentTex += "\n\\end{tabular}\n\\end{center}\n\\caption{CAPTION}\n\\label{tab:tab1}\n\\end{table}\n"

        print self.currentTex

        # self.formatColumn(self.data[1:],1)
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
\\end{tabular}\n\\end{center}\n\\caption{Temps d’exécution moyen pour 7 instances aléatoires en fonction de la taille de l'instance}\n\\label{tab:tab2}\n\\end{adjustwidth}\n\\end{table}\n
"""
if __name__ == '__main__':
    Table(sys.argv)
