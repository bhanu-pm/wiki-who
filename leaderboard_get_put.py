import boto3
import json
import os
import time


# Env variables
TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
GSI_NAME = os.environ.get('DYNAMODB_GSI')
MAX_SCORES = {
    "MODE_10": 10,
    "MODE_20": 20,
    "MODE_30": 30
}
SCORE_PADDING = 2 
TIME_PADDING = 8

# Initializing db
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET', 'POST',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Credentials': True
            },
        'body': json.dumps(body)
    }

# Router function for API calls
def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod')
        path = event.get('path')

        # Posting new score
        if http_method == 'POST' and path == '/score':
            body = json.loads(event.get('body', '{}'))
            return add_score(table, body)

        # Getting leaderboard (parameters in the query string)
        elif http_method == 'GET' and path == '/leaderboard':
            params = event.get('queryStringParameters', {})
            return get_leaderboard(table, params)
        
        elif http_method == 'OPTIONS':
            return build_response(200, {'message': 'CORS preflight successful'})

        else:
            return build_response(404, {'error': f'Not Found: No route for {http_method} {path}'})

    except json.JSONDecodeError:
        return build_response(400, {'error': 'Invalid JSON format in request body.'})
    except Exception as e:
        print(f"An error occurred: {e}")
        return build_response(500, {'error': str(e)})

# Adding score to the database
def add_score(table, data):
    nickname = data.get('nickname')
    score = data.get('score')
    time_taken_ms = data.get('timeTakenMs')
    game_mode = data.get('gameMode') # For the different number of questions

    if not all([nickname, isinstance(score, int), isinstance(time_taken_ms, int), game_mode]):
        return build_response(400, {'error': 'Request body must contain nickname, score, timeTakenMs, and gameMode.'})
    
    if game_mode not in MAX_SCORES:
        return build_response(400, {'error': f'Invalid gameMode: {game_mode}'})

    max_score = MAX_SCORES[game_mode]
    inverted_score = max_score - score  # to make a compound index (with time taken), ranks higher if number lower
    
    padded_score = str(inverted_score).zfill(SCORE_PADDING)
    padded_time = str(time_taken_ms).zfill(TIME_PADDING)
    
    score_and_time_key = f"{padded_score}-{padded_time}"

    # For a unique session ID
    # Combining the nickname, game mode, and the current timestamp in ms.
    timestamp_ms = int(time.time() * 1000)
    session_id = f"{nickname}-{game_mode}-{timestamp_ms}"

    item_to_add = {
        'sessionId': session_id,
        'nickname': nickname,
        'score': score,
        'timeTakenMs': time_taken_ms,
        'gameMode': game_mode,
        'scoreAndTime': score_and_time_key,
        'timestamp': timestamp_ms
    }

    table.put_item(Item=item_to_add)
    
    return build_response(201, {'message': 'Score added successfully!', 'item': item_to_add})

# gets top 9 scores from given mode
def get_leaderboard(table, params):
    game_mode = params.get('gameMode')
    if not game_mode or game_mode not in MAX_SCORES:
        return build_response(400, {'error': 'Missing or invalid gameMode query string parameter.'})

    response = table.query(
        IndexName=GSI_NAME,
        KeyConditionExpression=boto3.dynamodb.conditions.Key('gameMode').eq(game_mode),
        ScanIndexForward=True, # Ascending sort on our compound key gives the correct order
        Limit=9
    )
    
    leaderboard_items = response.get('Items', [])
    
    return build_response(200, leaderboard_items)
