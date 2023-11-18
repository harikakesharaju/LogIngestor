from flask import Flask, request, jsonify
from datetime import datetime
import re

app = Flask(__name__)

logs = []

@app.route('/ingest', methods=['POST'])
def ingest_log():
    log = request.get_json()
    logs.append(log)
    return jsonify({"status": "success"})

@app.route('/search', methods=['GET'])
def search_logs():
    query_params = request.args.to_dict()
    filtered_logs = filter_logs(query_params)
    return jsonify(filtered_logs)

def filter_logs(query_params):
    filtered_logs = logs

    for key, value in query_params.items():
        if key == 'timestamp':
            filtered_logs = filter_by_timestamp(filtered_logs, value)
        elif key == 'level' or key == 'message' or key == 'resourceId' or key == 'traceId' or key == 'spanId' or key == 'commit':
            filtered_logs = filter_by_field(filtered_logs, key, value)
        elif key.startswith('metadata.'):
            metadata_key = key.split('.')[1]
            filtered_logs = filter_by_metadata(filtered_logs, metadata_key, value)

    return filtered_logs

def filter_by_timestamp(logs, timestamp):
    try:
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        return [log for log in logs if datetime.strptime(log['timestamp'], '%Y-%m-%dT%H:%M:%SZ') == timestamp]
    except ValueError:
        return []

def filter_by_field(logs, key, value):
    return [log for log in logs if log.get(key) == value]

def filter_by_metadata(logs, metadata_key, value):
    return [log for log in logs if log.get('metadata', {}).get(metadata_key) == value]

def filter_logs_advanced(query_params):
    filtered_logs = logs

    date_range_start = query_params.get('date_range_start')
    date_range_end = query_params.get('date_range_end')
    regex_pattern = query_params.get('regex_pattern')

    if date_range_start or date_range_end:
        filtered_logs = filter_by_date_range(filtered_logs, date_range_start, date_range_end)

    if regex_pattern:
        filtered_logs = filter_by_regex(filtered_logs, regex_pattern)

    return filtered_logs

def filter_by_date_range(logs, start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ') if start_date else datetime.min
        end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ') if end_date else datetime.max
        return [log for log in logs if start_date <= datetime.strptime(log['timestamp'], '%Y-%m-%dT%H:%M:%SZ') <= end_date]
    except ValueError:
        return []

def filter_by_regex(logs, pattern):
    try:
        regex = re.compile(pattern)
        return [log for log in logs if regex.search(str(log))]
    except re.error:
        return []

if __name__ == '__main__':
    app.run(port=3000)
