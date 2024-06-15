import os
import requests
import re
import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv('.env.local')

class ContractInfo:
    """
    Get information about deployed contracts
    """
    def __init__(self, chain_id):
        """
        Initializes with the specified chain_id and init instance variables
        """
        self.chain_id = chain_id
        self._configure_chain()

    def _configure_chain(self):
        chain_configs = {
            42161: ('arbitrum', 'https://api.arbiscan.io/', os.getenv('ARB_NODE'), os.getenv('ARB_EXPLORER')),
            43114: ('avax', 'https://api.snowtrace.io/', os.getenv('AVAX_NODE'), os.getenv('AVAX_EXPLORER')),
            56: ('bsc', 'https://api.bscscan.com/', os.getenv('BSC_NODE'), os.getenv('BSC_EXPLORER')),
            1: ('ethereum', 'https://api.etherscan.io/', os.getenv('ETH_NODE'), os.getenv('ETH_EXPLORER')),
            10: ('optimism', 'https://api-optimistic.etherscan.io/', os.getenv('OPT_NODE'), os.getenv('OPT_EXPLORER')),
            137: ('polygon', 'https://api.polygonscan.com/', os.getenv('POLY_NODE'), os.getenv('POLY_EXPLORER')),
            8453: ('base', 'https://api.basescan.org/', os.getenv('BASE_NODE'), os.getenv('BASE_EXPLORER')),
            250: ('fantom', 'https://api.ftmscan.com/', os.getenv('FTM_NODE'), os.getenv('FTM_EXPLORER'))
        }

        if self.chain_id in chain_configs:
            self.llama_chain, self.url, self.rpc, self.api_key = chain_configs[self.chain_id]
            self.w3 = Web3(Web3.HTTPProvider(self.rpc))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.timeout = 15 if self.chain_id != 1 else 30  # Special case for Ethereum
            self.timeout = 90 if self.chain_id == 10 else self.timeout  # Special case for Optimism
        else:
            # Raise an exception if the specified chain_id is not valid
            raise Exception("not a valid chain_id")

    def get_contract_abi(self, contract_address):
        """
        Fetches and returns the ABI of a contract
        """
        abi_url = f'{self.url}api?module=contract&action=getabi&address={contract_address}&apikey={self.api_key}'
        response = requests.get(abi_url)
        abi = response.json().get('result')
        return abi

    def get_contract_sourcecode(self, contract_address):
        """
        Fetches and returns the source code of a contract
        """
        sourcecode_url = f'{self.url}api?module=contract&action=getsourcecode&address={contract_address}&apikey={self.api_key}'
        response = requests.get(sourcecode_url).json()
        return response

    def get_contract_creation_info(self, contract_address):
        """
        Fetches and returns the creation information of a contract
        """
        creation_info_url = f'{self.url}api?module=contract&action=getcontractcreation&contractaddresses={contract_address}&apikey={self.api_key}'
        response = requests.get(creation_info_url).json()
        return response

    def get_contract_transactions(self, contract_address):
        """
        Fetches and returns the transactions of a contract
        """
        account_url = f'{self.url}api?module=account&action=txlist&address={contract_address}&apikey={self.api_key}'
        response = requests.get(account_url).json()
        return response

    def get_gas_price(self):
        """
        Fetches and returns the current gas price
        """
        gas_price_url = f'{self.url}api?module=proxy&action=eth_gasPrice&apikey={self.api_key}'
        response = requests.get(gas_price_url).json()
        return response

    def get_contract_details(self, source_code):
        """
        Fetches and returns basic details on the contract from the source code correcting for proxy
        """
        contract_name = None
        contract_address = None
        impl_source_code = source_code
        if source_code['status'] == "1":
            contract_address = source_code['result'][0].get('Implementation',
                                                            source_code['result'][0].get('ContractAddress'))
            if contract_address:
                impl_source_code = self._get_source_code(contract_address)
                if impl_source_code['status'] == "1":
                    contract_name = impl_source_code['result'][0]['ContractName']
            else:
                contract_name = source_code['result'][0]['ContractName']
        return contract_address, contract_name, impl_source_code
