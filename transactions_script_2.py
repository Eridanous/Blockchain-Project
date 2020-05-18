# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:11:54 2019

@author: liano
"""

import os
import time
import requests
import json

number_of_nodes = 5
my_id = 2
my_ip = '127.0.0.1:5002'

path = os.getcwd()+'/transactions/'+str(number_of_nodes)+'nodes/transactions'+str(my_id)+'.txt'

cntr = 0
with open(path, "r") as file:
    for line in file:
        if cntr >= 0 and cntr < 20:
            receiver,amount = line.split()
            receiver = receiver[2]
            print('receiver: ',receiver,' amount: ',int(amount))    
            r = requests.post('http://' + my_ip + '/transactions/new', data = json.dumps(dict({'receiver':receiver,'amount':int(amount)})))
            print(r.text)
            cntr += 1
            time.sleep(1)