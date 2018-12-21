# aws-cloudwatch-slack-notifier
Make Cloudwatch alarms readable in Slack

![Alama](https://raw.githubusercontent.com/rewindio/aws-cloudwatch-slack-notifier/master/images/lama-emoji.png)

The AWS Cloudwatch Slack Notifier (or Alama, Alamer) formats Cloudwatch alarms to be a little easier to read.

# Installing and Configuring

## Slack Setup
Before installing anything to AWS, you will need to configure an incoming webhook in Slack to handle the posts for you.  Slack has lots of docs on this.  Once you have the Slack webhook URL, grab it as you'll need it next.

Within the images folder of this repo is a lama emoji. This needs to be added to Slack as a custom emoji and named `:lama:`

## AWS Setup
* Take the Slack webhook URL and save it as an encrypted parameter in AWS Parameter store.
* Get the Key ID from KMS which is used to encrypt your parameter store secret

## Deploying to AWS
Before starting, you will need:
* The [AWS CLI](https://aws.amazon.com/cli/) installed and default credentials configured
* the [AWS SAM CLI](https://github.com/awslabs/aws-sam-cli) installed
* An existing S3 bucket where the AWS Lambda code will be deployed to by SAM
* This repo cloned

1. Run the *build.sh* script.  This will just copy the needed files into the right locations
2. Run the *deploy.sh* script like

```
./deploy.sh <aws CLI profile> <region>  <s3 bucket to store lamba code in> '<slack channel>' '<ssm parmater containing slack webhook' <kms key ID to decrypt ssm parameter>
```

For Example:

```
./deploy.sh staging us-east-1 lambda-sam-staging '#alarms' '/devops/slack/incoming-webhook' 123456-1224-1234-5678-987654321
```

deploy.sh uses AWS SAM to package the AWS Lambda functions and then deploys them to AWS.  Everything is deployed as a Cloudformation Stack in the specified region.

## Cloudwatch Alarm Configuration
The template creates an SNS topic called `cloudwatch_to_slack` and subscribes the Lambda to it.  Any Cloudwatch alarms you want formatted and sent to the configured Slack channel should just be configured to notify this topic.  The Lambda will do the rest.
