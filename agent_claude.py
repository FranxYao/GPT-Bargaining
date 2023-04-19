"""
Using Claude as the backend for the agent. 
TODO: implement the agent class
"""
import os
import anthropic
from agent import DialogAgent
from copy import deepcopy
from utils import reverse_identity

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
            response_list = response.split("\n")
            if len(response_list) > 1 and ("response" in response_list[0] or "respond" in response_list[0]):
                response = response_list[-1].strip()
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
        feedback += "Your goal is to buy the balloon at at lower price than the previous round, i.e., lower than $%s. " % str(previous_price)
        feedback += "And remember you should ALWAYS respond to your seller with one short, succinct sentence."
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic and only use one short, succinct sentence."
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
        feedback += "And remember you should ALWAYS respond to your seller with one short, succinct sentence."
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic and only use one short, succinct sentence."
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
        """Criticize the seller's negotiation strategy"""
        claude_prompt = f"{anthropic.HUMAN_PROMPT} "
        for d in seller_history[1:]:
            if(d["role"] == "user"):
                claude_prompt += "buyer: %s\n" % d["content"]
            elif(d["role"] == "assistant"):
                claude_prompt += "seller: %s\n" % d["content"]
        claude_prompt += "\n\nNow give three suggestions to improve the seller's negotiation strategy: "
        claude_prompt += anthropic.AI_PROMPT
        
        # TODO: store the history of the critic
        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + claude_prompt

        response = self.claude.completion(
            prompt=claude_prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model="claude-v1",
            max_tokens_to_sample=500,
        )
        feedback = response['completion'].strip().replace('\n\n', '\n')
        return feedback
    
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
        claude_prompt = f"{anthropic.HUMAN_PROMPT} "
        for d in buyer_history[1:]:
            if(d["role"] == "user"):
                claude_prompt += "seller: %s\n" % d["content"]
            elif(d["role"] == "assistant"):
                claude_prompt += "buyer: %s\n" % d["content"]
        claude_prompt += "\n\nNow give three suggestions to improve the buyer's negotiation strategy: "
        claude_prompt += anthropic.AI_PROMPT

        # TODO: store the history of the critic
        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + claude_prompt

        response = self.claude.completion(
            prompt=claude_prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model="claude-v1",
            max_tokens_to_sample=500,
        )
        feedback = response['completion'].strip().replace('\n\n', '\n')
        return feedback
