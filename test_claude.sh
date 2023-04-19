#!/bin/bash
#SBATCH --output=/home/%u/GPT-Bargaining/logs/buyer_critic_claude_500_runs_rollout_2_ver_1.8.0.out
#SBATCH --error=/home/%u/GPT-Bargaining/logs/buyer_critic_claude_500_runs_rollout_2_ver_1.8.0.out
#SBATCH --job-name=buyer_critic_claude_500_runs_rollout_2_ver_1.8.0
#SBATCH --nodes=1
#SBATCH --mem=16g
#SBATCH --cpus-per-task=4
#SBATCH --time=36:00:00
#SBATCH --array=0

api_key=
game_type=criticize_buyer
moderator_instruction=moderator_buyer_reason_first
buyer_engine=claude-v1.3
buyer_critic_engine=claude-v1.3
moderator_engine=gpt-4
verbose=1
game_version=buyer_critic_claude_500_runs_rollout_2_ver_1.8.0
n_round=10
n_rollout=2
n_exp=500
python run.py\
    --api_key=${api_key}\
    --game_type=${game_type}\
    --verbose=${verbose}\
    --n_round=${n_round}\
    --n_rollout=${n_rollout}\
    --n_exp=${n_exp}\
    --buyer_engine=${buyer_engine}\
    --buyer_critic_engine=${buyer_critic_engine}\
    --moderator_engine=${moderator_engine}\
    --moderator_instruction=${moderator_instruction}\
    --game_version=${game_version}