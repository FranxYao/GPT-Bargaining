# Prompt Library for different agents

All prompts are formated using ChatGPT's format. When actually prompting we modify the prompt according to the underlying engine. 

Hardest one is the moderator
* moderator_seller.txt -- moderator used when criticizing seller
* moderator_buyer.txt -- moderator used when criticizing buyer, initial version
* moderator_buyer_reason_first.txt -- moderator used when criticizing buyer, reasoning before decision, this one works better because it is a better chain-of-thought