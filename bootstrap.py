# -*- coding: utf-8 -*-
"""
@authors: Giannis Kazakos, Nikolas Lianos, Eridanous Loulas
"""
from block import Block
from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet

import requests
from flask import Flask, jsonify, request
import json,jsonpickle

import datetime
import time
import binascii
from Crypto.PublicKey import RSA
from Crypto import Random
from threading import Thread


class Node:
    
    def __init__(self,node_id):
        self.blockchain = Blockchain()
        self.id = node_id
#        self.NBCs = 0
        self.mine_flag = False
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
    
    
    def getBalance(self,address):
        blockchain = self.blockchain
        balance = 0
        for block in blockchain.chain:
            for trans in block.listOfTransactions:
                if trans['sender_address'] == address:
                    balance -= trans['value']
                if trans['recipient_address'] == address:
                    balance += trans['value']            
        return(balance)
    
    
    def create_transaction(self,sender, receiver, amount):
        #remember to broadcast it
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        return Transaction(timestamp,sender, receiver, amount)


    def valid_transaction(self,trans,ring):
         if (trans.amount <= ring[trans.sender_address]['balance']):
              ring[trans.sender_address]['balance'] -= trans.amount
              ring[trans.receiver_address]['balance'] += trans.amount
              return(True)
         else:
              return(False)
#        return(trans.amount <= node.getBalance(trans.sender_address))
        
    def register_node_to_ring(self,node_address):
    		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
        global nodes_id_cntr,node_capacity
        nodes_id_cntr += 1
        self.ring[str(nodes_id_cntr)] = {'ip_address': '127.0.0.1:500'+ str(nodes_id_cntr), 'public_key': node_address,  'balance': 0}  
        

    
    
    def broadcast_ring(self):
        self.create_genesis_block()
        for node_id in self.ring.keys():
            #if str(node_id) == str(self.id+1):
            if int(node_id) > 0:
                self.node_balances()
                genesis = jsonpickle.encode(node.blockchain.getLatestBlock(),unpicklable = True)
                requests.post('http://127.0.0.1:500' + str(node_id) + '/nodes/receive_ring', data = json.dumps(dict({'ring':self.ring,'genesis':genesis})))

    def broadcast_transaction(self,transaction):
         for peer in self.ring.keys():
             if peer != str(self.id):
                 details = self.ring[peer]
                 url = details['ip_address']
                 r = requests.post('http://' + url + '/transactions/receive', data = json.dumps(jsonpickle.encode(transaction)))
                 print(r.text)

    def validate_transaction(self,Trans,ring):
        #use of signature and NBCs balance
        timestamp = Trans['Timestamp']
        sender = Trans['sender_address']
        pk_sender = self.ring[sender]['public_key']
        receiver = Trans['recipient_address']
        value = Trans['value']
        signature = Trans['signature']
        check = Transaction(timestamp,sender,receiver,value)
        check.signature = signature
        return(check.verify_signature(pk_sender) and self.valid_transaction(check,ring) )    
        
        
    def mine_block(self):
         if (self.blockchain.minePendingTransactions()):
             self.broadcast_block(self.blockchain.getLatestBlock())
         self.mine_flag = False
         if len(self.blockchain.pendingTransactions) >= self.blockchain.capacity and self.mine_flag == False:
             self.mine_flag = True
             t = Thread(target = self.mine_block)
             t.start()
                 
    def broadcast_block(self,block):
        for peer in self.ring.keys():
             if peer != str(self.id):
                 details = self.ring[peer]
                 url = details['ip_address']
                 r = requests.post('http://' + url + '/block/receive', data = json.dumps(jsonpickle.encode(block.to_dict())))
                 print(r.text)
    		
    
    def valid_proof(self,block):
        index = block['Index']
        timestamp = block['Timestamp']
        Trans = block['Transactions']
        Nonce = block['Nonce']
        prevHash = block['PreviousHash']
        currHash = block['CurrentHash']
        check = Block(index,Trans,prevHash)
        check.timestamp = timestamp
        check.nonce = Nonce
        check.currentHash = currHash
        if check.isValid(self.blockchain.difficulty):
            return(check)
        else:
            return(None)
    
        
    def validate_block_transactions(self,block):
        temp_ring = self.ring.copy()
        for node in temp_ring.keys():
            temp_ring[node]['balance'] = self.getBalance(node)
        return(all(self.validate_transaction(trans,temp_ring) for trans in block.listOfTransactions))
             
    
    def create_genesis_block(self):
        trans = []
        for index in self.ring.keys():
            trans.append( (self.create_transaction("Noobcash",index,100)).to_dict() )
        # Genesis block creation
        genesis_block = Block(0,trans,'-1')
        self.blockchain.add_block(genesis_block)
        
        
    	#concencus functions
    
# =============================================================================
#     	def valid_chain(self, chain):
#     		#check for the longer chain accroose all nodes
# =============================================================================
    
    
    def resolve_conflicts(self):
    	#resolve correct chain
        max_length = len(self.blockchain.chain)
        max_chain = self.blockchain.chain
        for peer in self.ring.keys():
             if peer != str(self.id):
                 details = self.ring[peer]
                 url = details['ip_address']
                 r = requests.get('http://' + url + '/chain').json()
                 chain = jsonpickle.decode(r)
                 length = len(chain)
                 if max_length < length:
                     max_length = length
                     max_chain = chain
        self.blockchain.chain = max_chain
        self.node_balances()

    def node_balances(self):
        for node in self.ring.keys():
             self.ring[node]['balance'] = self.getBalance(node)

node_capacity = 3
nodes_id_cntr = 0 


app = Flask(__name__)
node = Node(node_id=0)

# Only for the bootstrap node
if node.id == 0:
    
    # Register myself to the ring
    node.ring['0'] = {'ip_address': '127.0.0.1:5000', 'public_key': node.wallet.public_key, 'balance':0} #node.wallet.get_wallet_balance(node.blockchain)}
    print('Nodes Ring : \n', node.ring, '\n')


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    node_address = values.get('address')
    
    if node_address is None:
        return "Error: Please supply a valid list of nodes", 400
    
    node.register_node_to_ring(node_address)    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': [n for n in node.ring.keys()],
    }

      
    return jsonify(response), 201


@app.route('/nodes/get_id', methods=['GET'])
def get_id():
    #Get transactions from transactions pool
    global nodes_id_cntr
    response = {'node_id': nodes_id_cntr}
    if nodes_id_cntr == node_capacity-1:
            t = Thread(target=node.broadcast_ring)
            t.start()
            
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json(force = True)

    # Check that the required fields are in the POST'ed data
    required = ['receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    Trans = node.create_transaction(str(node.id), values['receiver'], values['amount'])
    if node.valid_transaction(Trans,node.ring):
        Trans.sign_transaction(node.wallet.private_key)
        node.blockchain.add_transaction(Trans.to_dict())
        node.broadcast_transaction(Trans.to_dict())
        # Mining + Thread
        if len(node.blockchain.pendingTransactions) >= node.blockchain.capacity and node.mine_flag == False:
            node.mine_flag = True
            t = Thread(target = node.mine_block)
            t.start()
        response = {'message': f'Transaction will be added to Pending Transactions'}
        return jsonify(response), 201
    else:
        response = {'message': f'Transaction is invalid, not enough NBCs'}
        return jsonify(response), 201

@app.route('/transactions/pending', methods=['GET'])
def pending_transaction():
     response = node.blockchain.pendingTransactions
     return jsonify(response), 201
 
@app.route('/chain', methods=['GET'])
def show_chain():
    response = jsonpickle.encode(node.blockchain.chain,unpicklable = True)
    return jsonify(response), 201
#     response = [el.to_dict() for el in node.blockchain.chain]
#    
    
@app.route('/transactions/receive', methods=['POST'])
def receive_transaction():
    Trans = request.get_json(force = True)
    Trans = jsonpickle.decode(Trans)
    if node.validate_transaction(Trans,node.ring):
        node.blockchain.add_transaction(Trans)
        # Mining + Thread
        if len(node.blockchain.pendingTransactions) >= node.blockchain.capacity and node.mine_flag == False:
            node.mine_flag = True
            t = Thread(target = node.mine_block)
            t.start()
        response = {'message': f'Transaction will be added to Pending Transactions'}
        return jsonify(response), 201
    else:
        response = {'message':f'Invalid Transaction, Transaction dropped'}
        return jsonify(response), 400

@app.route('/block/receive', methods=['POST'])
def receive_block():
    receive = request.get_json(force = True)
    receive = jsonpickle.decode(receive)
    block = node.valid_proof(receive)
    if block:
        if block.previousHash == node.blockchain.getLatestBlock().currentHash:
            if node.validate_block_transactions(block):
                node.blockchain.add_block(block)
                response = {'message': f'Block added to Blockchain'}
                return jsonify(response), 201
            else:
                response = {'message': f'Block has invalid Transactions'}
                return jsonify(response), 401  
        elif node.validate_block_transactions(block) and block.previousHash not in node.blockchain.Hash_set:
            t = Thread(target = node.resolve_conflicts())
            t.start()
            response = {'message': f'Consensus'}
            return jsonify(response), 201
        else:
            response = {'message': f'Block already in Blockchain'}
            return jsonify(response), 401            
    else:
        response = {'message': f'Block Rejected'}
        return jsonify(response), 400


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, threaded = True)