# Lambda function to read and write data to dynamodb leaderboard table
import json
import boto3


dynamodb = boto3.resource('dynamodb')
table_10 = dynamodb.Table('leaderboard_10')
table_20 = dynamodb.Table('leaderboard_20')
table_30 = dynamodb.Table('leaderboard_30')

# Router function which invokes functions based on GET or POST API requests received in event.
def lambda_handler(event, context):
    # Extract HTTP method and path from the event
    http_method = event.get('httpMethod')
    path = event.get('path')

    # Generate the quiz according to API route logic
    try:
        # --- The Router Logic ---
        if http_method == 'GET' and path == '/leaderboard-q-10':
            status_code = 200
            response_body = get_leaderboard_data(question_count=10)

        elif http_method == 'GET' and path == '/leaderboard-q-20':
            status_code = 200
            response_body = get_leaderboard_data(question_count=20)
        
        elif http_method == 'GET' and path == '/leaderboard-q-30':
            status_code = 200
            response_body = get_leaderboard_data(question_count=30)

        elif http_method == 'PUT' and path == '/leaderboard-q-10':
            status_code = 200
            response_body = put_leaderboard_data(request_body=event['body'])

        elif http_method == 'PUT' and path == '/leaderboard-q-20':
            status_code = 200
            response_body = put_leaderboard_data(request_body=event['body'])

        elif http_method == 'PUT' and path == '/leaderboard-q-30':
            status_code = 200
            response_body = put_leaderboard_data(request_body=event['body'])

        else:
            status_code = 404
            response_body = {"error": "Not Found: No route for this request."}

    except Exception as e:
        status_code = 500
        response_body = {"error": "An internal server error occurred."}

    return {
        "statusCode": status_code,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET', 'POST',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Credentials': True
            },
        "body": json.dumps(response_body)
    }
