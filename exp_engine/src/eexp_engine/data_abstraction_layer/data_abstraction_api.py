import requests
import logging
import datetime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_data_abstraction_config(config):
    global CONFIG, DATA_ABSTRACTION_HEADERS
    CONFIG = config
    DATA_ABSTRACTION_HEADERS = {'access-token': CONFIG.DATA_ABSTRACTION_ACCESS_TOKEN}


def get_all_experiments():
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/executed-experiments"
    r = requests.get(url, headers=DATA_ABSTRACTION_HEADERS)
    print(f"GET request to {url} return status code: {r.status_code}")
    return r.json()['executed_experiments']


def create_experiment(body):
    body["status"] = "scheduled"
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/experiments"
    r = requests.put(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    logger.info(f"PUT request to {url} return status code: {r.status_code}")
    if r.status_code == 201:
        exp_id = r.json()['message']['experimentId']
        print(f"New experiment created with id {exp_id}")
        return exp_id
    else:
        print(r.json())
        print("something went wrong when creating experiment")
        return None


def get_experiment(exp_id):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/experiments/{exp_id}"
    r = requests.get(url, headers=DATA_ABSTRACTION_HEADERS)
    print(f"GET request to {url} return status code: {r.status_code}")
    return r.json()['experiment']


def update_experiment(exp_id, body):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/experiments/{exp_id}"
    r = requests.post(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(f"POST request to {url} return status code: {r.status_code}")
    return r.json()


def create_workflow(exp_id, body):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/workflows"
    body["experimentId"] = exp_id
    body["status"] = "scheduled"
    r = requests.put(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(f"PUT request to {url} return status code: {r.status_code}")
    if r.status_code == 201:
        wf_id = r.json()['workflow_id']
        print(f"New workflow created with id {wf_id}")
        return wf_id
    else:
        print(r.json())
        print("something went wrong when creating workflow")
        return None


def get_workflow(wf_id):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/workflows/{wf_id}"
    r = requests.get(url, headers=DATA_ABSTRACTION_HEADERS)
    print(f"GET request to {url} return status code: {r.status_code}")
    return r.json()['workflow']


def update_workflow(wf_id, body):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/workflows/{wf_id}"
    r = requests.post(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(f"POST request to {url} return status code: {r.status_code}")
    return r.json()


def create_metric(wf_id, task, name, semantic_type, kind, data_type):
    body = {
        "name": name,
        "producedByTask": task,
        "type": data_type,
        "kind": kind,
        "semantic_type": semantic_type,
        "parent_id": wf_id,
        "parent_type": "workflow"
    }
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/metrics"
    r = requests.put(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(f"PUT request to {url} return status code: {r.status_code}")
    if r.status_code == 201:
        m_id = r.json()['metric_id']
        print(f"New metric created with id {m_id}")
    else:
        print(r.json())
        print(f"New metric was NOT created successfully")


def update_metric(m_id, body):
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/metrics/{m_id}"
    r = requests.post(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(r.json())
    print(f"POST request to {url} return status code: {r.status_code}")
    return r.json()


def update_metrics_of_workflow(wf_id, result):
    wf = get_workflow(wf_id)
    if "metrics" in wf:
        for m in wf["metrics"]:
            m_id = next(iter(m))
            name = m[m_id]["name"]
            value = result[name]
            add_value_to_metric(m_id, value)


def add_value_to_metric(m_id, value):
    body = {
        "value": str(value)
    }
    return update_metric(m_id, body)


def add_data_to_metric(m_id, data):
    records = []
    for d in data:
        record = {"value": d}
        records.append(record)
    body = {"records": records}
    url = f"{CONFIG.DATA_ABSTRACTION_BASE_URL}/metrics-data/{m_id}"
    r = requests.put(url, json=body, headers=DATA_ABSTRACTION_HEADERS)
    print(f"PUT request to {url} return status code: {r.status_code}")
    print(f"New data added to metric with id {m_id}")


def get_current_time():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
