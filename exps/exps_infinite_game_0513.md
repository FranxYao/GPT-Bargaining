
```bash
# Claude v1.3 100k criticize seller, unroll 50
api_key=
anthropic_api_key=
game_type=criticize_seller
seller_instruction=seller_diamond
seller_engine=claude-v1.3-100k
seller_critic_instruction=seller_critic_diamond
seller_critic_engine=claude-v1.3-100k
buyer_instruction=buyer_diamond
buyer_engine=claude-v1.3-100k
moderator_instruction=moderator_0513_diamond
cost_price=50
seller_init_price=2000
buyer_init_price=500
verbose=1
n_round=10
n_rollout=50
n_exp=20
ver=0.4.0.0
game_version=${game_type}_${n_exp}_runs_${n_rollout}_rollout_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --seller_instruction=${seller_instruction}\
    --seller_engine=${seller_engine}\
    --seller_critic_instruction=${seller_critic_instruction}\
    --seller_critic_engine=${seller_critic_engine}\
    --buyer_instruction=${buyer_instruction}\
    --buyer_engine=${buyer_engine}\
    --cost_price=${cost_price}\
    --seller_init_price=${seller_init_price}\
    --buyer_init_price=${buyer_init_price}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version} 
```