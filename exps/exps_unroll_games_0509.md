
```bash
# gpt3.5 criticize seller, unroll 5
api_key=
game_type=criticize_seller
moderator_instruction=moderator_0509
verbose=1
n_round=10
n_rollout=5
n_exp=200
ver=0.3.0.0
game_version=${game_type}_${n_exp}_runs_${n_rollout}_rollout_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version} 

# gpt3.5 criticize buyer, unroll 5
api_key=
game_type=criticize_buyer
moderator_instruction=moderator_0509
verbose=1
n_round=10
n_rollout=5
n_exp=200
ver=0.3.1.0
game_version=${game_type}_${n_exp}_runs_${n_rollout}_rollout_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version} 

# claude criticize seller, unroll 5
api_key=
anthropic_api_key=
game_type=criticize_seller
moderator_instruction=moderator_0509
verbose=1
n_round=10
n_rollout=5
n_exp=200
ver=0.3.2.0
seller_engine=claude-instant-v1.0
seller_critic_engine=claude-instant-v1.0
game_version=${game_type}_${n_exp}_runs_${n_rollout}_rollout_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version} 

# claude criticize buyer, unroll 5
api_key=
anthropic_api_key=
game_type=criticize_buyer
moderator_instruction=moderator_0509
verbose=1
n_round=10
n_rollout=5
n_exp=200
ver=0.3.3.0
buyer_engine=claude-instant-v1.0
buyer_critic_engine=claude-instant-v1.0
game_version=${game_type}_${n_exp}_runs_${n_rollout}_rollout_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --buyer_engine=${buyer_engine}\
    --buyer_critic_engine=${buyer_critic_engine}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version} 
```