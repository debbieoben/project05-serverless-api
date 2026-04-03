import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TaskManagementAPI')

def lambda_handler(event, context):
    """
    Update an existing task
    
    Args:
        event: API Gateway event with taskId in pathParameters and updates in body
        context: Lambda context object
        
    Returns:
        HTTP response with 200 status and updated task, or 404 if not found
    """
    try:
        print(f"Full event: {json.dumps(event, default=str)}")
        
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
        
        # Parse body - handle all cases
        body = {}
        if event.get('body'):
            if isinstance(event['body'], str):
                try:
                    body = json.loads(event['body'])
                except:
                    body = {}
            elif isinstance(event['body'], dict):
                body = event['body']
        
        # If still no body, check if update fields are in the event directly
        if not body:
            if event.get('title') or event.get('description') or event.get('status') or event.get('priority'):
                body = {
                    'title': event.get('title'),
                    'description': event.get('description'),
                    'status': event.get('status'),
                    'priority': event.get('priority')
                }
                # Remove None values
                body = {k: v for k, v in body.items() if v is not None}
        
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No update fields provided'})
            }
        
        print(f"Update body: {body}")
        
        # Find task
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
        
        # Build update
        update_parts = []
        expr_values = {':updatedAt': int(datetime.now().timestamp())}
        expr_names = {}
        
        update_parts.append("updatedAt = :updatedAt")
        
        if body.get('title'):
            update_parts.append("title = :title")
            expr_values[':title'] = body['title']
        
        if body.get('description'):
            update_parts.append("description = :description")
            expr_values[':description'] = body['description']
        
        if body.get('status'):
            update_parts.append("#st = :status")
            expr_values[':status'] = body['status']
            expr_names['#st'] = 'status'
        
        if body.get('priority'):
            update_parts.append("priority = :priority")
            expr_values[':priority'] = body['priority']
        
        update_expr = "SET " + ", ".join(update_parts)
        
        print(f"Update expression: {update_expr}")
        print(f"Expression values: {expr_values}")
        
        # Update
        update_params = {
            'Key': {'taskId': task_id, 'createdAt': created_at},
            'UpdateExpression': update_expr,
            'ExpressionAttributeValues': expr_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expr_names:
            update_params['ExpressionAttributeNames'] = expr_names
        
        result = table.update_item(**update_params)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Task updated successfully',
                'task': result['Attributes']
            }, default=str)
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
