from web3 import Web3
import time
#from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request, render_template
import json
import flask
import os
import requests


endpoint = "https://celo-sepolia.g.alchemy.com/v2/uaMqSKXLCJyrnPr4XttQuONWGbjfbGjz"
web3 = Web3(Web3.HTTPProvider(endpoint))

# Flask endpoints for every smart contract functions
app = Flask(__name__)
# app = FastAPI()
# CORS(app)
#cors = CORS(app, resources={r"*": {"origins": "*"}})


# Home message
@app.route("/", methods=['GET'])
# @app.get("/")
async def home():
    return "Welcome to eWallet !"

# Get user balance of ETH
@app.route('/user-balance')
def getUserBalance():
    args = request.args
    userAddress = web3.to_checksum_address(args.get('address'))
    userBalance = web3.eth.get_balance(userAddress)
    return f"User balance : {userBalance}"


# Send ETH to users
@app.route('/send', methods=["POST"])
def sendRawTransaction():
    received_data = request.get_json(force=True)
    senderAddress = web3.to_checksum_address(received_data['senderAddress'])
    senderPrivateKey = received_data['senderPrivateKey']
    receiverAddress = web3.to_checksum_address(received_data['receiverAddress'])
    value = web3.to_wei(received_data['value'], 'ether')
    gas = 21000
    #gasPrice = web3.to_wei(received_data['gasPrice'], 'gwei')
    nonce = web3.eth.get_transaction_count(senderAddress, 'pending')

    latest_block = web3.eth.get_block('latest')
    base_fee = latest_block['baseFeePerGas']

    max_priority_fee = web3.to_wei(2, 'gwei')  # pourboire pour le mineur/validateur, ajustable
    max_fee = base_fee * 2 + max_priority_fee  # marge de sécurité (x2 le baseFee courant)


    # create or build the transaction in form of dictionary
    transaction = {
        'nonce': nonce,
        'to' : receiverAddress,
        'value': value,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': max_priority_fee,
        'gas':gas,
        'chainId': 11142220,
        #'chainId': "0xaa044c",
    }

    # sign the transaction
    signedTransaction = web3.eth.account.sign_transaction(transaction, senderPrivateKey)

    # send the transaction and get the hash
    transaction_hash = web3.eth.send_raw_transaction(signedTransaction.raw_transaction)

    # get the transaction hash
    dictToReturn = {'tx_hash':web3.to_hex(transaction_hash)}
    # dictToReturn.headers.add('Access-Control-Allow-Origin', '*')
    return dictToReturn


if __name__ == "__main__":
    app.run(debug=True)