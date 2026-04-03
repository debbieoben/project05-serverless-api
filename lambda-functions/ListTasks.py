import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TaskManagementAPI')

def lambda_handler(event, context):
    """
    List all tasks with optional limit
    
    Args:
        event: API Gateway event with optional limit in queryStringParameters
        context: Lambda context object
        
    Returns:
        HTTP response with 200 status and array of tasks
    """
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 20))
        
        # Scan table
        response = table.scan(Limit=limit)
        
        tasks = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'tasks': tasks,
                'count': len(tasks)
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
