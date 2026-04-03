import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TaskManagementAPI')

def lambda_handler(event, context):
    """
    Get a specific task by ID
    
    Args:
        event: API Gateway event with taskId in pathParameters
        context: Lambda context object
        
    Returns:
        HTTP response with 200 status and task object, or 404 if not found
    """
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Get taskId from path parameters
        task_id = None
        if event.get('pathParameters'):
            task_id = event['pathParameters'].get('id')
        
        if not task_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing taskId in path'})
            }
        
        print(f"Looking for taskId: {task_id}")
        
        # Scan table for the task
        response = table.scan(
            FilterExpression='taskId = :tid',
            ExpressionAttributeValues={':tid': task_id},
            Limit=1
        )
        
        print(f"DynamoDB response: {response}")
        
        items = response.get('Items', [])
        
        if not items:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Task not found'})
            }
        
        task = items[0]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'task': task}, default=str)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
