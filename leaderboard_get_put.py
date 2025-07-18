# Lambda function to read and write data to dynamodb leaderboard table
import json
import boto3


dynamodb = boto3.resource('dynamodb')
table_10 = dynamodb.Table('leaderboard_10')
table_20 = dynamodb.Table('leaderboard_20')
table_30 = dynamodb.Table('leaderboard_30')

# Router function based on GET or POST API requests received in event.
def lambda_handler(event, context):
    # Extract HTTP method and path from the event
    http_method = event.get('httpMethod')
    path = event.get('path')
    question_count = int(path.split('-')[-1])

    # Generate the quiz according to API route logic
    try:
        if http_method == 'GET' and question_count in [10, 20, 30]:
            status_code = 200
            resource_body = get_leaderboard_data(question_count=question_count)

        elif http_method == 'PUT' and question_count in [10, 20, 30]:
            status_code = 200
            response_body = put_leaderboard_data(request_body=event['body'], table_name=f"table_{question_count}")

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
