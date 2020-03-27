import socket
import select
import time
import logging
from threading import Thread


class SampleMiner(Thread):
    def __init__(self, host='0.0.0.0', port=2010, max_clients=3, logger=None):
        """ Initialize the server with a host and port to listen to.
        Provide a list of functions that will be used when receiving
        specific data """
        Thread.__init__(self)
        # Create logger and add NullHandler
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.sock.bind((host, port))
        self.sock.listen(max_clients)
        self.sock_threads = []
        self.counter = 0   # Will be used to give a number to each thread

    def close(self):
        """ Close the client socket threads and server socket
        if they exists. """
        _ = 'Closing server socket (host {}, port {})'
        _ = _.format(self.host, self.port)
        self.logger.info(_)

        for thr in self.sock_threads:
            thr.stop()
            thr.join()

        if self.sock:
            self.sock.close()
            self.sock = None

    def run(self):
        """ Accept an incoming connection.
        Start a new SocketServerThread that will handle the communication. """
        _ = 'Starting socket server (host {}, port {})'
        _ = _.format(self.host, self.port)
        self.logger.info(_)

        self.__stop = False
        while not self.__stop:
            self.sock.settimeout(1)
            try:
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None

            if client_sock:
                client_thr = SocketServerThread(
                                                client_sock,
                                                client_addr,
                                                self.counter,
                                                self.logger)
                self.counter += 1
                self.sock_threads.append(client_thr)
                client_thr.start()
        self.close()

    def stop(self):
        self.__stop = True


class SocketServerThread(Thread):
    def __init__(self, client_sock, client_addr, number, logger=None):
        """ Initialize the Thread with a client socket and address """
        Thread.__init__(self)
        # Create logger and add NullHandler
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.client_sock = client_sock
        self.client_addr = client_addr
        self.number = number

    def run(self):
        _ = "[Thr {}] SocketServerThread starting with client {}"
        _ = _.format(self.number, self.client_addr)
        self.logger.info(_)
        self.__stop = False
        while not self.__stop:
            if self.client_sock:
                # Check if the client is still connected
                # and if data is available:
                try:
                    rdy_read, rdy_write, sock_err = select.select(
                                                        [self.client_sock, ],
                                                        [self.client_sock, ],
                                                        [],
                                                        5)
                except select.error:
                    _ = '[Thr {}] Select() failed on socket with {}'
                    _ = _.format(self.number, self.client_addr)
                    self.logger.info()
                    self.stop()
                    return

                if len(rdy_read) > 0:
                    read_data = self.client_sock.recv(255)

                    # Check if socket has been closed
                    if len(read_data) == 0:
                        _ = '[Thr {}] {} closed the socket.'
                        _ = _.format(self.number, self.client_addr)
                        self.logger.info(_)
                        self.stop()
                    else:
                        # Strip newlines just for output clarity
                        _ = '[Thr {}] Received {}'
                        _ = _.format(self.number, read_data.rstrip())
                        self.logger.info(_)
                        if len(rdy_write) > 0:
                            _ = '{"id":0,"jsonrpc":"2.0"' +\
                                ',"method":"miner_getstat1","psw":""}'
                            if read_data.decode() == _:
                                _ = '{"result": ' +\
                                    '["9.3 - ETH", ' +\
                                    '"21", ' +\
                                    '"182724;51;0", ' +\
                                    '"30502;30457;30297' +\
                                    ';30481;30479;30505", ' +\
                                    '"0;0;0", ' +\
                                    '"off;off;off;off;off;off", ' +\
                                    '"53;71;57;67;61;72' +\
                                    ';55;70;59;71;61;70", ' +\
                                    '"eth-eu1.nanopool.org:9999", ' +\
                                    '"0;0;0;0"]}'
                                self.logger.info('Send Message : ' + _)
                                self.client_sock.sendall(_.encode())
                            else:
                                _ = 'Send Message : ' + read_data.decode()
                                self.logger.info(_)
                                self.client_sock.sendall(read_data)

            else:
                _ = "[Thr {}] No client is connected, "
                "SocketServer can't receive data"
                _ = _.format(self.number)
                self.logger.info(_)
                self.stop()
        self.close()

    def stop(self):
        self.__stop = True

    def close(self):
        """ Close connection with the client socket. """
        if self.client_sock:
            _ = '[Thr {}] Closing connection with {}'
            _ = _.format(self.number, self.client_addr)
            self.logger.info(_)
            self.client_sock.close()


def main():
    # Start socket server, stop it after a given duration
    duration = 120
    server = SampleMiner()
    server.start()
    time.sleep(duration)
    server.stop()
    server.join()


if __name__ == "__main__":
    main()
