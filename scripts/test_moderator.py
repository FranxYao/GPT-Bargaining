import sys 
sys.path.append('..')
sys.path.append('.')
from agent import load_initial_instructions, GPTAgent

import openai

# add commandline arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--engine', type=str, default="gpt-3.5-turbo", help='gpt-3.5-turbo')
# add openai api key
parser.add_argument('--api_key', type=str, default=None, help='openai api key')
args = parser.parse_args()

openai.api_key = args.api_key

def main(args):
    # Test moderator
    moderator_initial_instruction = load_initial_instructions("instructions/moderator.txt")
    moderator = GPTAgent(initial_dialog_history=moderator_initial_instruction, 
                         agent_type="moderator")

    # test cases
    test_cases = open('data/moderator_test.txt').readlines()
    test_case = []
    for li, l in enumerate(test_cases):
        if(li % 3 == 0):
            test_case.append(l)
        elif(li % 3 == 1):
            test_case.append(l)
            # print(test_case)
            if(test_case[0].startswith("seller")):
                who_is_first = "seller"
                seller_last_response = test_case[0].split('seller: ')[1].strip()
                buyer_last_response = test_case[1].split('buyer: ')[1].strip()
            elif(test_case[0].startswith("buyer")): 
                who_is_first = "buyer"
                buyer_last_response = test_case[0].split('buyer: ')[1].strip()
                seller_last_response = test_case[1].split('seller: ')[1].strip()

            moderate = moderator.moderate(seller_last_response, buyer_last_response, 
                                          who_is_first=who_is_first, debug=True)
            # print(test_case[0])
            # print(test_case[1])
            # print('MODERATE: %s' % moderate)
            test_case = []
        else: pass
    return 

if __name__ == "__main__":
    main(args)