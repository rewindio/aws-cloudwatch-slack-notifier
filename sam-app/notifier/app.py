import boto3
from botocore.exceptions import ClientError
import json
import logging
import os

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def send_to_slack(slack_message, slack_webhook_url):
    status = True
    print("sending slack message")
    emoji = ":lama:"

    req = Request(slack_webhook_url, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

    return status

def get_slack_webhook_url(ssm_parm):
    ssm_client = boto3.client('ssm')
    slack_url = None

    try:
        response = ssm_client.get_parameter(Name=ssm_parm, WithDecryption=True)
        slack_url = response['Parameter']['Value']

    except ClientError as e:
        print("Unexpected error getting SSM param: "+ e.response['Error']['Code'])
    
    return slack_url

# These are outside the handler so they persist while the container is warm
slack_channel = os.environ['SLACK_CHANNEL']
slack_webhook_ssm_parm = os.environ['SSM_SLACK_WEBHOOK']
region = os.environ['AWS_REGION']

slack_webhook_url = get_slack_webhook_url(slack_webhook_ssm_parm)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    # Pull data out of the alarm message
    alarm_name = message['AlarmName']
    #old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    region_str = message['Region']

    if 'Threshold' in message['Trigger']:
        alarm_threshold = int(message['Trigger']['Threshold'])
        alarm_threshold = format(alarm_threshold,",")
    else:
        alarm_threshold = "n/a"

    if 'EvaluationPeriods' in message['Trigger']:
        eval_periods = message['Trigger']['EvaluationPeriods']
    else:
        eval_periods = "n/a"

    alarm_console_link = "https://console.aws.amazon.com/cloudwatch/home?region=" + region + "#alarm:alarmFilter=ANY;name=" + alarm_name
    slack_message = "Cloudwatch Alarm `" + alarm_name + "` is in state _" + new_state + "_ in " + region_str

    slack_attachment = [
        {
            "fallback": "Check the Cloudwatch console for details.",
            "color": "#EC0030",
            "title": "View Alarm Details in the AWS Console",
            "title_link": alarm_console_link,
            "fields": [
                {
                    "title": "Threshold",
                    "value": str(alarm_threshold),
                    "short": 'false'
                },
                 {
                    "title": "Evals Over Threshold",
                    "value": str(eval_periods),
                    "short": 'false'
                }
            ]
        }
    ]

    slack_body = {
        'username': "ALama",
        'icon_emoji': ":lama:",
        'channel': slack_channel,
        'attachments': slack_attachment,
        'text': slack_message
    }

    if slack_webhook_url:
        status = send_to_slack(slack_body, slack_webhook_url)
    else:
        logger.error("Unable to obtain the Slack webhook URL to post to")

    return status