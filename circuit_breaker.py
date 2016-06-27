import threading

import MySQLdb
from ping_hosts import PingHosts

PING_INTERVAL = 10.0

HOST = ""
USERNAME = ""
PASSWORD = ""
DB = ""
TABLE_NAME = ""
# Create Table " create table toggle (name varchar(128),state varchar(123));"

RESULT_TRACKER = {}

HOSTS = {'zorotools.groupbycloud.com': 'SEARCHANDISER',
         'qa-product-server-1687331963.us-east-1.elb.amazonaws.com': 'PRODUCT_API'}

query = """ UPDATE toggles
    SET value = %s
    WHERE name in %s """


def calculate_results(results):
    for result in results:
        if results[result] == 'down':
            RESULT_TRACKER[result] += 1
        else:
            RESULT_TRACKER[result] = 0


def break_circuit():
    down = []
    up = []
    for k, v in RESULT_TRACKER.items():
        if v > 5:
            down.append(HOSTS[k])
        else:
            up.append(HOSTS[k])
    update_database(down, up)


def update_database(down, up):
    db = MySQLdb.connect(host=HOST,
                         user=USERNAME,
                         passwd=PASSWORD,
                         db=DB)
    cur = db.cursor()
    database_helper(cur, up, 'True')
    database_helper(cur, down, 'False')
    db.commit()


def create_result_tracker():
    for host in list(HOSTS.keys()):
        RESULT_TRACKER[host] = 0


def database_helper(cur, lists, boolean):
    data = str(lists).replace('[', '(').replace(']', ')')
    if lists:
        cur.execute("UPDATE" + TABLE_NAME + " SET state = " + boolean + " WHERE name in " + data)


def disconnect_database(db):
    db.close()


def check_connections():
    threading.Timer(PING_INTERVAL, check_connections).start()
    ping = PingHosts()
    ping.thread_count = 1
    ping.hosts = list(HOSTS.keys())
    results = ping.start()
    calculate_results(results)
    break_circuit()


create_result_tracker()
check_connections()
