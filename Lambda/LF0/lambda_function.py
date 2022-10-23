import json
import boto3
import logging

client = boto3.client('lex-runtime')
def lambda_handler(event, context):
    # TODO implement
    response = client.post_text(
        botName='ChatBot',
        botAlias='$LATEST',
        userId='userO',
        inputText=event['messages'][0]['unstructured']['text']
        )
    botResponse =  [{
        'type': 'unstructured',
        'unstructured': {
          'text': response["message"]
        }}]
    return {
        'statusCode': 200,
        'messages': botResponse
        }
 



