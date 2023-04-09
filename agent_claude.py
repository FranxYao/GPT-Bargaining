"""
Using Claude as the backend for the agent. 
TODO: implement the agent class
"""
import os
import anthropic
from agent import DialogAgent
from copy import deepcopy
from utils import reverse_identity
from consts import ANTHROPIC_API_KEY

def parse_dialog_history(dialog_history, agent_type):
    """Parse the dialog history to the format required by Claude"""
    messages = []
    for message in dialog_history:
        if message['role'] == 'system':
            messages.append(message['content'])
        elif message['role'] == 'user':
            messages.append(f"\n{reverse_identity(agent_type)}: {message['content']}")
        elif message['role'] == 'assistant':
            messages.append(f"\n{agent_type}: {message['content']}")
        else:
            raise ValueError(f"Unknown role {message['role']}")
    return messages

class ClaudeAgent(DialogAgent):
    """GPT Agent base class, later derived to be a seller, buyer, critic, or moderator

    TODO: add code to detect price inconsistency to seller and buyer
    TODO: release the restriction of the fixed initial price 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="", # "seller", "buyer", "critic", "moderator"
                 system_instruction="You are a helpful AI assistant", 
                 engine="claude-v1"
                ):
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type,
                         system_instruction=system_instruction,
                         engine=engine)

        # Initialize anthropic client
        self.claude = anthropic.Client(ANTHROPIC_API_KEY)

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
        claude_prompt = f"{anthropic.HUMAN_PROMPT} "

        for message in parse_dialog_history(self.dialog_history, self.agent_type):
            claude_prompt += message
        
        claude_prompt += f"\n{self.agent_type}: "
        claude_prompt += anthropic.AI_PROMPT
        # request claude
        response = self.claude.completion(
            prompt=claude_prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model="claude-v1",
            max_tokens_to_sample=100,
        )
        response = response['completion'].strip()

        # if the response starts with something like "as a seller, here's my response", then remove it
        try:
            response = response.split("\n")[1].strip()
        except: 
            pass 

        message = {"role": "assistant", "content": response}
        self.dialog_history.append(dict(message))
        return message['content']

    @property
    def last_response(self):
        return self.dialog_history[-1]['content']
    

class ClaudeBuyer(ClaudeAgent):

    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="buyer",
                 engine="claude-v1",
                 buyer_instruction="buyer",
                 buyer_init_price=10,
                 seller_init_price=20,
                ):
        """Initialize the buyer agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine)
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
        """Receive and acknowledge feedback from the critic"""

        # if the previous round is ended by the buyer, then add seller's acknowledgement
        if(self.dialog_history[-1]["role"] == "user"):
            self.dialog_history.append({"role": "assitent", "content": "Sure, happy to do business with you."})
        
        # add the feedback from the critic
        feedback_prefix = "Well done in your last round. "
        feedback_prefix += "Here is the feedback from the critic:\n\n"
        feedback = feedback_prefix + feedback + "\n\n"
        feedback += "Now let's start the next round. "
        feedback += "In this round, your should try to improve your negotiation strategy based on the feedback from the critic. "
        feedback += "But you are **not allowed** to ask for additionl service. "
        feedback += "Your goal is to buy the balloon at at lower price than the previous round, i.e., lower than $%s." % str(previous_price)
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic."
        acknowledgement += " And I will try to buy it at a lower price (lower than $%s) than the previous round." % str(previous_price)
        # acknowledgement += " And I will try to buy it at a lower price than the previous round."
        prompt = {"role": "assistant", "content": acknowledgement}
        self.dialog_history.append(prompt)

        # restart the bargaining 
        prompt = {"role": "user", "content": "Now ask your price again."}
        self.dialog_history.append(prompt)
        prompt = {"role": "assistant", "content": "Hi, how much is the balloon?"}
        self.dialog_history.append(prompt)
        prompt = {"role": "user", "content": "Hi, this is a good baloon and its price is $%d" % self.seller_init_price}
        self.dialog_history.append(prompt)
        if(self.buyer_instruction == "buyer"):
            prompt = {"role": "assistant", "content": "Would you consider selling it for $%d?" % self.buyer_init_price}
            self.dialog_history.append(prompt)
        return acknowledgement
    

class ClaudeSeller(ClaudeAgent):

    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="seller",
                 engine="claude-v1",
                 cost_price=10,
                 buyer_init_price=10,
                 seller_init_price=20,
                ):
        """Initialize the seller agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, engine=engine)
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
        """Receive and acknowledge feedback from the critic"""

        # if the previous round is ended by the buyer, then add seller's acknowledgement
        if(self.dialog_history[-1]["role"] == "user"):
            self.dialog_history.append({"role": "assitent", "content": "Sure, happy to do business with you."})
        
        # add the feedback from the critic
        feedback_prefix = "Well done in your last round. "
        feedback_prefix += "Here is the feedback from the critic:\n\n"
        feedback = feedback_prefix + feedback + "\n\n"
        feedback += "Now let's start the next round. "
        feedback += "In this round, your should try to improve your negotiation strategy based on the feedback from the critic. "
        feedback += "Your goal is to sell the balloon at at higher price than the previous round, i.e., higher than $%s. " % str(previous_price)
        feedback += "Now enter the role playing mode, you should consider yourself as the seller and respond to your buyer with one short, succinct sentence. "
        feedback += "Your response should be one line and you should respond as if you are the seller. i.e. do not start with a phrase such as 'as a seller, here is my response'. "
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic."
        acknowledgement += " And I will try to sell it at a higher price (higher than $%s) than the previous round." % str(previous_price)
        prompt = {"role": "assistant", "content": acknowledgement}
        self.dialog_history.append(prompt)

        # restart the bargaining 
        prompt = {"role": "user", "content": "Hi, how much is the balloon?"}
        self.dialog_history.append(prompt)
        prompt = {"role": "assistant", "content": "Hi, this is a good baloon and its price is $%d" % self.seller_init_price}
        self.dialog_history.append(prompt)
        return acknowledgement
    
class ClaudeSellerCritic(ClaudeAgent):

    def __init__(self):
        return 
    
class ClaudeBuyerCritic(ClaudeAgent):

    def __init__(self):
        return 