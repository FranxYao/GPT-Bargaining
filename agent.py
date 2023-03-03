import openai

class GPTAgent(object):
    def __init__(self, 
                 system_instruction="You are a helpful assistant.", 
                 initial_instruction="", 
                 role=""
                ):
        super().__init__()
        
        self.role = role
        self.system_instruction = system_instruction
        self.initial_instruction = initial_instruction
        
        self.dialog_history = [{"role": "system", "content": system_instruction}]
        self.history_len = 0
        
        if(len(initial_instruction) > 0): self.call(initial_instruction)
        return 
    
    def call(self, prompt):
        prompt = {"role": "user", "content": prompt}
        self.dialog_history.append(prompt)
        
        messages = list(self.dialog_history)
        messages.append(prompt)
        response = openai.ChatCompletion.create(
                      model="gpt-3.5-turbo",
                      messages=messages
                    )
        message = response['choices'][0]['message']
        assert(message['role'] == 'assistant')
        self.dialog_history.append(dict(message))
        self.history_len = response['usage']['total_tokens']
        return message['content']