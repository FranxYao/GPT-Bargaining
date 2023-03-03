import openai
import re
import time
import argparse
import json

import numpy as np

from pprint import pprint
from tqdm import tqdm
from agent import GPTAgent

# commandline arguments

parser = argparse.ArgumentParser()
parser.add_argument("--api_key", type=str, default="", help="openai api key")
parser.add_argument("--task", type=str, default="", help="task to be simulated")
args = parser.parse_args()

def main(args):
    openai.api_key = args.api_key

    ## querier
    querier_initial_instruction = open('instructions/querier.txt', 'r').read()
    task = open('instructions/%s.txt' % args.task, 'r').readlines()
    for ti, t in enumerate(task):
        if(args.task == 'coding_questions'):
            t = t.strip()[:-1] + ' in Python'
        q_initial_instruction = querier_initial_instruction.replace("[TASK]", t)
        # import ipdb; ipdb.set_trace()
        querier = GPTAgent(initial_instruction=q_initial_instruction)
        query = querier.call('Now exactly repeat the initial question: %s' % t)

        ## answerer
        answerer_initial_instruction = open('instructions/answerer.txt', 'r').read()
        answerer = GPTAgent(initial_instruction=answerer_initial_instruction)

        ## simulation
        for _ in tqdm(range(5)):
            answer = answerer.call(query)
            query = querier.call(answer)

        with open('outputs/%s/%d_querier.json' % (args.task, ti), 'w', encoding='utf-8') as f:
            json.dump(querier.dialog_history, f, ensure_ascii=False, indent=4)
        with open('outputs/%s/%d_answerer.json' % (args.task, ti), 'w', encoding='utf-8') as f:
            json.dump(answerer.dialog_history, f, ensure_ascii=False, indent=4)

        # pprint(querier.dialog_history)
    return 

if __name__ == "__main__":
    main(args)