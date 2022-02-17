from flask import Flask, jsonify, request, make_response
from flask_json_schema import JsonSchema, JsonValidationError
import requests
import logging
import datetime
import json
import boto3
import hmac
import base64


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

schema = JsonSchema(app)

conn = None

ssm_client = boto3.client('ssm', region_name='eu-west-1')
ssm_response = ssm_client.get_parameter(
    Name='/{REMOVED}/peoplefirstbot_token',
    WithDecryption=True
)
peoplefirstbot_token = ssm_response['Parameter']['Value']


ssm_client = boto3.client('ssm', region_name='eu-west-1')
ssm_response_2 = ssm_client.get_parameter(
    Name='/{REMOVED}/peoplehrbot/token',
    WithDecryption=True
)
slack_token = ssm_response_2['Parameter']['Value']


ssm_response_3 = ssm_client.get_parameter(
    Name='/{REMOVED}/peoplefirst-api/hmac',
    WithDecryption=True
)
peoplefirst_hmac = ssm_response_3['Parameter']['Value']


@app.errorhandler(JsonValidationError)
def validation_error(e):
    return jsonify({'error': e.message, 'errors': [validation_error.message for validation_error in e.errors]}), 400


@app.errorhandler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)




@app.route('/peoplefirst/webhook', methods=['POST', 'GET'])
def respond():
    logging.info(request.data)
    print(request.headers)

    jsonresp = request.json
    request_body = str(jsonresp)
    event_data = jsonresp.get('EventData')

    if validate_hmac(request.data) == request.headers.get('Peoplefirst-Signature'):
        url = "https://slack.com/api/chat.postMessage"
        payload = request.json
        querystring = {"channel": "{REMOVED}", "text": str(request.headers) + '\n' + "h success"}
        headers = {'authorization': 'Bearer ' + str(slack_token)}
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        print(response.text)
        return response.text, 200
    else:
        url = "https://slack.com/api/chat.postMessage"
        payload = request.json
        querystring = {"channel": "{REMOVED}", "text": "h failed: " + str(request_body) + '\n' + validate_hmac(request.data) + '\n' + request.headers.get('Peoplefirst-Signature')}
        headers = {'authorization': 'Bearer ' + str(slack_token)}
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        print(response.text)
        return response.text, 200
        # return 404


def this_week():
    week_start = datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().weekday() % 7)
    end_dt = week_start + datetime.timedelta(days=4)
    this_week_list = []
    weekdays = [week_start + datetime.timedelta(days=x) for x in range(0, (end_dt - week_start).days + 1)]
    for date in weekdays:
        this_week_list.append(date.strftime("%Y-%m-%d"))
    return this_week_list


def delete_previous():
    url = "https://{REMOVED}/delete"
    querystring = {"team": "backend"}
    payload = ""
    headers = json.loads(peoplefirstbot_token)
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    return jsonresult


def resolve_user_to_team(employee_id):
    user_teams = []
    with open('./users.json') as json_data_file:
        data = json.load(json_data_file)
        teams = data.get('Teams')
        for team in teams:
            team_name = team.get('Name')
            users = team.get('Users')
            for employee in users:
                stored_employee_id = employee.get('Id')
                name = employee.get('Name')
                if employee_id in employee.values():
                    user_teams.append(team_name)
    print(user_teams)
    return user_teams


def validate_hmac(request_body):
    pfkey_bytes = base64.b64decode(peoplefirst_hmac)
    pfhash = hmac.digest(pfkey_bytes, request_body, "sha256")  # is this hash function correct?
    b64hash = base64.b64encode(pfhash)
    return b64hash.decode('ascii')


@app.route('/peoplefirst/holiday', methods=['POST'])
def validate_incoming():
    """Four stage verification of the incoming request - if it's an event this week and an event by a team member"""
    weekend = ['Sat', 'Sun']
    if datetime.datetime.today().strftime("%a") in weekend:
        logging.info('Not sending reminder on the weekend')
    else:
        if request.headers.get('Peoplefirst-Signature'):
            event = request.json
            request_body = str(event)
            if validate_hmac(request.data) == request.headers.get('Peoplefirst-Signature'):
                event_data = event.get('EventData')
                absence_type = event_data.get('absenceTypeCode')
                person_id = event_data.get('personId')
                if event_data.get('startDate') in this_week() or event_data.get('endDate') in this_week():
                    member_teams = (resolve_user_to_team(person_id))
                    logging.info((resolve_user_to_team(person_id)))
                    if len(member_teams) > 0:
                        logging.info('event is validated as occurring this week and to a member of valid teams')
                        url = "https://{REMOVED}/records/update"
                        payload = {'teams': member_teams}
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Basic {REMOVED}"
                        }
                        response = requests.request("POST", url, json=payload, headers=headers)
                        if response.status_code != 200:
                            logging.info(payload)
                            logging.info(headers)
                            return jsonify({'error': 'server error'}), 500
                        else:
                            print(response.text)
                            return jsonify({}), 200
                    else:
                        logging.info('incoming request is not valid for current teams')
                        return jsonify({'error': 'not valid teams'}), 202
                else:
                    logging.info('bad request this week ')
                    return jsonify({'error': 'bad request this week ' + str(this_week()) + str(event_data.get('startDate'))}), 202

            else:
                return jsonify({'error': 'Unauthorized access'}), 403
        else:
            return jsonify({'error': 'Unauthorized access'}), 403


@app.route('/peoplefirst/health', methods=['GET'])
def peoplefirst_health():
    return {'message': 'Healthy'}, 200



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
