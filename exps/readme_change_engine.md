# Change the underlying engine for bargaining agents

```bash
# criticize seller, change seller and critic engine to be GPT-4
api_key=
game_type=criticize_seller
moderator_instruction=moderator_reason_multi_history
verbose=1
game_version=seller_critic_gpt_4_500_runs_rollout_2_ver_1.5.0
n_round=10
n_rollout=2
n_exp=500
moderator_engine=gpt-4
seller_engine=gpt-4
seller_critic_engine=gpt-4
moderator_trace_n_history=4
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --moderator_engine=${moderator_engine}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_trace_n_history=${moderator_trace_n_history}\
    --game_version=${game_version}


# criticize buyer, change buyer and critic engine to be GPT-4
game_type=criticize_buyer
moderator_instruction=moderator_reason_multi_history
verbose=1
game_version=buyer_critic_gpt_4_500_runs_rollout_2_ver_1.6.0
n_round=10
n_rollout=2
n_exp=500
moderator_engine=gpt-4
buyer_engine=gpt-4
buyer_critic_engine=gpt-4
moderator_trace_n_history=4
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --n_rollout=${n_rollout}\
    --moderator_instruction=${moderator_instruction}\
    --moderator_engine=${moderator_engine}\
    --buyer_engine=${buyer_engine}\
    --buyer_critic_engine=${buyer_critic_engine}\
    --moderator_trace_n_history=${moderator_trace_n_history}\
    --game_version=${game_version}


# criticize buyer, change buyer and critic engine to be claude-v1.3
api_key=
anthropic_api_key=
game_type=criticize_seller
moderator_instruction=moderator_reason_multi_history
seller_engine=claude-v1.3
seller_critic_engine=claude-v1.3
moderator_engine=gpt-3.5-turbo
verbose=1
n_round=10
n_rollout=2
n_exp=500
game_version=seller_critic_claude_${n_exp}_runs_rollout_2_ver_1.7.1
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_rollout=${n_rollout}\
    --n_exp=${n_exp}\
    --seller_engine=${buyer_engine}\
    --seller_critic_engine=${buyer_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version} 

# criticize buyer, change buyer and critic engine to be claude-v1.3
api_key=
anthropic_api_key=
game_type=criticize_buyer
moderator_instruction=moderator_reason_multi_history
buyer_engine=claude-v1.3
buyer_critic_engine=claude-v1.3
moderator_engine=gpt-3.5-turbo
verbose=1
n_round=10
n_rollout=2
n_exp=500
ver=1.8.1
game_version=${game_type}_${n_exp}_runs_rollout_${n_rollout}_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_rollout=${n_rollout}\
    --n_exp=${n_exp}\
    --buyer_engine=${buyer_engine}\
    --buyer_critic_engine=${buyer_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version}
```