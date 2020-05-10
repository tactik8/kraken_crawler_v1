import json
import requests

def kraken_post_datapoint(record_type, record_id, record):
    url = 'https://us-central1-kraken-v1.cloudfunctions.net/kraken_api_post_datapoint_v1'
    
    headers = {'content-type': 'application/json'}
    payload = {}
    payload['record_type'] = record_type
    payload['record_id'] = record_id
    payload['record'] = record

    payload=json.dumps(payload, default=str)

    r = requests.post(url, data=payload, headers=headers)

    id = r.text
    return id
    

