# -*- coding: utf-8 -*-
"""
@authors: Giannis Kazakos, Nikolas Lianos, Eridanous Loulas
"""
from block import Block



class Blockchain:
    
    def __init__(self):
        
        self.chain = []
        self.difficulty = 4
        self.capacity = 3
        self.pendingTransactions = []
        self.Hash_set = set()
    
     
    def add_block(self, block):
        self.Hash_set.add(block.currentHash)
        self.chain.append(block)
   
    def add_transaction(self, transaction):
        self.pendingTransactions.append(transaction)
    
    def getLatestBlock(self):
        return( self.chain[ len(self.chain) - 1 ] )
        
        
    def minePendingTransactions(self):
        index = len(self.chain)
        if len(self.pendingTransactions) >= self.capacity:
            block = Block(index,self.pendingTransactions[0:self.capacity],self.getLatestBlock().currentHash)
            self.pendingTransactions = self.pendingTransactions[self.capacity:]
            block.mine(self.difficulty)
            if block.previousHash == self.getLatestBlock().currentHash:
                self.add_block(block)
                return(True)
            else:
                return(False)
        else:
            return(False)
            
        
    def __str__(self):
        msg = ""
        for s in self.chain:
            msg = msg + "{}\n\n".format(str(s))
        return(msg)