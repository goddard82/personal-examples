"""Script to scrape an airtable page & post relevant events to the Timeline db via the Timeline api"""

import json
import requests
import logging
import boto3
import slack_alerts
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

logger = logging.getLogger(__name__)

SLACK_CONN_ID = 'slack_alerts'

ssm_client = boto3.client('ssm', region_name='eu-west-1')
ssm_response_one = ssm_client.get_parameter(
    Name='{PATH_TO_TOKEN_DIR}',
    WithDecryption=True
)
airtable_token = ssm_response_one['Parameter']['Value']

ssm_response_two = ssm_client.get_parameter(
    Name='{PATH_TO_TOKEN_DIR}',
    WithDecryption=True
)
timeline_token = ssm_response_two['Parameter']['Value']


default_args = {
    'owner': 'timeline',
    'start_date': datetime(2020, 6, 18),
    'depends_on_past': False,
    'provide_context': True,
    'on_failure_callback': slack_alerts.task_fail_slack_alert
}

dag = DAG('airtable_pull_lops',
          description='Airtable timeline scraper for events',
          schedule_interval='59 22 * * *',
          catchup=False,
          default_args=default_args)


def check_airtable(**kwargs):
    payload = ""
    url = "https://api.airtable.com/v0/{ACCOUNT+ENV}/?view=viwkfe2gdKMWiG10r"
    headers = {
        'authorization': "Bearer " + str(airtable_token)
    }
    response = requests.request("GET", url, data=payload, headers=headers)
    jsonresponse = response.json()
    records = jsonresponse["records"]
    if len(records) >= 1:
        print(len(records))
        check_timeline(records)

    else:
        print("No records to scrape.")


def check_timeline(records, **kwargs):
    payload_list = []
    for record in records:
        fields = record["fields"]
        description = fields.get("Name")
        timestamp = fields.get("Start Date", None)
        endtime = fields.get("End Date", None)
        payload = fields.get("Event Type", None)
        event_payload = {
            "description": description,
            "subsystem": "liveops",
            "type": "config",
            "status": "ok",
            "timestamp": timestamp,
            "endtime": endtime,
            "payload": {"notes": payload}
        }
        payload_list.append(event_payload)
        description_to_search_for = event_payload['description']
        start_time = event_payload['timestamp']
        url = "https://{REMOVED}/timeline/events/query"
        querystring = {"subsystem": "liveops", "type": "config",
                       "description": description_to_search_for,
                       "timestamp": start_time}
        payload = ""
        headers = {'authorization': "basic " + str(json.loads(timeline_token)["auth_token"])}
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        jsonresult = response.json()
        found_events = jsonresult["events"]
        if len(found_events) == 0:
            print("I should create an event from this: ")
            write_new(event_payload)
        if len(found_events) >= 1:
            print('record already exists.')
        if response.status_code != 200:
            print("something went wrong")
            print(jsonresult)


def write_new(event_payload, **kwargs):
    url = "https://{REMOVED}/timeline/events"
    payload = event_payload
    headers = {
        'content-type': "application/json",
        'authorization': "basic " + str(json.loads(timeline_token)["auth_token"])
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(response.text)


start = PythonOperator(
  task_id='check_airtable',
  dag=dag,
  python_callable=check_airtable
)
