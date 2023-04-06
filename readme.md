# Run simulation

Run the game 
```bash

# buyer fix initial price to be $10
api_key=
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
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

# repeat 500 times
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
verbose=1
game_version=buyer_critic_500_runs_0.1.1
n_round=10
n_exp=500
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}

# repeat 500 times, prompt add "get lower price"
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
buyer_critic_instruction=buyer_critic_lower_price
verbose=1
game_version=buyer_critic_500_runs_0.1.2
n_round=10
n_exp=500
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --buyer_critic_instruction=${buyer_critic_instruction}\
    --game_version=${game_version}

# buyer do not fix initial price
api_key=
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
buyer_instruction=buyer_no_initial_price
buyer_critic_instruction=buyer_critic_no_initial_price
verbose=1
game_version=buyer_critic_100_runs_0.2
n_round=10
n_exp=100
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --buyer_instruction=${buyer_instruction}\
    --game_version=${game_version}

# buyer engine change to GPT-4
api_key=
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
verbose=1
game_version=buyer_critic_100_runs_0.3
n_round=10
n_exp=100
buyer_engine=gpt-4
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --buyer_engine=${buyer_engine}\
    --game_version=${game_version}

# criticize seller, 500 runs 
game_type=criticize_seller
moderator_instruction=moderator_buyer_reason_first
verbose=1
game_version=seller_critic_500_runs_0.5.0
n_round=10
n_exp=500
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}

# criticize seller, 500 runs, rollout 3
api_key=
game_type=criticize_seller
moderator_instruction=moderator_buyer_reason_first
verbose=1
game_version=seller_critic_500_runs_rollout_3_0.5.1
n_round=10
n_rollout=3
n_exp=500
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}
```

Test scripts
```bash
api_key=
python scripts/test_moderator.py --api_key=${api_key}
```