import slack_alerts
import requests
import boto3
import logging
import pendulum
import datetime
import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

logger = logging.getLogger(__name__)

SLACK_CONN_ID = 'slack_alerts'

local_tz = pendulum.timezone("Europe/London")

default_args = {
    'owner': 'daniel.goddard',
    'start_date': datetime.datetime(2020, 11, 5, tzinfo=local_tz),
    'depends_on_past': False,
    'provide_context': True,
    'on_failure_callback': slack_alerts.task_fail_slack_alert
}

dag = DAG('yt_lops_reminder',
          description='Sends a slack message to members of the liveops team if they have an incomplete YouTrack task with a '
                      'release date in 2 days time',
          schedule_interval="0 9 * * 1-5",
          catchup=False,
          default_args=default_args
          )

ssm_client = boto3.client('ssm', region_name='eu-west-1')
ssm_response = ssm_client.get_parameter(
    Name='/{REMOVED}/yt-token',
    WithDecryption=True
)
yt_token = ssm_response['Parameter']['Value']

ssm_response_2 = ssm_client.get_parameter(
    Name='/{REMOVED}/token',
    WithDecryption=True
)
slack_token = ssm_response_2['Parameter']['Value']

ssm_response_3 = ssm_client.get_parameter(
    Name='/{REMOVED}/youtrackbot_token',
    WithDecryption=True
)
youtrackbot_token = ssm_response_3['Parameter']['Value']

MSG_PREFIX = "[{'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'Hey "


def get_lops_reminder_recipients(**kwargs):
    """Gets a list of users from a postgresDB via another API"""
    url = "https://{REMOVED}/users/query"
    querystring = {"projects": "lops"}
    payload = ""
    headers = json.loads(youtrackbot_token)
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    users = jsonresult['users']
    for user in users:
        full_name = user["full_name"]
        slack_id = user["slack_id"]
        get_issues(full_name, slack_id)


def add_working_days(**kwargs):
    """Makes sure that working days are counted (and weekends are not)"""
    start_date = datetime.date.today()
    added_days = 2
    days_elapsed = 0
    while days_elapsed < added_days:
        test_date = start_date + datetime.timedelta(days=1)
        start_date = test_date
        if test_date.weekday() > 4:
            continue
        else:
            days_elapsed += 1

    return start_date.strftime("%Y-%m-%d")


def get_issues(youtrack_name, slack_id, **kwargs):
    """Gets a list of issues for the given YouTrack user"""
    global state_value, due_value, type_value, release_value
    issue_list = []
    url = "https://{REMOVED}.myjetbrains.com/youtrack/api/issues?query=for%3A%20" + str(youtrack_name) + "%20%23Unresolved"
    querystring = {
        "fields": "type,created,summary,customFields(?type,id,name,projectCustomField(?type,field(?type,name),id),"
                  "value(?type,id,name)),description,idReadable,parent(issues(?type,idReadable)),subtasks(issues("
                  "?type,idReadable,customFields(?type,id,name,projectCustomField(?type,field(?type,name),id),"
                  "value(?type,id,name)))),project(?type,id,name,shortName)"}
    payload = ""
    headers = {
        'authorization': yt_token,
        'accept': "application/json"
    }
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    for issue in jsonresult:
        issue_id = issue["idReadable"]
        summary = issue["summary"]
        project_short_name = issue["project"]["shortName"]
        customfields = issue["customFields"]
        if project_short_name == "LOP":
            for customfield in customfields:
                customfield_value = customfield["value"]
                customfield_name = customfield["name"]
                if customfield_name == "State":
                    if customfield_value is None:
                        state_value = "_no state_"
                    else:
                        state_value = customfield["value"]["name"]
                if customfield_name == "Release date":
                    release_value = customfield["value"]
                    if release_value is None:
                        release_value = "_no release value_"
                    else:
                        release_value = datetime.datetime.fromtimestamp(release_value / 1000).strftime("%Y-%m-%d")
            possible_states_list = ["No State",
                                    "Idea",
                                    "Backlog In Review",
                                    "Blocked",
                                    "In Testing",
                                    "Ready to publish"]
            if (state_value in possible_states_list and release_value is not None) and release_value == add_working_days():
                issue_info = {"issue_id": issue_id,
                              "summary": summary,
                              "state": state_value,
                              "release_value": release_value}
                issue_list.append(issue_info)

    if len(issue_list) > 0:
        print(youtrack_name, issue_list)
        print(len(issue_list))
        send_reminder(youtrack_name, slack_id, issue_list)
    else:
        print(str(youtrack_name) + " has no issues.")


def send_reminder(youtrack_name, slack_id, issue_list, **kwargs):
    global state
    due_list = []
    name = youtrack_name.split(".")
    name = name[0].capitalize()
    print(name)
    state_link = ""
    blocks = ""
    url = "https://slack.com/api/chat.postMessage"
    too_many_field = {
        "type": "mrkdwn",
        "text": "<https://{REMOVED}.myjetbrains.com/youtrack/issues?q=Assignee:%20" + str(youtrack_name) + str(
            state_link) + "| Over 10 tasks due within 2 days.> "
    }
    if len(issue_list) > 10:
        due_list.clear()
        due_list.append(too_many_field)
        block = MSG_PREFIX + str(
            name) + " - The YT task(s) below are due in the next couple of days - here is a reminder that they are not complete and need to be looked at'}},{'type': 'divider'}," \
                    "{'type': 'section', 'fields':" + str(due_list) + "}]"
    elif len(issue_list) == 1:
        for issue in issue_list:
            issue_id = issue['issue_id']
            summary = issue['summary']
            state = issue['state']
            release_value = issue['release_value']
            issue_field = {
                "type": "mrkdwn",
                "text": "<https://{REMOVED}.myjetbrains.com/youtrack/issue/" + str(issue_id) + "|" + str(
                    issue_id) + "> - " + str(summary) + " - _due " + str(release_value) + "_"
            }
            due_list.append(issue_field)
            block = MSG_PREFIX + str(
            name) + " - The YT task below is due on  _" + str(release_value) + "_ - here is a reminder that it is not complete and needs to be looked at'}},{'type': 'divider'}," \
                    "{'type': 'section', 'text':" + str(issue_field) + "}]"
    else:
        for issue in issue_list:
            issue_id = issue['issue_id']
            summary = issue['summary']
            state = issue['state']
            release_value = issue['release_value']
            issue_field = {
                    "type": "mrkdwn",
                    "text": "<https://{REMOVED}.myjetbrains.com/youtrack/issue/" + str(issue_id) + "|" + str(
                        issue_id) + "> - " + str(summary) + " - _due " + str(release_value) + "_"
                }
            due_list.append(issue_field)
        block = MSG_PREFIX + str(name) + " - The YT task(s) below are due in the next couple of days - here is a reminder that they are not complete and need to be looked at'}},{'type': 'divider'}," \
                        "{'type': 'section', 'fields':" + str(due_list) + "}]"
    querystring = {'channel': str(slack_id), 'text': str(youtrack_name), 'blocks': block}
    payload = ""
    headers = {'authorization': 'Bearer ' + str(slack_token)}
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    if response.status_code != 200:
        print(response.text)
        print(blocks)
    else:
        if "invalid_blocks" in response.text:
            print("block format for " + str(youtrack_name) + " is incorrect.")
            print(block)
        else:
            print(response.text)
            print(querystring)
            print(blocks)


start = PythonOperator(
    task_id='get_lops_reminder_recipients',
    dag=dag,
    python_callable=get_lops_reminder_recipients
)
