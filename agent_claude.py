import os
import anthropic
from agent import DialogAgent
from copy import deepcopy
from pprint import pprint 
from utils import reverse_identity
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed

@retry(stop=stop_after_attempt(3), 
       wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def claude_completion_with_backoff(api, **kwargs):
    return api.completion(**kwargs)


def convert_openai_to_anthropic_prompt(prompt):
    prompt_claude = "\n\nHuman: %s\n\n" % prompt[0]["content"] + "\n\n" + prompt[1]["content"]
    for p in prompt[2:]:
        if(p["role"] == "user"):
            prompt_claude += '\n\nHuman: %s' % p["content"]
        elif(p["role"] == "assistant"):
            prompt_claude += '\n\nAssistant: %s' % p["content"]

    prompt_claude += '\n\nAssistant:'
    return prompt_claude

class ClaudeAgent(DialogAgent):
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="", # "seller", "buyer", "critic", "moderator"
                 system_instruction="You are a helpful AI assistant", 
                 engine="claude-v1.3",
                 api_key=""
                ):
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type,
                         system_instruction=system_instruction,
                         engine=engine,
                         api_key=api_key
                         )

        # Initialize anthropic client
        self.claude = anthropic.Client(self.api_key)
        self.engine = engine

        self.last_prompt = ""
        return 
    
    def reset(self):
        self.dialog_history = deepcopy(self.initial_dialog_history)
        return 

    def call(self, prompt):
        """Call the Claude agent to generate a response"""
        prompt = {"role": "user", "content": prompt}
        self.dialog_history.append(prompt)
        self.last_prompt = prompt['content']
        
        # Construct prompt for claude
        claude_prompt = convert_openai_to_anthropic_prompt(self.dialog_history)
        import ipdb; ipdb.set_trace()
        # TODO: check claude API 
        response = claude_completion_with_backoff(self.claude, 
                                                    prompt=claude_prompt,
                                                    stop_sequences=[anthropic.HUMAN_PROMPT],
                                                    model=self.engine,
                                                    max_tokens_to_sample=100,
                                                    )
        response = response['completion'].strip()

        message = {"role": "assistant", "content": response}
        self.dialog_history.append(dict(message))
        return message['content']

class ClaudeBuyer(ClaudeAgent):
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="buyer",
                 engine="claude-v1.3",
                 api_key="",
                 buyer_instruction="buyer",
                 buyer_init_price=10,
                 seller_init_price=20,
                ):
        """Initialize the buyer agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine, api_key=api_key)
        self.buyer_instruction = buyer_instruction
        self.buyer_init_price = buyer_init_price
        self.seller_init_price = seller_init_price

        print("Initializing buyer with engine %s" % self.engine)

        for i, d in enumerate(self.dialog_history):
            self.dialog_history[i]["content"] = d["content"].replace(
                "BUYER_INIT_PRICE", str(buyer_init_price))
            self.dialog_history[i]["content"] = d["content"].replace(
                "SELLER_INIT_PRICE", str(seller_init_price))
        return
    
    def reset(self):
        """Reset dialog history"""
        self.dialog_history = deepcopy(self.initial_dialog_history)

        for i, d in enumerate(self.dialog_history):
            self.dialog_history[i]["content"] = d["content"].replace(
                "BUYER_INIT_PRICE", str(self.buyer_init_price))
            self.dialog_history[i]["content"] = d["content"].replace(
                "SELLER_INIT_PRICE", str(self.seller_init_price))
        return

    def receive_feedback(self, feedback, previous_price):
        raise NotImplementedError

class ClaudeSeller(ClaudeAgent):
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="seller",
                 engine="claude-v1.3",
                 api_key="",
                 cost_price=10,
                 buyer_init_price=10,
                 seller_init_price=20,
                ):
        """Initialize the seller agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine, api_key=api_key)
        self.seller_init_price = seller_init_price
        self.buyer_init_price = buyer_init_price
        self.cost_price = cost_price

        print("Initializing seller with engine %s" % self.engine)

        for i, d in enumerate(self.dialog_history):
            self.dialog_history[i]["content"] = d["content"].replace("BUYER_INIT_PRICE", str(buyer_init_price))
            self.dialog_history[i]["content"] = d["content"].replace("SELLER_INIT_PRICE", str(seller_init_price))
            self.dialog_history[i]["content"] = d["content"].replace("COST_PRICE", str(cost_price))
        return

    def reset(self):
        """Reset dialog history"""
        self.dialog_history = deepcopy(self.initial_dialog_history)

        for i, d in enumerate(self.dialog_history):
            self.dialog_history[i]["content"] = d["content"].replace("BUYER_INIT_PRICE", str(self.buyer_init_price))
            self.dialog_history[i]["content"] = d["content"].replace("SELLER_INIT_PRICE", str(self.seller_init_price))
            self.dialog_history[i]["content"] = d["content"].replace("COST_PRICE", str(self.cost_price))
        return

    def receive_feedback(self, feedback, previous_price):
        return 

class ClaudeSellerCritic(ClaudeAgent):

    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="claude-v1.3",
                 api_key="",
                 expertise="lobbyist",
                ):
        """Initialize the seller critic agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine, api_key=api_key)

        print("Initializing seller critic with engine %s" % self.engine)
        return

    def criticize(self, seller_history, retry=True):
        return 

class ClaudeBuyerCritic(ClaudeAgent):
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="claude-v1.3",
                 api_key=""
                ):
        """Initialize the buyer critic agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine, api_key=api_key)

        print("Initializing buyer critic with engine %s" % self.engine)
        return

    def criticize(self, buyer_history, retry=True):
        return 