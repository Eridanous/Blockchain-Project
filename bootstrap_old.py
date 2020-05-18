# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 00:28:55 2019

@author: Giannis Kazakos
"""
from block import Block
from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet


import datetime
import time
import binascii
from Crypto.PublicKey import RSA
from Crypto import Random
import requests
from flask import Flask, jsonify, request, render_template
from threading import Thread


class Node:
    def __init__(self,node_id):
        #set

        self.blockchain = Blockchain()
        self.id = node_id
        self.NBCs = 0
        self.wallet = self.generate_wallet()
        self.ring = {} #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

        
    def generate_wallet(self):
        #create a wallet for this node, with a public key and a private key
        random_gen = Random.new().read
        private_key = RSA.generate(1024,random_gen) #.exportKey("DER").hex()
        public_key = private_key.publickey()
        pr_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        pu_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        return Wallet(pr_key, pu_key)
    
    
    def create_transaction(self,sender, receiver, amount):
        #remember to broadcast it
        return Transaction(sender, receiver, amount)


    def createGenesisBlock(self):
        return( Block("01-01-2019 00:00:00", [Transaction(self.wallet.public_key, self.wallet.public_key, 1000), \
                                               #Transaction("01-01-2019 00:00:00","Genesis Block","a2",1000), \
                                               #Transaction("01-01-2019 00:00:00","Genesis Block","a3",1000),  \
                                               #Transaction("01-01-2019 00:00:00","Genesis Block","a4",1000),   \
                                               #Transaction("01-01-2019 00:00:00","Genesis Block","a5",1000) 
                                               ], "-1" ) )

    def create_new_block(self, previousHash):
        index = len(self.blockchain.chain)
        return Block(index, previousHash)
    
 
    def add_transaction_to_block(self, block, transaction, capacity, difficulty):
        
        number_of_transactions = block.add_transaction(transaction)
        #if enough transactions  mine
        if number_of_transactions == capacity:
            self.mine_block(block,difficulty)
            print("Mining Done!")

# =============================================================================
#     	def register_node_to_ring():
#     		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
#     		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
#     
# =============================================================================
    

    
    
# =============================================================================
#     	def broadcast_transaction():
# =============================================================================
    
    
    
    
    
# =============================================================================
#     	def validdate_transaction():
#     		#use of signature and NBCs balance
# =============================================================================
    
    

        
        
    def mine_block(self, block, difficulty):
        
        block.mine(difficulty)
    
 
    def minePendingTransactions(self,miningRewardAddress):
        
        def getTimestamp(T):
            return(T.Timestamp)
        self.pendingTransactions.sort(key=getTimestamp) 
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        block = Block(timestamp,self.pendingTransactions,self.getLatestBlock().hash)
        block.MineBlock(self.difficulty)
        self.chain.append(block)
        
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.pendingTransactions = [Transaction(timestamp,"N00bCash",miningRewardAddress,self.miningReward)]
    
# =============================================================================
#     	def broadcast_block():
# =============================================================================
    
    
    		
    
# =============================================================================
#     	def valid_proof(.., difficulty=MINING_DIFFICULTY):
# =============================================================================
    
    
    
    
    	#concencus functions
    
# =============================================================================
#     	def valid_chain(self, chain):
#     		#check for the longer chain accroose all nodes
# =============================================================================
    
    
# =============================================================================
#     	def resolve_conflicts(self):
#     		#resolve correct chain
# =============================================================================

difficulty = 4
capacity = 5

nodes_cntr = 0 

node = Node(node_id=0)
#print(node.wallet.private_key)

# Only for the bootstrap node
if node.id == 0:
    
    genesis_tran = node.create_transaction('Noobcash', node.wallet.public_key, 1000)
    print('Genesis Transaction :\n', genesis_tran , '\n')
    genesis_tran.sign_transaction(node.wallet.private_key)

    genesis_block = node.create_new_block(previousHash = 1)
    node.add_transaction_to_block(genesis_block,genesis_tran, capacity, difficulty)
    print('Genesis Block :\n', genesis_block, '\n')
    
    node.blockchain.add_block(genesis_block)
    
    # Register myself to the ring
    node.ring[0] = {'ip_address': '127.0.0.1:5000', 'public_key': node.wallet.public_key, 'balance':node.wallet.get_wallet_balance(node.blockchain)}
    print('Nodes Ring : \n', node.ring, '\n')


#block1 = 

#node.mine_block(genesis_block,difficulty)
#node.add_transaction_to_block(genesis_block,transaction1, capacity)
#print(genesis_block)

#print(transaction1.verify_signature())

app = Flask(__name__)

#node = Node(id = None)


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    node_address = values.get('address')
    print("HAllo Node",node_address)
    
    if node_address is None:
        return "Error: Please supply a valid list of nodes", 400
    global nodes_cntr
    nodes_cntr += 1
    node.ring[nodes_cntr] = {'ip_address': '127.0.0.1:5000', 'public_key': node_address,  'balance': 0}

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [n for n in node.ring.keys()],
    }

      
    return jsonify(response), 201


@app.route('/nodes/get_id', methods=['GET'])
def get_id():
    #Get transactions from transactions pool
    global nodes_cntr
    response = {'node_id': nodes_cntr}
    return jsonify(response), 200




@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    Trans = node.create_transaction(node.wallet.public_key, values['receiver'], values['amount'])
#    Trans.sign_transaction(node.wallet.private_key)
    Trans.signature = None
    node.blockchain.pendingTransactions.append(Trans.to_dict())

    response = {'message': f'Transaction will be added to Pending Transactions'}
    return jsonify(response), 201


# =============================================================================
# @app.route('/transactions/pending', methods=['GET'])
# def pending_transaction():
#      response = node.blockchain.pendingTransactions
#      return jsonify(response), 201
# =============================================================================

# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)