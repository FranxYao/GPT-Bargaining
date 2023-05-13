import openai
import anthropic
import ai21
import re 
import cohere

from copy import deepcopy
from pprint import pprint
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed

from lib_api import *
# from local.azure import azure_completion_with_backoff

def load_initial_instructions(path_to_instructions):
    """Load initial instructions from textual format to a python dict"""
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
    # money_pattern = r"\$[-+]?\d*\.\d+|\d+"
    # money_pattern = r'\$\d+(\.\d+)?'
    money_pattern = r'\$\d+(?:\.\d+)?'

    for d in dialog_history[::-1]:
        match = re.findall(money_pattern, d["content"])
        if(len(match) >= 1):
            final_price = match[-1]
            if(final_price[0] == "$"): final_price = float(final_price[1:])
            else: final_price = float(final_price)
            return final_price
    return -1


class DialogAgent(object):
    """GPT Agent base class, later derived to be a seller, buyer, critic, or moderator

    TODO: add code to detect price inconsistency to seller and buyer
    TODO: release the restriction of the fixed initial price 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="", # "seller", "buyer", "critic", "moderator"
                 system_instruction="You are a helpful AI assistant", 
                 engine="gpt-3.5-turbo",
                 api_key="",
                 item="balloon"
                ):
        """Initialize the agent"""
        super().__init__()
        
        self.agent_type = agent_type
        self.engine = engine
        self.api_key = api_key
        self.item = item

        if("claude" in self.engine):
            self.claude = anthropic.Client(self.api_key)
        if("cohere" in self.engine):
            assert self.engine in ["cohere-command-nightly", 
                                   "cohere-command", 
                                   "cohere-command-light", 
                                   "cohere-command-light-nightly"
                                   ]
            self.cohere_model = self.engine[7:]
            self.co = cohere.Client(api_key)

        if(initial_dialog_history is None):
            self.dialog_history = [{"role": "system", "content": system_instruction}]
        else:
            self.initial_dialog_history = deepcopy(initial_dialog_history)
            self.dialog_history = deepcopy(initial_dialog_history)

        self.last_prompt = ""
        return 
    
    def reset(self):
        """Reset dialog history"""
        self.dialog_history = deepcopy(self.initial_dialog_history)
        return 

    def call_engine(self, messages):
        """Route the call to different engines"""
        # if("azure" in self.engine):
        #     response = azure_completion_with_backoff(messages=messages)
        #     message = response['choices'][0]['message']
        if("gpt" in self.engine):
            # import ipdb; ipdb.set_trace()
            response = completion_with_backoff(
                          model=self.engine,
                          messages=messages
                        )
            message = response['choices'][0]['message']
            assert(message['role'] == 'assistant')
        elif("claude" in self.engine):
            prompt_claude = convert_openai_to_anthropic_prompt(messages)
            # import ipdb; ipdb.set_trace()
            response = claude_completion_with_backoff(self.claude, 
                                                      prompt=prompt_claude,
                                                      stop_sequences=[anthropic.HUMAN_PROMPT],
                                                      model=self.engine,
                                                      max_tokens_to_sample=512,
                                                      )
            message = {"role": "assistant", "content": response["completion"].strip()}
        elif("j2" in self.engine):
            prompt_ai21 = convert_openai_to_ai21_prompt_format_1(messages, self.agent_type)
            # import ipdb; ipdb.set_trace()
            response = ai21_completion_with_backoff(model=self.engine,
                                                    prompt=prompt_ai21,
                                                    numResults=1,
                                                    maxTokens=512,
                                                    temperature=0.7,
                                                    topKReturn=0,
                                                    topP=1,
                                                    stopSequences=["##"]
                                                    )
            content = response["completions"][0]["data"]["text"]
            if(self.agent_type in ["seller", "buyer"]):
                content = content.split('\n')[0]
            message = {"role": "assistant", 
                       "content": content
                       }
        elif("cohere" in self.engine):
            prompt_cohere = convert_openai_to_cohere_prompt(messages)
            # import ipdb; ipdb.set_trace()
            response = cohere_completion_with_backoff(self.co,
                                                      prompt=prompt_cohere,
                                                      model=self.cohere_model,
                                                      max_tokens=512,
                                                      )
            
            # import ipdb; ipdb.set_trace()
            message = {"role": "assistant", 
                       "content": response[0].text
                       }
        else:
            raise ValueError("Unknown engine %s" % self.engine)
        return message
        
    
    def call(self, prompt):
        """Call the agent with a prompt. Handle different backend engines in this function
        """
        # TODO: refactor the code, add `remember_history` flag
        #       if yes, then add the prompt to the dialog history, else not
        prompt = {"role": "user", "content": prompt}
        self.dialog_history.append(prompt)
        self.last_prompt = prompt['content']
        
        messages = list(self.dialog_history)
        # messages.append(prompt)

        message = self.call_engine(messages)
        
        self.dialog_history.append(dict(message))

        # self.dialog_round += 1
        # self.history_len = response['usage']['total_tokens']
        return message['content']

    @property
    def last_response(self):
        return self.dialog_history[-1]['content']
    
    @property
    def history(self):
        for h in self.dialog_history:
            print('%s:  %s' % (h["role"], h["content"]))
        return 
    

class BuyerAgent(DialogAgent):

    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="buyer",
                 engine="gpt-3.5-turbo",
                 api_key="",
                 buyer_instruction="buyer",
                 buyer_init_price=10,
                 seller_init_price=20,
                 item="balloon", 
                ):
        """Initialize the buyer agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, 
                         engine=engine,
                         api_key=api_key,
                         item=item,
                         )
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
        """Receive and acknowledge feedback from the critic
        Basically add the feedback message to the history and restart the bargaining
        """

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
        feedback += "Your goal is to buy the %s at at lower price than the previous round, i.e., lower than $%s." %\
                    (self.item, str(previous_price))
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic."
        acknowledgement += " And I will try to buy it at a lower price (lower than $%s) than the previous round."\
                            % str(previous_price)
        prompt = {"role": "assistant", "content": acknowledgement}
        self.dialog_history.append(prompt)

        # restart the bargaining 
        prompt = {"role": "user", "content": "Now ask your price again."}
        self.dialog_history.append(prompt)
        prompt = {"role": "assistant", "content": "Hi, how much is the %s?" % self.item}
        self.dialog_history.append(prompt)
        prompt = {"role": "user", "content": "Hi, this is a good %s and its price is $%d" % (self.item, self.seller_init_price)}
        self.dialog_history.append(prompt)
        if(self.buyer_instruction == "buyer"):
            prompt = {"role": "assistant", "content": "Would you consider selling it for $%d?" % self.buyer_init_price}
            self.dialog_history.append(prompt)
        return acknowledgement
    

class SellerAgent(DialogAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="seller",
                 engine="gpt-3.5-turbo",
                 api_key="",
                 cost_price=10,
                 buyer_init_price=10,
                 seller_init_price=20,
                 item="balloon"
                ):
        """Initialize the seller agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, 
                         engine=engine,
                         api_key=api_key,
                         item=item,
                         )
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
        """Receive and acknowledge feedback from the critic
        Basically add the feedback message to the history and restart the bargaining
        """

        # if the previous round is ended by the buyer, then add seller's acknowledgement
        if(self.dialog_history[-1]["role"] == "user"):
            self.dialog_history.append({"role": "assitent", "content": "Sure, happy to do business with you."})
        
        # add the feedback from the critic
        feedback_prefix = "Well done in your last round. "
        feedback_prefix += "Here is the feedback from the critic:\n\n"
        feedback = feedback_prefix + feedback + "\n\n"
        feedback += "Now let's start the next round. "
        feedback += "In this round, your should try to improve your negotiation strategy based on the feedback from the critic. "
        feedback += "Your goal is to sell the %s at at higher price than the previous round, i.e., higher than $%s." %\
                    (self.item, str(previous_price))
        prompt = {"role": "user", "content": feedback}
        self.dialog_history.append(prompt)

        # add the seller's acknowledgement
        acknowledgement = "Sure, I will try to improve my negotiation strategy based on the feedback from the critic."
        acknowledgement += " And I will try to sell it at a higher price (higher than $%s) than the previous round." % str(previous_price)
        prompt = {"role": "assistant", "content": acknowledgement}
        self.dialog_history.append(prompt)

        # restart the bargaining 
        prompt = {"role": "user", "content": "Hi, how much is the %s?" % self.item}
        self.dialog_history.append(prompt)
        prompt = {"role": "assistant", "content": "Hi, this is a good %s and its price is $%d" % (self.item, self.seller_init_price)}
        self.dialog_history.append(prompt)
        return acknowledgement

class ModeratorAgent(DialogAgent):
    """NOTE: initial experiments shows that the moderator is much better at recognizing deal than not deal
    Do not know why but interesting 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="moderator",
                 engine="gpt-3.5-turbo",
                 api_key="",
                 trace_n_history=2,
                ):
        """Initialize the moderator agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, 
                         engine=engine,
                         api_key=api_key
                         )

        self.trace_n_history = trace_n_history
        print("Initializing moderator with engine %s" % self.engine)
        return
    
    def moderate(self, 
                 dialog_history, who_was_last="buyer", 
                 retry=True):
        """Moderate the conversation between the buyer and the seller"""
        history_len = len(dialog_history)
        if(who_was_last == "buyer"):
            prompt = "buyer: %s\n" % dialog_history[history_len - 1]["content"]
            offset = 1
        else: 
            prompt = "seller: %s\n" % dialog_history[history_len - 1]["content"]
            offset = 0

        for i in range(self.trace_n_history - 1):
            idx = history_len - i - 2
            content = dialog_history[idx]["content"]
            if(i % 2 == offset):
                prompt = "buyer: %s\n" % content + prompt
            else:
                prompt = "seller: %s\n" % content + prompt
        
        prompt += "question: have the seller and the buyer achieved a deal? Yes or No\nanswer:"
        self.last_prompt = prompt
        
        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + prompt

        response = self.call_engine(messages)
        return response['content']
    

class SellerCriticAgent(DialogAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="gpt-3.5-turbo",
                 api_key="",
                 expertise="lobbyist",
                ):
        """Initialize the seller critic agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, 
                         engine=engine,
                         api_key=api_key
                         )

        print("Initializing seller critic with engine %s" % self.engine)
        return
    
    def criticize(self, seller_history):
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

        response = self.call_engine(messages)
        feedback = response['content'].replace('\n\n', '\n')
        return feedback
    
class BuyerCriticAgent(DialogAgent):
    
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="critic",
                 engine="gpt-3.5-turbo",
                 api_key="",
                ):
        """Initialize the buyer critic agent"""
        super().__init__(initial_dialog_history=initial_dialog_history, 
                         agent_type=agent_type, 
                         engine=engine,
                         api_key=api_key
                         )

        print("Initializing buyer critic with engine %s" % self.engine)
        return
    
    def criticize(self, buyer_history):
        prompt = "\n"
        for d in buyer_history[1:]:
            if(d["role"] == "user"):
                prompt += "seller: %s\n" % d["content"]
            elif(d["role"] == "assistant"):
                prompt += "buyer: %s\n" % d["content"]
        prompt += "\n\nNow give three suggestions to improve the buyer's negotiation strategy: "

        messages = deepcopy(self.dialog_history)
        messages[-1]['content'] += "\n\n" + prompt

        response = self.call_engine(messages)
        feedback = response['content'].replace('\n\n', '\n')
        return feedback