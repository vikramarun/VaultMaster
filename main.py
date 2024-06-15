import json
from libraries.ai import OpenAIClient
from libraries.contracts import ContractInfo

def get_contract_details(chain_id, contract_address):
    contract_info = ContractInfo(chain_id)
    source_code = contract_info.get_contract_sourcecode(contract_address)

    if source_code['status'] == "0":
        return {'status': 404, 'message': 'Error in running check: API explorer down'}

    vault_address, vault_name, vault_source_code = contract_info.get_contract_details(source_code)

    if vault_source_code['status'] == "0":
        return {'status': 404, 'message': 'Error in running check: API explorer down'}
    else:
        vault_source_code = vault_source_code['result'][0]['SourceCode']
        if 'pragma solidity' not in vault_source_code:
            return {'status': 404, 'message': "Error in running check: Can only run for solidity contracts"}
        vault_source_code = vault_source_code.strip()[1:-1]
        vault_source_code = json.loads(vault_source_code)

    if not vault_address:
        vault_address = contract_address

    if not vault_name:
        return {'status': 404, 'message': "Error in running check: Contract source code not verified"}

    matched_key = next((key for key in vault_source_code['sources'].keys() if vault_name in key), None)

    if matched_key:
        content = vault_source_code['sources'][matched_key]['content']
        selected_source_code = content
    else:
        return {'status': 404, 'message': "Error in running check: Matching source code not found"}

    data = {
        "address": vault_address,
        "name": vault_name,
        "source_code": selected_source_code
    }

    return {'status': 200, 'message': 'Success', 'data': data}

def format_response(response):
    content = response.choices[0].message.content
    formatted_response = f"\nOpenAI Response:\n{'-'*20}\n{content}\n{'-'*20}\n"
    return formatted_response

if __name__ == "__main__":
    client = OpenAIClient()

    vault_code = get_contract_details(8453, '0x83084cB182162473d6FEFfCd3Aa48BA55a7B66F7')
    adapter_code = get_contract_details(8453, '0x6914110efe4e61cfa0f28de5f6606baa33d21693')

    if vault_code['status'] == 200 and adapter_code['status'] == 200:
        message_context = (
            "Title: Adapt Existing ERC-4626 Strategy Integrating Locking Mechanism"
            "Context/Overview: I have an existing ERC-4626 vault and a separate contract that people normally call to do something with their vault shares after."
            "I want to create a new ERC-4626 strategy that incorporates this action directly and appropriately into the original vault. Be comprehensive, and please directly modify the original Vault contract to perform the Action, but only show me what changes."
            "Action Description: Vault shares need to be 'lock' after getting them via deposit/mint. 'unlock' must similarly be called before redeem/withdraw."
        )
        vault_message = vault_code['data']['source_code']
        adapter_message = adapter_code['data']['source_code']

        combined_message = f"{message_context}\n\nVault Code:\n{vault_message}\n\nAction Code:\n{adapter_message}"

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_message}
        ]

        response = client.get_chat_completion(messages)
        formatted_response = format_response(response)
        print(formatted_response)
