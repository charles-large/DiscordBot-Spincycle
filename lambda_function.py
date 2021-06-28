import json
import urllib3
import random
import time
import os
from nacl.signing import VerifyKey 
from nacl.exceptions import BadSignatureError 


TOKEN = os.environ['Discord_Token']
PUBLIC_KEY = os.environ['Discord_Public_Key']



def lambda_handler(event, context):
    # TODO implement
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = event['headers']["x-signature-ed25519"] 
    timestamp = event['headers']["x-signature-timestamp"] 
    body = event['body']
    json_body = json.loads(event['body'])
    print(json_body)

    try:
        #Verify signatures of body with Discord Public Key#
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        if json_body["type"] == 1:
            return {
             'statusCode': 200, 
             'body': json.dumps({'type': 1})
         }
    except (BadSignatureError) as e:
        return {
             'statusCode': 401, 
             'body': json.dumps("Bad Signature")
         }
    
    MEMBER_ID = json_body['data']['options'][0]['value']
    GUILD_ID = json_body['guild_id']
    USERNAME = json_body['data']['resolved']['users'][MEMBER_ID]['username']
    
    # if USERNAME == "Rabid Bigfoot":
    #     return {
    #   'statusCode': 200, 
    #     'body': json.dumps({'type': '4', 'data': {'content': f'Nice try'}})
    # } 
    
    http = urllib3.PoolManager()
    get_url = f"https://discord.com/api/v8/guilds/{GUILD_ID}/channels"
    
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    
    f = http.request('GET', get_url, headers=headers)
    
    request = json.loads(f.data.decode("utf-8"))
    
    # print(request)
    
    voice_channels = [entry['id'] for entry in request if entry['type'] == 2]
    
    patch_url = f"https://discord.com/api/v8/guilds/{GUILD_ID}/members/{MEMBER_ID}"
    
    try:
        return {
       'statusCode': 200, 
        'body': json.dumps({'type': '4', 'data': {'content': f'{USERNAME} has been SPUN'}})
    }
    except Exception as e:
        print(e)
    finally:
        for x in range(4):
            random_choice = random.choice(voice_channels)
            voice_channels.remove(random_choice)
            body = {
             "channel_id": random_choice
        }
            time.sleep(.4)
            body = json.dumps(body).encode()
            try:
                request = http.request('PATCH', patch_url, headers = headers, body=body)
                if json.loads(request.data.decode())['message'] == "Target user is not connected to voice.":
                    return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': "User is not in a voice channel"}})
                    }
            except Exception as e:
                print(e)
                continue 
     