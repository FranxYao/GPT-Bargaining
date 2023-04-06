"""
Using Claude as the backend for the agent. 
TODO: implement the agent class
"""

class ClaudeAgent(object):
    """GPT Agent base class, later derived to be a seller, buyer, critic, or moderator

    TODO: add code to detect price inconsistency to seller and buyer
    TODO: release the restriction of the fixed initial price 
    """
    def __init__(self, 
                 initial_dialog_history=None,
                 agent_type="", # "seller", "buyer", "critic", "moderator"
                 system_instruction="You are a helpful AI assistant", 
                 engine="gpt-3.5-turbo"
                ):
        super().__init__()
        
        self.agent_type = agent_type
        self.engine = engine

        raise NotImplementedError("ClaudeAgent is not implemented yet")
        # if(initial_dialog_history is None):
        #     self.dialog_history = [{"role": "system", "content": system_instruction}]
        # else:
        #     self.initial_dialog_history = deepcopy(initial_dialog_history)
        #     self.dialog_history = deepcopy(initial_dialog_history)

        self.last_prompt = ""
        return 
    
    def reset(self):
        """Reset dialog history"""
        raise NotImplementedError("ClaudeAgent is not implemented yet")
        # self.dialog_history = deepcopy(self.initial_dialog_history)
        return 
        
    
    def call(self, prompt, retry=True):
        """Call the Claude agent to generate a response"""
        raise NotImplementedError("ClaudeAgent is not implemented yet")
        # prompt = {"role": "user", "content": prompt}
        # self.dialog_history.append(prompt)
        # self.last_prompt = prompt['content']
        
        # messages = list(self.dialog_history)
        # messages.append(prompt)
        # if(retry):
        #     response = completion_with_backoff(
        #                   model=self.engine,
        #                   messages=messages
        #                 )
        # else:
        #     response = openai.ChatCompletion.create(
        #                 model=self.engine,
        #                 messages=messages
        #                 )
        # message = response['choices'][0]['message']
        # assert(message['role'] == 'assistant')
        # self.dialog_history.append(dict(message))
        return message['content']

    @property
    def last_response(self):
        raise NotImplementedError("ClaudeAgent is not implemented yet")
        return self.dialog_history[-1]['content']