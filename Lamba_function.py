import json

def lambda_handler(event, context):
    # TODO implement
    botResponse =  [{
        'type': 'unstructured',
        'unstructured': {
          'text': 'Application under development. Search functionality will be implemented in Assignment 2'
        }}]
    return {
        'statusCode': 200,
        'messages': botResponse
        }
 