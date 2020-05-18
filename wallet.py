"""
@authors: Giannis Kazakos, Nikolas Lianos, Eridanous Loulas
"""

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class Wallet:

    def __init__(self, private_key, public_key):
        ##set 
        self.private_key = private_key
        self.public_key = public_key
        self.address = public_key
