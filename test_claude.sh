api_key=
game_type=criticize_seller
moderator_instruction=moderator_buyer_reason_first
seller_engine=claude-v1
verbose=1
game_version=seller_critic_100_runs_0.5.0
n_round=100
n_exp=1
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}