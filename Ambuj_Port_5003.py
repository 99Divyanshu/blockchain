# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime # Every block should have the time stamp when its created.
import hashlib # Every block will be hashed
import json # we'll use its function to encode blocks before hashing them.
from flask import Flask, jsonify, request  # Flask class is used from flask library and jsonify is used to return message to our interface to interact with our blockchain.
import requests # to catch the right node , when we'll check all nodes are same in yhe de-centralised blockchain network.
from uuid import uuid4 # used for the address of node 
from urllib.parse import urlparse # parse the ip or address of node.

# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self): # used initialise components of class or functions."self" refer to class object.
        self.chain = [] # initialising blockchain by initialising chain that will be a list of blocks.
        self.transactions = [] # list of transactions that will be added to the block from here , kept before create_block() becoz if after it ,then block will be created first and the function wont be able to find transactions.
        self.create_block(proof = 1, previous_hash = '0') # For creation of first or genesis block of blockchain "proof" every block has its proof but by practice its initialised to 1 ,every block has prev. hash which is encoded as we'll use sha256 and by practice initialised to '0'.
        self.nodes = set() # for consensus we need nodesalso its a set not list becoz there is no order of nodes , they are created al around the world.
    
    def create_block(self, proof, previous_hash): # will be called once a block is mined we get a proof of work.
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = [] # after adding transactions in block the list must get empty for the other set.
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]  # -1 will give us the last element of chain.

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block): # Take a block as input and returnits sha256 cryptographic hash of the block.
        encoded_block = json.dumps(block, sort_keys = True).encode() # for that the block/dictionary is converted to string using dumps function json library as in future we'll put the dictionary in json file in json format Therefore perform like in hash operation replcing str().
        return hashlib.sha256(encoded_block).hexdigest() 
    
    def is_chain_valid(self, chain): # check the 2 conditions Previous_hash and hash of previous block and the proof_of_work of block is within our definition or not.
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount): # To add transactions tro list in form of dictionary
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block() # We need to add the transactions in the new block ,therefore require the block.
        return previous_block['index'] + 1 # returning the new block index where al the transactions will be added
    
    def add_node(self, address): # add node in using address(http://127.0.0.1:5000) by varying port no.s and return the parsed address(only 127......:....)part.
        parsed_url = urlparse(address) # categorising the url into "scheme:http , netloc:'127.0.0.1:5000',etc.
        self.nodes.add(parsed_url.netloc) # add is used in place of append(for lists) for set. Netloc gives us the 127..... part.
    
    def replace_chain(self): # to replace with longest chain in the network.
        network = self.nodes
        longest_chain = None # it will store the longest chain in it for replacement once we iterate through all the nodes(for loop)
        max_length = len(self.chain) # considering the chain we are in currently to be max in size , will get updated if larger chain encountered.
        for node in network: # iterating through all nodes to check length.
            response = requests.get(f'http://{node}/get_chain') # f string i.e. on using it like {nodes} it will give the value in the node set and we have stored the netloc address i.e. ip + port (so we get the correct ip with port for iterating through different nodes) as this requests.get function takes the complete address of the function/request(here get_chain)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:  # if longest_chain is modified (is not NONE)
            self.chain = longest_chain # updating iterated chain by longest chain.
            return True
        return False

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5001
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
# Decorator for what function to trigger and request type(GET)
@app.route('/mine_block', methods = ['GET'])
# method is an http method (Flask documentation) use GET(to get something) use POST(to create something) 
# we need to get a block
def mine_block():
    # no argument becoz we'll get everything from our 'blockchain' object.
# To mine a block we need
# 1. solve proof of work prob. by finding the proof using prev. proof(last block)
# 2. above step makes it mining successfull.
# 3. now we'll get other keys i.e. index , timestamp......
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Ambuj', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',  # we'll return this response for the Postman in json format therefore Dictionary.
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}  # its a mere key of dictionary until we get the transactions here by (blockchain.add_transactions())
    return jsonify(response), 200 # jsonify returns 'response' in json format , '200' is the http status code(Google Wikipedia) code for successfull http request(OK).  

# Getting the full Blockchain
# TO fetch the full BLockchain in our user friendly app Postman

@app.route('/get_chain', methods = ['GET'])
def get_chain(): # To display full chain use 'chain' list in 'blockchain' object , will get populated as we mine.
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()  # we'll add the elements of in a json file to get it used get_json() of request module.
    transaction_keys = ['sender', 'receiver', 'amount'] # Keys of transaction that will be used ina condition to check if any element was left empty in Postman app.
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400 # message and faiure http status code.
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount']) # if keys are filled then we need to add transaction in next block mined for that we need its index.
    response = {'message': f'This transaction will be added to Block {index}'} # json['sender']....etc gives the exact value of sender in json file.
    return jsonify(response), 201 # Success http status for create(POST) type of request. 

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json() # json file of nodes.
    nodes = json.get('nodes') # value of key('nodes') gets us the list of address stored in json file of nodes .
    if nodes is None:
        return "No node", 400
    for node in nodes: # Now we'll iterate through all nodes to add them(connect).
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain() #returns boolean
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app

# check our mine_block & get_chain request 
# app(object) run method(2 arguments 'host' & 'port')
# our flask based app is running on 127.0.0.1 in Postman

app.run(host = '0.0.0.0', port = 5003)

# If our 1st request is get_chain we'll get only one block the genesis block. 
