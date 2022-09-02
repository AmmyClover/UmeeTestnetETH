import threading
import time
from threading import *
from web3 import Web3


ETH_RPC = 'https://goerli.infura.io/v3/fbc36f556c9e44fabb1ba0c9c2b3dd59'
w3 = Web3(Web3.HTTPProvider(ETH_RPC))


def run(op):
    with open('Wallets.txt', 'r') as file:
        wallets = [row.strip() for row in file]
    threads = 1
    i = 1
    while wallets:
        if threading.active_count() <= threads:
            for _ in range(threads):
                privatekey = wallets.pop(0)
                address = w3.eth.account.privateKeyToAccount(privatekey).address
                print("Wallet ", i, " ", address)
                if op == 1:
                    Thread(target=deposit, args=(address, privatekey,), name=f"HUY-{i}").start()
                    i += 1

                elif op == 2:
                    Thread(target=borrow, args=(address, privatekey,), name=f"HUY-{i}").start()
                    i += 1
                elif op == 3:
                    Thread(target=approve, args=(address, privatekey,), name=f"HUY-{i}").start()
                    i += 1

def approve(addr, privatekey):
    abi = open("abi_approve.txt", 'r').read().replace('\n', '')
    nonce = w3.eth.getTransactionCount(addr)
    contract = w3.eth.contract(Web3.toChecksumAddress('0x110bE24B5515DD08c0918B63660AE4eE5cEd3c9c'), abi=abi)
    transaction = contract.functions.approve('0x75d5e88adf8F3597c7C3e4a930544FB48089C779', 115792089237316195423570985008687907853269984665640564039457584007913129639935).buildTransaction(
        {
        'gas': 200000,
        'gasPrice': w3.toWei('3', 'gwei'),
        'from': addr,
        'nonce': nonce
        }
    )
    signed_tx = w3.eth.account.signTransaction(transaction, private_key=privatekey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Approve success")


def deposit(addr, privatekey):
    amount = getBalanceAtom(addr)
    # time.sleep(5)
    if (amount / 1000000) < 1:
        print("Not enough tokens for supply!")
        return 0

    # approve(addr, privatekey)

    abi = open("abi.txt", 'r').read().replace('\n', '')
    nonce = w3.eth.getTransactionCount(addr)
    contract = w3.eth.contract(Web3.toChecksumAddress('0x75d5e88adf8F3597c7C3e4a930544FB48089C779'), abi=abi)
    transaction = contract.functions.deposit('0x110bE24B5515DD08c0918B63660AE4eE5cEd3c9c', amount, addr, 0).buildTransaction(
        {
            'gas': 800000,
            'gasPrice': w3.toWei('3.5', 'gwei'),
            'from': addr,
            'nonce': nonce
        }
    )
    signed_tx = w3.eth.account.signTransaction(transaction, private_key=privatekey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Supply success Atom:", amount / 1000000)


def borrow(addr, privatekey):
    amount = int(getAvailableBorrow(addr))
    if (amount / 1000000) < 1:
        print("Not enough tokens for borrow!")
        return 0
    abi = open("abi.txt", 'r').read().replace('\n', '')
    nonce = w3.eth.getTransactionCount(addr)
    contract = w3.eth.contract(Web3.toChecksumAddress('0x75d5e88adf8F3597c7C3e4a930544FB48089C779'), abi=abi)
    transaction = contract.functions.borrow('0x110bE24B5515DD08c0918B63660AE4eE5cEd3c9c', amount, 2, 0, addr).buildTransaction(
        {
            'gas': 800000,
            'gasPrice': w3.toWei('3.5', 'gwei'),
            'from': addr,
            'nonce': nonce
        }
    )
    signed_tx = w3.eth.account.signTransaction(transaction, private_key=privatekey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Borrow success  Atom:", amount / 1000000)


def getBalanceAtom (addr):

    abi = open("abi.txt", 'r').read().replace('\n', '')
    contract = w3.eth.contract(Web3.toChecksumAddress('0x110bE24B5515DD08c0918B63660AE4eE5cEd3c9c'), abi=abi)
    raw_balance = contract.functions.balanceOf(addr).call()
    return raw_balance


def getAvailableBorrow (addr):
    abi = open("abi.txt", 'r').read().replace('\n', '')
    contract = w3.eth.contract(Web3.toChecksumAddress('0x9939d1E8eF193008F902bFCc5c7d7278332C58Bf'), abi=abi)
    raw_balanceUatom = contract.functions.balanceOf(addr).call()
    contract2 = w3.eth.contract(Web3.toChecksumAddress('0x4BAE106FDeC90bc7e0e1d2658E2F81f4CEFc6921'), abi=abi)
    kolvo_borowchenko = contract2.functions.balanceOf(addr).call()
    return (raw_balanceUatom*0.625) - kolvo_borowchenko


if __name__ == '__main__':
    print("Enter the operation")
    print("1 - deposit")
    print("2 - borrow")
    print("3 - borrow")
    operation = int(input())
    if operation == 1:
        run(1)
    elif operation == 2:
        run(2)
    elif operation == 3:
        run(3)
    else:
        print("Selection error")
