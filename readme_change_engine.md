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
```