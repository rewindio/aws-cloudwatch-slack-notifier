#!/bin/bash -x 

PROFILE=$1
REGION=$2
BUCKET=$3
SLACK_CHANNEL=$4
SSM_SLACK_WEBHOOK=$5
SSM_KMS_KEY_ID=$6

pushd sam-app

sam package --template-file template.yaml --output-template-file packaged.yaml --s3-bucket ${BUCKET} --profile ${PROFILE}

CLEANED_SLACK_CHANNEL=$(echo ${SLACK_CHANNEL} | tr -d '#')

sam deploy \
    --template-file packaged.yaml \
    --parameter-overrides SlackChannel=${SLACK_CHANNEL} SSMParameterSlackWebhook=${SSM_SLACK_WEBHOOK} SSMKMSKeyId=${SSM_KMS_KEY_ID} SNSTopicName=cloudwatch_to_slack-${CLEANED_SLACK_CHANNEL}\
    --stack-name cw-alarm-to-slack-${CLEANED_SLACK_CHANNEL} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION} \
    --profile ${PROFILE}

aws cloudformation describe-stacks --stack-name cw-alarm-to-slack-${CLEANED_SLACK_CHANNEL} --query 'Stacks[].Outputs' --profile ${PROFILE} --region ${REGION}

popd
