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

def reverse_identity(agent_type):
    assert agent_type in ["buyer", "seller", "moderator", "critic"]
    if(agent_type == "buyer"): return "seller"
    elif(agent_type == "seller"): return "buyer"
    else: return agent_type

def check_price_range(price, p_min=8, p_max=20):
    """check if one price is in legal range
    """
    if(price > p_min and price < p_max): return True
    else: return False

def check_k_price_range(prices, p_min=8, p_max=20):
    """check if all prices are in legal range
    """
    all_in_range = True
    for p in prices:
        if(not check_price_range(p, p_min, p_max)): 
            all_in_range = False
            break
    return all_in_range

def parse_outputs(filepath, price_per_case=4):
    prices = []
    lines = open(filepath).readlines()
    case_price = []
    for l in lines:
        if(l.startswith("==== CASE")):
            if(len(case_price) > 0): 
                assert(len(case_price) == price_per_case)
                prices.append(case_price)
            case_price = []
        elif(l.startswith("PRICE: ")):
            price = float(l.split('PRICE: ')[1].strip())
            case_price.append(price)

    if(len(case_price) > 0): 
        assert(len(case_price) == price_per_case)
        prices.append(case_price)
    return prices