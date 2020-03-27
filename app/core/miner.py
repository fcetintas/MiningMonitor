import logging
import socket
import time
import json


class Miner():

    def __init__(self, ip='127.0.0.1',
                 port=3333,
                 timeout=5,
                 password='',
                 logger=None):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.password = password

        # Create logger and add NullHandler
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.info('Miner - '+self.ip+' - '+str(self.port))

    def check_connection(self):
        """Check if miner available"""
        self.logger.info("Checking if miner is available.")
        with socket.socket() as sock:
            sock.settimeout(self.timeout)
            try:
                sock.connect((self.ip, self.port))
                self.logger.info("Miner is available.")
                return True
            except Exception:
                self.logger.error("Miner is not available.")
                return False

    def get_data(self):
        """Retrieve and return miner data as JSON"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            try:
                sock.connect((self.ip, self.port))
            except Exception:
                logger.error('Miner is closed.')

            request = '{\"id\":0,\"jsonrpc\":\"2.0\",' + \
                      '\"method\":\"miner_getstat1\",\"psw\":\"\"}'
            request = request.encode()
            try:
                sock.sendall(request)
            except Exception:
                logger.error('Sending data was aborted')
                return []
            try:
                data = sock.recv(512)
            except Exception:
                logger.error('Recieveing data was aborted')
                return []
            message = json.loads(data)['result']
            message_dict = {}
            message_dict['version'] = message[0]
            message_dict['running_time'] = int(message[1])
            hashrate = {
                        'hashrate': int(message[2].split(';')[0]),
                        'shr': int(message[2].split(';')[1]),
                        'rejshr': int(message[2].split(';')[2])
                        }
            message_dict['hashrate'] = hashrate
            gpus = []
            for i in range(0, len(message[3].split(';'))):
                gpus.append({'hashrate': int(message[3].split(';')[i]),
                             'tmp': int(message[6].split(';')[2*i]),
                             'fan': int(message[6].split(';')[2*i+1])
                             })
            message_dict['gpus'] = gpus
            message_dict['pool'] = message[7]
            sock.close()
            return message_dict

    def set_timeout(self, timeout):
        self.__timeout = timeout

    def get_timeout(self, timeout):
        return self.__timeout


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    miner = Miner()
    if miner.check_connection():
        while True:
            print(miner.get_data())
            time.sleep(1)
