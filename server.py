import threading
import pathlib
from cli import CommandLineInterface
from listener import Listener
from thought import Thought


cli = CommandLineInterface()


class Handler(threading.Thread):
    lock = threading.Lock()

    def __init__(self, connection, data_dir):
        super().__init__()
        self.connection = connection
        self.data_dir = data_dir

    def run(self):
        user_id_bytes = self.connection.receive(8)
        timestamp_bytes = self.connection.receive(8)
        thought_sz_bytes = self.connection.receive(4)
        thought_sz = int.from_bytes(thought_sz_bytes, 'little')
        thought_bytes = self.connection.receive(thought_sz)
        self.connection.close()
        thought = \
            Thought.deserialize(\
                user_id_bytes+timestamp_bytes+thought_sz_bytes+thought_bytes)
        Handler.lock.acquire()
        try:
            user_dir = self.data_dir.joinpath(str(thought.user_id))
            if not user_dir.exists():
                user_dir.mkdir()
            output_file = \
                user_dir.joinpath(\
                    thought.timestamp.strftime('%Y-%m-%d_%H-%M-%S') + '.txt')
            if output_file.exists():
                open(str(output_file), 'a').write('\n' + thought.thought)
            else:
                open(str(output_file), 'w').write(thought.thought)
            finally:
                Handler.lock.release()


@cli.command
def run(address, data):
    address = (address.split(':')[0], int(address.split(':')[1]))
    data = pathlib.Path(data)
    lsnr = Listener(address[1], host=address[0])
    lsnr.start()
    while True:
        client = lsnr.accept()
        handler = Handler(client, data)
        handler.start()


if __name__ == '__main__':
    cli.main()
