# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 19:40:26 2019

@author: Giannis Kazakos
"""

import requests
import json
from block import Block
from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
import jsonpickle


def getBalance(chain,address):

    balance = 0
    for block in chain:
        for trans in block.listOfTransactions:
            if trans['sender_address'] == address:
                balance -= trans['value']
            if trans['recipient_address'] == address:
                balance += trans['value']            
    return(balance)


print('Type the id of the node you want to access :')

node_id = input()
print('\n')

print('Type the action or "help" to see the supported commands  :')

cmd = input().split()
print('\n')

while cmd != 'exit':

    if cmd[0] == 't':
        
        # New transaction
        receiver = cmd[1]
        amount = cmd[2]
        r = requests.post('http://' +'127.0.0.1:500' + node_id + '/transactions/new', data = json.dumps(dict({'receiver':receiver,'amount':int(amount)})))
        print('\n')
        
    elif cmd[0] == 'view':
    
        # Get chain
        r = requests.get('http://' + '127.0.0.1:500' + node_id + '/chain').json()
        chain = jsonpickle.decode(r)  
        last_block = chain[-1].to_dict()
        transactions = last_block['Transactions']
        #['Transactions']
        print([dict(t) for t in transactions])
        print('\n')
        
    elif cmd[0] == 'balance':
        
        #Get node balance
        r = requests.get('http://' + '127.0.0.1:500' + node_id + '/chain').json()
        chain = jsonpickle.decode(r)  
        print(getBalance(chain,node_id))
        print('\n')
        
    elif cmd[0] == 'help':
        
        print('Supported commands : \n')
        print('"t <recipient address> <amount>": Send <amount> coins to node with address <reciepient address>\n')
        print('"view" : View the transactions of the last valid block of the blockchain\n')
        print('"balance" : View the balance of the current node\n')
        print('"exit" : Exit \n')
        print('\n')
    
    elif cmd[0] == 'exit':
         
        break

    else :
        print('Invalid command...Try again')
        print('\n')
        
    print('Type the id of the node you want to access :')
    
    node_id = input()
    print('\n')
    
    print('Type the action or "help" to see the supported commands  :')
    
    cmd = input().split()
    print('\n')