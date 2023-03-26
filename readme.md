# Run simulation

Run the game 
```bash
api_key=
game_type=criticize_buyer
moderator_instruction=moderator_buyer
verbose=1
game_version=buyer_critic_100_runs_0.1
n_round=20
n_exp=100
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}
```

Test scripts
```bash
api_key=
python scripts/test_moderator.py --api_key=${api_key}
```