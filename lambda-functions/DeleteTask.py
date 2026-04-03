import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TaskManagementAPI')

def lambda_handler(event, context):
    """
    Delete a task by ID
    
    Args:
        event: API Gateway event with taskId in pathParameters
        context: Lambda context object
        
    Returns:
        HTTP response with 200 status on success, or 404 if not found
    """
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Get taskId
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
                'body': json.dumps({'error': 'Missing taskId'})
            }
        
        print(f"Deleting taskId: {task_id}")
        
        # Find task first
        response = table.scan(
            FilterExpression='taskId = :tid',
            ExpressionAttributeValues={':tid': task_id},
            Limit=1
        )
        
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
        created_at = task['createdAt']
        
        # Delete
        table.delete_item(
            Key={'taskId': task_id, 'createdAt': created_at}
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Task deleted successfully'})
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
