import json
import boto3
import pymysql
from datetime import date


def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="ap-northeast-2"
    )
    get_secret_value_response = client.get_secret_value(
        SecretId='rds-secret-05'
    )
    token = get_secret_value_response['SecretString']
    return eval(token)


def db_ops():
    secrets = get_secret()
    try:
        connection = pymysql.connect(
            host=secrets['host'],
            user=secrets['username'],
            password=secrets['password'],
            db='sparta',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    except pymysql.MySQLError as e:
        print("connection error!!")
        return e

    print("connection ok!!")
    return connection


def lambda_handler(event, context):
    type = event['queryStringParameters']['type']

    if type == 'write':
        today = date.today()
        body = json.loads(event['body'])
        conn = db_ops()
        cursor = conn.cursor()
        cursor.execute("insert into board(title, content, regDate) value('" + body['title'] + "', '" + body[
            'content'] + "', '" + today.strftime("%Y%m%d") + "')")
        conn.commit()
        body = json.dumps({
            "message": "success",
        })
    elif type == 'list':
        conn = db_ops()
        cursor = conn.cursor()
        cursor.execute("select idx, title, regDate from board")
        result = cursor.fetchall()
        body = json.dumps({
            "result": "success",
            "data": result
        })
    elif type == 'delete':
        idx = event['queryStringParameters']['idx']
        conn = db_ops()
        cursor = conn.cursor()
        cursor.execute("delete from board where idx=" + idx)
        conn.commit()
        body = json.dumps({
            "message": "success",
        })

    return {
        "statusCode": 200,
        # Cross Origin처리
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,x-requested-with',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        "body": body,
    }