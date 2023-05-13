"""APIs for calling different engines"""

import openai
import anthropic
import ai21
import re 
import cohere

from copy import deepcopy
from pprint import pprint
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed


"""
Below are functions calling different APIs. All stops after three retries. 
For the first two retries, if there is a network error, wait for 3 seconds.
For the third retry, if there is a network error, wait for 5 seconds.
"""
STOP_AFTER_ATTEMPT=4

@retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
        wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def completion_with_backoff(**kwargs):
    """OpenAI API wrapper, if network error then retry 3 times"""
    return openai.ChatCompletion.create(**kwargs)


@retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
       wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def claude_completion_with_backoff(api, **kwargs):
    """Claude API wrapper, if network error then retry 3 times"""
    return api.completion(**kwargs)


@retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
       wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def ai21_completion_with_backoff(**kwargs):
    """AI21 API wrapper, if network error then retry 3 times"""
    return ai21.Completion.execute(**kwargs)


@retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
       wait=wait_chain(*[wait_fixed(3) for i in range(2)] +
                       [wait_fixed(5) for i in range(1)]))
def cohere_completion_with_backoff(co, **kwargs):
    """Cohere API wrapper, if network error then retry 3 times"""
    return co.generate(**kwargs)


"""
By default we use OpenAI formated prompt, explained in 
https://github.com/openai/openai-python/blob/main/chatml.md

Below are functions converting prompts to different formats.
"""

def convert_openai_to_anthropic_prompt(prompt):
    """Convert OpenAI API format to Claude format"""
    prompt_claude = "\n\nHuman: %s\n\n" % prompt[0]["content"] + "\n\n" + prompt[1]["content"]
    for p in prompt[2:]:
        if(p["role"] == "user"):
            prompt_claude += '\n\nHuman: %s' % p["content"]
        elif(p["role"] == "assistant"):
            prompt_claude += '\n\nAssistant: %s' % p["content"]

    prompt_claude += '\n\nAssistant:'
    return prompt_claude

def convert_openai_to_ai21_prompt_format_1(prompt, agent_type="buyer"):
    """Convert OpenAI API format to AI21 format, all rounds end with ##"""
    prompt_ai21 = prompt[0]["content"] + "\n\n" + prompt[1]["content"] + "\n\n##\n"

    # if(agent_type == "seller"): counterpart = "Buyer"
    # elif(agent_type == "buyer"): counterpart = "Seller"
    # else: pass 
    
    for p in prompt[2:]:
        if(p["role"] == "user"):
            prompt_ai21 += '\n\nUser: %s\n\n##' % (p["content"])
        elif(p["role"] == "assistant"):
            prompt_ai21 += '\n\nMary: %s\n\n##' % p["content"]

    prompt_ai21 += "\n\nMary:"
    return prompt_ai21

def convert_openai_to_ai21_prompt_format_2(prompt, agent_type="buyer"):
    """Convert OpenAI API format to AI21 format, try other round splitters 
    because using ## seems to be not the default in the official documentation"""
    # prompt_ai21 = prompt[0]["content"] + "\n\n" + prompt[1]["content"]

    # if(agent_type == "seller"): counterpart = "Buyer"
    # elif(agent_type == "buyer"): counterpart = "Seller"
    # else: pass 
    
    # for p in prompt[2:]:
    #     if(p["role"] == "user"):
    #         prompt_ai21 += '\n\n%s: %s' % (counterpart, p["content"])
    #     elif(p["role"] == "assistant"):
    #         prompt_ai21 += '\n\nMary: %s' % p["content"]

    # prompt_ai21 += "\n\nMary:"
    return prompt_ai21

def convert_openai_to_cohere_prompt(prompt):
    """Convert OpenAI API format to Cohere format
    This format is very initial and may subject to change in the future for better perfomance
    """
    prompt_cohere = "\n\n[User] %s\n\n" % prompt[0]["content"] + "\n\n" + prompt[1]["content"]
    for p in prompt[2:]:
        if(p["role"] == "user"):
            prompt_cohere += '\n\n[User] %s' % p["content"]
        elif(p["role"] == "assistant"):
            prompt_cohere += '\n\n[Assistant] %s' % p["content"]

    prompt_cohere += '\n\n[Assistant]'
    return prompt_cohere