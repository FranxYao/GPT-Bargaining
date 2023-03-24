import openai
import re 

from copy import deepcopy
from pprint import pprint
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed

@retry(wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

def load_initial_instructions(path_to_instructions):
    pattern = r"==== (SYSTEM|USER|ASSISTANT) ===="

    # Use re.split to split the string by the pattern
    with open(path_to_instructions) as f:
        content = f.read()
        content = re.split(pattern, content)
        content_ = []
        for c in content: 
            if(c != ""): content_.append(c)
        content = content_
        l = len(content)
        assert(l % 2 == 0)
        initial_instruction = []
        for i in range(0, l, 2):
            instruction = {"role": content[i].strip().lower().replace("====", "").replace(" ", "").strip(), 
                           "content": content[i+1].strip()
                           }
            initial_instruction.append(instruction)
    return initial_instruction

def involve_moderator(player_1_run, player_2_run):
    """If at least one player's response does not contain a number, involve a moderator
    The moderator determines if they players have reached an agreement, or break the 
    negotiation, or is still in negotiation.
    """
    number_pattern = r"[-+]?\d*\.\d+|\d+"

    # Use re.search to find if the string contains a match to the pattern
    match_1 = re.search(number_pattern, player_1_run)
    # print(match_1)
    match_2 = re.search(number_pattern, player_2_run)
    # print(match_2)
    if((match_1 is not None and match_2 is None) or 
       (match_1 is None and match_2 is not None)
       or (match_1 is None and match_2 is None)
      ): return True
    else: return False

def parse_final_price(dialog_history):
    """parse the final price from the dialog history"""
    # money_pattern = r"$[-+]?\d*\.\d+|\d+"
    money_pattern = r'\$\d+(\.\d+)?'

    for d in dialog_history[::-1]:
        # print(d)
        match = re.findall(money_pattern, d["content"])
        # print(match)
        if(len(match) >= 1):
            return match[-1]
    return -1

class GPTAgent(object):
    """GPT Agent base class, later derived to be a seller, buyer, critic, or moderator

    TODO: add code to detect price inconsistency to seller and buyer
    TODO: modify the moderator to support the CONTINUE state
    TODO: release the restriction of the fixed initial price 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="", # "seller", "buyer", "coach", "moderator"
                 system_instruction="You are a helpful AI assistant", 
                 engine="gpt-3.5-turbo"
                ):
        super().__init__()
        
        self.agent_type = agent_type
        self.engine = engine

        if(initial_dialog_history is None):
            self.dialog_history = [{"role": "system", "content": system_instruction}]
        else:
            self.initial_dialog_history = deepcopy(initial_dialog_history)
            self.dialog_history = deepcopy(initial_dialog_history)

        # self.history_len = 0
        # self.dialog_round = 0
        self.last_prompt = ""
        return 
    
    def reset(self):
        """Reset dialog history"""
        self.dialog_history = deepcopy(self.initial_dialog_history)
        # self.history_len = 0
        self.last_prompt = ""
        return
    
    def call(self, prompt, retry=True):
        prompt = {"role": "user", "content": prompt}
        self.dialog_history.append(prompt)
        self.last_prompt = prompt['content']
        
        messages = list(self.dialog_history)
        messages.append(prompt)
        if(retry):
            response = completion_with_backoff(
                          model=self.engine,
                          messages=messages
                        )
        else:
            response = openai.ChatCompletion.create(
                        model=self.engine,
                        messages=messages
                        )
        message = response['choices'][0]['message']
        assert(message['role'] == 'assistant')
        self.dialog_history.append(dict(message))
        # self.dialog_round += 1
        # self.history_len = response['usage']['total_tokens']
        return message['content']

    @property
    def last_response(self):
        return self.dialog_history[-1]['content']
    

class BuyerAgent(GPTAgent):

    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="buyer",
                 engine="gpt-3.5-turbo"
                ):
        super().__init__(initial_dialog_history, agent_type, engine)
        return
    

class SellerAgent(GPTAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="seller",
                 engine="gpt-3.5-turbo"
                ):
        super().__init__(initial_dialog_history, agent_type, engine)
        return
    
    def receive_feedback(self, feedback):
        """Receive and acknowledge feedback from the critic"""

        # if the previous round is ended by the buyer, then add seller's acknowledgement
        if(self.dialog_history[-1]["role"] == "user"):
            self.dialog_history.append({"role": "assitent", "content": "Sure, happy to do business with you."})
        
        # add the feedback from the critic
        feedback_prefix = "Well done in your last round. "
        feedback_prefix += "Here is the feedback from the critic:\n\n"
        feedback = feedback_prefix + feedback + "\n\n"
        feedback += "Now let's start the next round. "
        feedback += "In this round, your should try to improve your negotiation strategy based on the feedback from the critic."
        feedback += "Your goal is to sell the balloon at at higher price than the previous round."
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic."
        acknowledgement += "And I will try to sell it at a higher price than the previous round."
        prompt = {"role": "assistant", "content": acknowledgement}
        self.dialog_history.append(prompt)

        # restart the bargaining 
        prompt = {"role": "user", "content": "Hi, how much is the balloon?"}
        self.dialog_history.append(prompt)
        prompt = {"role": "assistant", "content": "Hi, this is a good baloon and its price is $20"}
        self.dialog_history.append(prompt)
        return

class ModeratorAgent(GPTAgent):
    """NOTE: initial experiments shows that the moderator is much better at recognizing deal than not deal
    Do not know why but interesting 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="moderator",
                 engine="gpt-3.5-turbo"
                ):
        super().__init__(initial_dialog_history, agent_type, engine)
        return
    
    def moderate(self, seller_last_response, buyer_last_response, who_is_first="buyer", retry=True, debug=False):
        if(who_is_first == "buyer"):
            prompt = "buyer: %s\n" % buyer_last_response
            prompt += "seller: %s\n" % seller_last_response
        else: 
            prompt = "seller: %s\n" % seller_last_response
            prompt += "buyer: %s\n" % buyer_last_response
        prompt += "question: have the seller and the buyer achieved a deal? Yes or No\nanswer:"
        self.last_prompt = prompt
        
        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + prompt
        # import ipdb; ipdb.set_trace()

        if(debug): pprint(messages)
        if(retry):
            response = completion_with_backoff(
                          model=self.engine,
                          messages=messages
                        )
        else:
            response = openai.ChatCompletion.create(
                        model=self.engine,
                        messages=messages
                        )
        if(debug): pprint(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']
    

class SellerCriticAgent(GPTAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="gpt-3.5-turbo"
                ):
        super().__init__(initial_dialog_history, agent_type, engine)
        return
    
    def criticize(self, seller_history, retry=True):
        """Criticize the seller's negotiation strategy"""
        prompt = "\n"
        for d in seller_history[1:]:
            if(d["role"] == "user"):
                prompt += "buyer: %s\n" % d["content"]
            elif(d["role"] == "assistant"):
                prompt += "seller: %s\n" % d["content"]
        prompt += "\n\nNow give three suggestions to improve the seller's negotiation strategy: "
        
        # TODO: store the history of the critic
        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + prompt

        if(retry):
            response = completion_with_backoff(
                          model=self.engine,
                          messages=messages
                        )
        else:
            response = openai.ChatCompletion.create(
                        model=self.engine,
                        messages=messages
                        )
        feedback = response['choices'][0]['message']['content']
        return feedback
    
class BuyerCriticAgent(GPTAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="gpt-3.5-turbo"
                ):
        super().__init__(initial_dialog_history, agent_type, engine)
        return
    
    def criticize(self, buyer_history):
        return 