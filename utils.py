import sys

def wprint(s, fd=None, verbose=True):
    if(fd is not None): fd.write(s + '\n')
    if(verbose): print(s)
    return 

class Logger(object):
    def __init__(self, log_file, verbose=True):
        self.terminal = sys.stdout
        self.log = open(log_file, "w")
        self.verbose = verbose

    def write(self, message):
        self.log.write(message + '\n')
        if(self.verbose): self.terminal.write(message + '\n')

    def flush(self):
        pass

def check_price_range(price, p_min=10, p_max=20):
    if(price >= p_min and price <= p_max): return True
    else: return False