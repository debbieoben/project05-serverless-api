import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table = dynamodb.Table('TaskManagementAPI')

# SNS Topic ARN - Update with your actual ARN
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:TaskNotifications'

def lambda_handler(event, context):
    """
    Create a new task and send SNS notification
    
    Args:
        event: API Gateway event with task data in body
        context: Lambda context object
        
    Returns:
        HTTP response with 201 status and created task
    """
    try:
        # Handle both API Gateway test and actual requests
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        elif 'body' in event:
            body = event['body']
        else:
            body = event
        
        # Validate required fields
        if 'title' not in body or 'userId' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: title, userId'})
            }
        
        # Generate task ID and timestamps
        task_id = str(uuid.uuid4())
        timestamp = int(datetime.now().timestamp())
        
        # Create task item
        task = {
            'taskId': task_id,
            'userId': body['userId'],
            'title': body['title'],
            'description': body.get('description', ''),
            'status': body.get('status', 'pending'),
            'priority': body.get('priority', 'medium'),
            'dueDate': body.get('dueDate', 0),
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        
        # Save to DynamoDB
        table.put_item(Item=task)
        
        # Send SNS notification
        try:
            message = f"""
New Task Created!

Task ID: {task_id}
Title: {task['title']}
Description: {task['description']}
Priority: {task['priority']}
Status: {task['status']}
Assigned to: {task['userId']}
Created at: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"New Task: {task['title']}",
                Message=message
            )
            print(f"SNS notification sent for task {task_id}")
        except Exception as sns_error:
            print(f"SNS error (non-fatal): {str(sns_error)}")
            # Continue even if SNS fails
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Task created successfully',
                'task': task
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
