import subprocess
import threading

NUMBER_OF_PACKETS = 2
WAIT_TIME = 1


class PingHosts(object):
    hosts = []
    status = {}
    thread_count = 4  # Default thread count
    lock = threading.Lock()

    def ping(self, ip):
        ret = subprocess.call(['ping', '-c', str(NUMBER_OF_PACKETS), '-W', str(WAIT_TIME), ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        return ret == 0

    def pop_queue(self):
        ip = None
        self.lock.acquire()
        if self.hosts:
            ip = self.hosts.pop()
        self.lock.release()
        return ip

    def select_host(self):
        while True:
            ip = self.pop_queue()
            if not ip:
                return None
            result = 'up' if self.ping(ip) else 'down'
            self.status[ip] = result

    def start(self):
        threads = []
        for i in range(self.thread_count):
            t = threading.Thread(target=self.select_host)
            t.start()
            threads.append(t)
        [t.join() for t in threads]
        return self.status
