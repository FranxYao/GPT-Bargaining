
```bash 

# compare different feedbacks, GPT-3.5-Turbo
api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=gpt-3.5-turbo
seller_critic_engine=gpt-3.5-turbo
moderator_engine=gpt-3.5-turbo
verbose=1
game_version=seller_compare_feedback_500_runs_ver_1.9.0
n_round=10
n_exp=750
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}

# compare different feedbacks, GPT-4
api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=gpt-4
seller_critic_engine=gpt-4
moderator_engine=gpt-3.5-turbo
verbose=1
game_version=seller_compare_feedback_500_runs_ver_1.10.0
n_round=10
n_exp=250
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}

# compare different feedbacks, Claude instant
api_key=
anthropic_api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=claude-instant-v1.0
seller_critic_engine=claude-instant-v1.0
moderator_engine=gpt-3.5-turbo
verbose=1
game_version=seller_compare_feedback_500_runs_ver_1.10.0
n_round=10
n_exp=3
python run.py\
    --api_key=${api_key}\
    --anthropic_api_key=${anthropic_api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}
```