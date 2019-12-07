from cli import CommandLineInterface
from connection import Connection
from thought import Thought
from datetime import datetime


cli = CommandLineInterface()


@cli.command
def upload(address, user, thought):
    import socket
    import time
    try:
        address = (address.split(':')[0], int(address.split(':')[1]))
        user = int(user)
        s = socket.socket()
        s.connect(address)
        conn = Connection(s)
        thought_obj = Thought(user, datetime.fromtimestamp(int(time.time())), thought)
        conn.send(thought_obj.serialize())
        return 0
    except Exception as error:
        print(f'ERROR: {error}')
        return 1
    finally:
        conn.close()
        print('done')


if __name__ == '__main__':
    cli.main()
