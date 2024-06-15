import json
from libraries.ai import OpenAIClient
from libraries.contracts import ContractInfo

def get_vault_details(chain_id, contract_address):
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

    else:
        matched_key = None
        for key in vault_source_code['sources'].keys():
            if vault_name in key:
                matched_key = key
                break

        if matched_key:
            content = vault_source_code['sources'][matched_key]['content']
            selected_source_code = content

    data = {
        "address" : vault_address,
        "name": vault_name,
        "source_code": selected_source_code
    }

    return {'status': 200, 'message': 'Success', 'data': data}

if __name__ == "__main__":
    client = OpenAIClient()

    vault_code = get_vault_details(8453,'0xa92666b7eee6fd502398bb8cabfe15d41f7cd721')
    # chat_completion = client.get_chat_completion(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": "What GPT are you? Are you custom?",
    #         }
    #     ]
    # )
    # print(chat_completion)
