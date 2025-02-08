# Local development settings - DO NOT COMMIT actual local_settings.py

# Bitcoin settings
BITCOIN_RPC_URL = 'http://username:password@localhost:8332'

# Ethereum settings
ETH_CHAIN_ID = 3  # Ropsten testnet
ETH_WALLET_ADDRESS = '0x...'  # Your Ethereum wallet address
ETH_PRIVATE_KEY = '0x...'  # Your Ethereum private key
ETHEREUM_RPC_URL = 'https://ropsten.infura.io/v3/YOUR_PROJECT_ID'

# USDT/TRON settings
TRON_API_URL = 'https://api.shasta.trongrid.io'  # Testnet
TRON_WALLET_ADDRESS = 'T...'  # Your TRON wallet address

# Override network settings for testing
NETWORK_SETTINGS = {
    'BTC': {
        'confirmations_required': 1,  # Lower for testing
        'min_withdrawal': '0.001',
        'max_withdrawal': '1.0',
        'withdrawal_fee': '0.0001',
    },
    'ETH': {
        'confirmations_required': 1,  # Lower for testing
        'min_withdrawal': '0.01',
        'max_withdrawal': '10.0',
        'withdrawal_fee': '0.001',
    },
    'USDT': {
        'confirmations_required': 1,  # Lower for testing
        'min_withdrawal': '1.0',
        'max_withdrawal': '1000.0',
        'withdrawal_fee': '1.0',
    }
} 