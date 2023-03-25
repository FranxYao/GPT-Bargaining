# Run simulation

```bash
api_key=
python scripts/test_moderator.py --api_key=${api_key}
```

# Run Bard simulation

The Bard simulation is adapted from [LarryDpk]('https://github.com/LarryDpk')'s work on [google-bard-python-chatbot]('https://github.com/LarryDpk/pkslow-samples/blob/master/python/src/main/python/google-bard-python-chatbot/Bard.py'). There are two files, `bard.py` and `bard_interactive.py`. The first is a vanilla Bard class while the second is a dialogue simulator of the bard website. To run the dialogue simulator, first install any missing dependencies with

```bash
pip install -r bard_requirements.txt
```

To use Bard you need a session key from the Bard site. The steps are described in [LarryDpk's blog]('https://www.cnblogs.com/larrydpk/p/17250015.html'). Basically you need to open the Bard site in a browser, open the developer tools and go to the Application tab. Click Cookies -> https://bard.google.com -> sessionid and find the key with name '__Secure-1PSID'. Copy the value of this key and use it as the '--session' argument to run `bard_interactive.py`. For example:
```bash
python bard_interactive.py --session <your_copied_cookie>
```
`bard.py` has a class BardChatbot with a method `ask(question: str)` which takes a question and returns a response. 