from .patches import *
from web3 import Web3
from bitcoin import rpc
from django.conf import settings
import requests
import json
from decimal import Decimal
from .logging import TransactionLogger

class BlockchainAPI:
    def __init__(self):
        self.logger = TransactionLogger()
        # Initialize blockchain connections
        self.btc_client = rpc.RawProxy(service_url=settings.BITCOIN_RPC_URL)
        self.web3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))

    def send_transaction(self, network, to_address, amount):
        """Send transaction to blockchain"""
        try:
            tx_hash = None
            if network == 'BTC':
                tx_hash = self.send_btc(to_address, amount)
            elif network == 'ETH':
                tx_hash = self.send_eth(to_address, amount)
            elif network == 'USDT':
                tx_hash = self.send_usdt(to_address, amount)
            else:
                raise ValueError(f"Unsupported network: {network}")

            self.logger.log_blockchain_transaction(
                network=network,
                tx_type='withdrawal',
                amount=amount,
                address=to_address,
                tx_hash=tx_hash,
                status='sent'
            )
            return tx_hash

        except Exception as e:
            self.logger.log_error(
                'blockchain_send',
                str(e),
                f"Network={network}, Address={to_address}, Amount={amount}"
            )
            raise

    def send_btc(self, to_address, amount):
        """Send Bitcoin transaction"""
        try:
            # Convert amount to BTC (from satoshis if needed)
            amount_btc = float(amount)
            
            # Create and send transaction
            tx_hash = self.btc_client.sendtoaddress(to_address, amount_btc)
            
            return tx_hash
            
        except Exception as e:
            print(f"Error sending BTC: {str(e)}")
            raise

    def send_eth(self, to_address, amount):
        """Send Ethereum transaction"""
        try:
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(
                settings.ETH_WALLET_ADDRESS, 
                'latest'
            )
            
            # Convert amount to Wei
            amount_wei = self.web3.to_wei(float(amount), 'ether')
            
            # Prepare transaction
            transaction = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': settings.ETH_CHAIN_ID
            }
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction,
                settings.ETH_PRIVATE_KEY
            )
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_txn.rawTransaction
            )
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"Error sending ETH: {str(e)}")
            raise

    def send_usdt(self, to_address, amount):
        """Send USDT (TRC20) transaction"""
        try:
            # Prepare API request
            url = f"{settings.TRON_API_URL}/wallet/triggersmartcontract"
            
            # Convert amount to USDT format (6 decimals)
            amount_usdt = int(Decimal(amount) * Decimal('1000000'))
            
            # Contract function call data
            data = {
                "owner_address": settings.TRON_WALLET_ADDRESS,
                "contract_address": settings.USDT_CONTRACT_ADDRESS,
                "function_selector": "transfer(address,uint256)",
                "parameter": f"{to_address},{amount_usdt}",
                "fee_limit": 1000000,
                "call_value": 0,
                "visible": True
            }
            
            # Sign and broadcast transaction
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('result', {}).get('result', False):
                return result['transaction']['txID']
            else:
                raise Exception("USDT transaction failed")
            
        except Exception as e:
            print(f"Error sending USDT: {str(e)}")
            raise

    def get_btc_confirmations(self, tx_hash):
        try:
            tx = self.btc_client.getrawtransaction(tx_hash, True)
            if 'confirmations' in tx:
                return tx['confirmations']
            return 0
        except Exception as e:
            print(f"Error getting BTC confirmations: {str(e)}")
            return 0

    def get_eth_confirmations(self, tx_hash):
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            if tx and tx['blockNumber']:
                current_block = self.web3.eth.block_number
                return current_block - tx['blockNumber']
            return 0
        except Exception as e:
            print(f"Error getting ETH confirmations: {str(e)}")
            return 0

    def get_usdt_confirmations(self, tx_hash):
        """Get USDT (TRC20) confirmations using Tron API directly"""
        try:
            url = f"{settings.TRON_API_URL}/transaction-info?hash={tx_hash}"
            response = requests.get(url)
            data = response.json()
            if data.get('confirmed', False):
                return data.get('confirmations', 0)
            return 0
        except Exception as e:
            print(f"Error getting USDT confirmations: {str(e)}")
            return 0

    def generate_deposit_address(self, network):
        """Generate new deposit address for given network"""
        try:
            if network == 'BTC':
                return self.btc_client.getnewaddress()
            elif network == 'ETH':
                account = self.web3.eth.account.create()
                return account.address
            elif network == 'USDT':
                # Use a different method or service for USDT address generation
                raise NotImplementedError("USDT address generation not implemented")
            else:
                raise ValueError(f"Unsupported network: {network}")
        except Exception as e:
            print(f"Error generating address for {network}: {str(e)}")
            raise

class BlockchainManager:
    def __init__(self):
        self.web3 = None  # Initialize web3 connection here
        
    def deposit(self, user, amount):
        # Implement deposit logic
        pass
        
    def withdraw(self, user, amount):
        # Implement withdraw logic
        pass
        
    def get_balance(self, address):
        # Implement balance check
        pass