"""An example of a DAG for Apache Airflow. Will send a request to an API on a schedule. Uses the custom slack_alerts
 module which posts in a channel should the Airflow task fail."""


import slack_alerts
import requests
import json
import pendulum
import boto3
import logging
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

logger = logging.getLogger(__name__)


SLACK_CONN_ID = 'slack_alerts'

local_tz = pendulum.timezone("Europe/London")

default_args = {
    'owner': 'holiday_bot',
    'start_date': datetime.datetime(2021, 10, 1, tzinfo=local_tz),
    'depends_on_past': False,
    'provide_context': True,
    'on_failure_callback': slack_alerts.task_fail_slack_alert
}

dag = DAG('slack_bot_cleanup',
          description='sends a request every Friday morning to clear up the bot posts from the previous week',
          schedule_interval="0 6 * * 1",
          catchup=False,
          default_args=default_args
          )

ssm_client = boto3.client('ssm', region_name='{REGION}')

ssm_response = ssm_client.get_parameter(
    Name='{PATH-TO-SECRET}',
    WithDecryption=True
)
peoplefirstbot_token = ssm_response['Parameter']['Value']


def cleanup(**kwargs):
    url = "https://peoplefirst-bot.dev.placeholder.co/delete/friday"
    querystring = {"team": "backend"}
    payload = ""
    headers = json.loads(peoplefirstbot_token)
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    print(response.text)


task1 = PythonOperator(
    task_id='cleanup',
    dag=dag,
    python_callable=cleanup
)