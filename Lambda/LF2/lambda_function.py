import json
import random
import boto3
import logging
from botocore.exceptions import ClientError
import requests 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#this is the trigger function for this program, it calls the callSQS function 
def lambda_handler(event, context):
    callSQS(event)

#as soon as a message gets in the SQSqueue, lf2 gets triggered and information is stored as a event
def callSQS(event):
    message_attributes = event['Records'][0]['messageAttributes']
    cuisine = message_attributes['cuisine']['stringValue']
    location = message_attributes['location']['stringValue']
    date = message_attributes['date']['stringValue']
    time = message_attributes['time']['stringValue']
    people = message_attributes['people']['stringValue']
    email = message_attributes['email']['stringValue']
    rest_ids = get_rest_id(cuisine)
    rest_info = ""
    for i in range(5):
        
        rest_info += str(i+1)+ ". "+get_restaurant_info(rest_ids[i]) +"\n"+"\n"
    sendMessage = 'As requested the suggestions for '+ cuisine +' You an explore these restaurants. They can accomodate ' + people + ' people to dine in ' + date + ' at ' + time + " " + '\n' +'\n'+rest_info+'Enjoy your meal'
    temp_email(sendMessage,email)

#get restaurant ID from Elastic Open Search with target user query cusine
def get_rest_id(cuisine):
    es_Query = "https://search-jay-bsd4fpyg4nizdhczbv7neibppa.us-east-1.es.amazonaws.com/_search?q={cuisine}".format(
        cuisine=cuisine)
    esResponse = requests.get(es_Query,auth=('jay', '!7Bzeing'))
    data = json.loads(esResponse.content.decode('utf-8'))
    try:
        esData = data["hits"]["hits"]
    except KeyError:
        logger.debug("Error in Hits")
    rest_ids = []
    nums = random.sample(range(0, len(esData)-1), 5)
    for i in range(5):
        tmpList = esData[nums[i]]
        rest_ids.append(tmpList['_source']['id'])

    return rest_ids
    
    
#get restaurant name and address from dynamo db based on the id fetched from Elastic search
def get_restaurant_info(rest_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')
    response = table.get_item(
        Key={
            'id': rest_id
        }
    )
    item = response.get("Item")
    rest_name = item['restaurent']
    rest_address = item['address']
    rest_info = ('Restaurant Name: '+rest_name +'\n'+'Address: '+','.join(rest_address))
    return rest_info

#send user the template mail with the suggestions 
#Note: Free Tier only supports sending mails to verified email addresses 
#Verify the E-Mail address in the SES microservice 
def temp_email(sendMessage,email):
    ses_client = boto3.client("ses", region_name="us-east-1")
    CHARSET = "UTF-8"
    ses_client.send_email(
        Destination={
            "ToAddresses": [
                email,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": sendMessage,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "Dining Suggestions",
            },
        },
        Source="js12178@nyu.edu",
    )