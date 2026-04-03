# Setup Guide - Deploy Serverless Task Management API

## Prerequisites

- AWS Account
- AWS CLI configured with credentials
- Python 3.12
- Basic understanding of AWS Lambda, API Gateway, DynamoDB

---

## Step 1: Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name TaskManagementAPI \
    --attribute-definitions \
        AttributeName=taskId,AttributeType=S \
        AttributeName=createdAt,AttributeType=N \
        AttributeName=userId,AttributeType=S \
    --key-schema \
        AttributeName=taskId,KeyType=HASH \
        AttributeName=createdAt,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        IndexName=userId-createdAt-index,\
KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=createdAt,KeyType=RANGE}],\
Projection={ProjectionType=ALL} \
    --region us-east-1
```

**Enable Streams (optional):**
```bash
aws dynamodb update-table \
    --table-name TaskManagementAPI \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --region us-east-1
```

---

## Step 2: Create SNS Topic

```bash
aws sns create-topic \
    --name TaskNotifications \
    --region us-east-1
```

**Subscribe email:**
```bash
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:TaskNotifications \
    --protocol email \
    --notification-endpoint your-email@example.com \
    --region us-east-1
```

**Confirm subscription via email link**

---

## Step 3: Create IAM Execution Role

**Create role:**
```bash
aws iam create-role \
    --role-name TaskAPILambdaExecutionRole \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'
```

**Attach AWS managed policy:**
```bash
aws iam attach-role-policy \
    --role-name TaskAPILambdaExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

**Add DynamoDB policy:**
```bash
aws iam put-role-policy \
    --role-name TaskAPILambdaExecutionRole \
    --policy-name DynamoDBTaskAPIAccess \
    --policy-document file://iam-policies/dynamodb-policy.json
```

**Add SNS policy:**
```bash
aws iam put-role-policy \
    --role-name TaskAPILambdaExecutionRole \
    --policy-name SNSPublishTaskNotifications \
    --policy-document file://iam-policies/sns-policy.json
```

---

## Step 4: Create Lambda Functions

**Update SNS_TOPIC_ARN in CreateTask.py with your actual ARN**

**For each function:**

```bash
# Zip the function
cd lambda-functions
zip CreateTask.zip CreateTask.py

# Create Lambda function
aws lambda create-function \
    --function-name CreateTask \
    --runtime python3.12 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/TaskAPILambdaExecutionRole \
    --handler CreateTask.lambda_handler \
    --zip-file fileb://CreateTask.zip \
    --environment Variables={TABLE_NAME=TaskManagementAPI} \
    --region us-east-1
```

**Repeat for:** GetTask, ListTasks, UpdateTask, DeleteTask

---

## Step 5: Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
    --name TaskManagementAPI \
    --endpoint-configuration types=REGIONAL \
    --region us-east-1
```

**Note the API ID from output**

**Create resources and methods via AWS Console or continue with CLI:**
1. Create `/tasks` resource
2. Create `/{id}` resource under `/tasks`
3. Add methods (POST, GET, PUT, DELETE)
4. Configure Lambda integrations
5. Enable CORS
6. Deploy to `dev` stage

---

## Step 6: Test API

**Get Invoke URL:**
```bash
aws apigateway get-stage \
    --rest-api-id YOUR-API-ID \
    --stage-name dev \
    --region us-east-1 \
    --query 'invokeUrl'
```

**Test CREATE:**
```bash
curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/dev/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "alice",
    "title": "Test Task",
    "description": "Testing API",
    "priority": "high"
  }'
```

**Test LIST:**
```bash
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/dev/tasks
```

---

## Step 7: Configure CloudWatch

**Create alarm:**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name CreateTask-Errors \
    --alarm-description "Alert on CreateTask Lambda errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --dimensions Name=FunctionName,Value=CreateTask \
    --alarm-actions arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:TaskNotifications
```

---

## Cleanup

**Delete in reverse order:**

```bash
# Delete Lambda functions
aws lambda delete-function --function-name CreateTask
aws lambda delete-function --function-name GetTask
aws lambda delete-function --function-name ListTasks
aws lambda delete-function --function-name UpdateTask
aws lambda delete-function --function-name DeleteTask

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id YOUR-API-ID

# Delete DynamoDB table
aws dynamodb delete-table --table-name TaskManagementAPI

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:TaskNotifications

# Delete IAM role policies and role
aws iam delete-role-policy --role-name TaskAPILambdaExecutionRole --policy-name DynamoDBTaskAPIAccess
aws iam delete-role-policy --role-name TaskAPILambdaExecutionRole --policy-name SNSPublishTaskNotifications
aws iam detach-role-policy --role-name TaskAPILambdaExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name TaskAPILambdaExecutionRole
```

---

## Cost Estimate

**Demo:** ~$0.05  
**Production (100K requests/month):** ~$2.30/month

See main README for detailed cost breakdown.
