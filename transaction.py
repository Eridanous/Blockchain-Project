# -*- coding: utf-8 -*-
"""
@authors: Giannis Kazakos, Nikolas Lianos, Eridanous Loulas
"""
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import binascii
from collections import OrderedDict


class Transaction:
    
    def __init__(self, timestamp, sender_address, receiver_address, amount):
        
        # Amount of transaction
        self.amount = amount
        
        # Sender's public_key
        self.sender_address = sender_address
        
        # Receiver's public_key
        self.receiver_address = receiver_address
        #self.transaction_id: το hash του transaction
        #self.transaction_inputs: λίστα από Transaction Input 
        #self.transaction_outputs: λίστα από Transaction Output 
        # Signature
        self.timestamp = timestamp
        self.signature = None
        
        
     
    def calculate_hash(self):
        
        transaction_str = str.encode(self.timestamp + self.sender_address + self.receiver_address + str(self.amount))
        return(SHA256.new(transaction_str))

    def sign_transaction(self, sender_private_key):
        
        transaction_hash = self.calculate_hash()
        sign_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signature = PKCS1_v1_5.new(sign_key).sign(transaction_hash)
        self.signature = binascii.hexlify(signature).decode('ascii')

    def verify_signature(self,sender_key):
        transaction_hash = self.calculate_hash()
        public_key = RSA.importKey(binascii.unhexlify(sender_key))
        verifier = PKCS1_v1_5.new(public_key)
        sig = binascii.unhexlify(self.signature)
        return verifier.verify(transaction_hash, sig)

    
    def to_dict(self):
        return OrderedDict({'Timestamp': self.timestamp,
                            'sender_address': self.sender_address,
                            'recipient_address': self.receiver_address,
                            'value': self.amount,
                            'signature' : self.signature})
    
    def __str__(self):

        return("timestamp: {}, From Address: {}, To Address: {}, Amount: {}".format(
                self.timestamp, self.sender_address, self.receiver_address, self.amount))
    