
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

# compare different feedbacks, Claude instant
api_key=
anthropic_api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=claude-instant-v1.0            # <- seller use claude-instant-v1.0
seller_critic_engine=claude-instant-v1.0     # <- seller critic use claude-instant-v1.0
moderator_engine=gpt-3.5-turbo
verbose=1
game_version=seller_compare_feedback_500_runs_ver_1.10.0
n_round=10
n_exp=500
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

# compare different feedbacks, AI21 
api_key=
ai21_api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=j2-jumbo-instruct            # <- seller use j2-jumbo-instruct
seller_critic_engine=j2-jumbo-instruct     # <- seller critic use j2-jumbo-instruct
seller_instruction=seller_ai21
seller_critic_instruction=seller_critic_ai21
moderator_engine=gpt-3.5-turbo
verbose=1
game_version=seller_compare_feedback_200_runs_ver_1.11.0
n_round=10
n_exp=200
python run.py\
    --api_key=${api_key}\
    --ai21_api_key=${ai21_api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_instruction=${seller_instruction}\
    --seller_critic_engine=${seller_critic_engine}\
    --seller_critic_instruction=${seller_critic_instruction}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}

# compare different feedbacks, GPT-4  TODO: run this again 
api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=gpt-4                 # <- seller uses gpt-4
seller_critic_engine=gpt-4          # <- seller critic uses gpt-4
moderator_engine=gpt-3.5-turbo
verbose=1
n_exp=500
n_round=10
game_version=seller_compare_feedback_${n_exp}_runs_ver_1.12.0
nohup python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}\
    &> outputs/${game_version}.log & 
tail -f outputs/${game_version}.log

# compare different feedbacks, Claude-v1.3
api_key=
anthropic_api_key=
game_type=seller_compare_feedback
moderator_instruction=moderator_reason_multi_history
seller_engine=claude-v1.3                 
seller_critic_engine=claude-v1.3          
moderator_engine=gpt-3.5-turbo
verbose=1
n_exp=500
n_round=10
ver=1.13.0
game_version=${game_type}_${n_exp}_runs_ver_${ver}
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
    --ver=${ver}\
    --game_version=${game_version}


# compare different feedbacks, Cohere command
api_key=
cohere_api_key=
game_type=run_simple
seller_engine=cohere-command-nightly
seller_critic_engine=cohere-command-nightly
moderator_instruction=moderator_0511_cohere
moderator_engine=gpt-3.5-turbo
verbose=1
n_exp=3
n_round=10
ver=1.15.0
game_version=${game_type}_${n_exp}_runs_ver_${ver}
python run.py\
    --api_key=${api_key}\
    --cohere_api_key=${cohere_api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_exp=${n_exp}\
    --seller_engine=${seller_engine}\
    --seller_critic_engine=${seller_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --ver=${ver}\
    --game_version=${game_version}
```