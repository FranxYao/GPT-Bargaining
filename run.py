import openai
import re
import time
import json

import numpy as np

from tqdm import tqdm
from pprint import pprint
from agent import (load_initial_instructions, involve_moderator, parse_final_price, 
    BuyerAgent, SellerAgent, ModeratorAgent, SellerCriticAgent, BuyerCriticAgent)


# add commandline arguments
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--seller_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--seller_critic_engine', type=str, default="gpt-3.5-turbo")

parser.add_argument('--buyer_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--buyer_instruction', type=str, default="buyer",
                    help="[buyer, buyer_no_initial_price]")
parser.add_argument('--buyer_critic_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--buyer_critic_instruction', type=str, default="buyer_critic",
                    help="[buyer_critic, buyer_critic_no_initial_price]")

parser.add_argument('--moderator_instruction', type=str, default="moderator_buyer",
                    help="[moderator_buyer, moderator_seller, moderator_buyer_reason_first]")
parser.add_argument('--moderator_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--moderator_trace_n_history', type=int, default=2,
                    help="how long the moderator trace history")

parser.add_argument('--verbose', type=int, default=1, help="0: not print, 1: print")
parser.add_argument('--api_key', type=str, default=None, help='openai api key')
parser.add_argument('--game_type', type=str, default=None, 
                    help='[criticize_seller, criticize_buyer]')
parser.add_argument('--n_exp', type=int, default=1, 
                    help='number of experiments')
parser.add_argument('--n_round', type=int, default=10, 
                    help='number of rounds')
parser.add_argument('--n_rollout', type=int, default=3, 
                    help='number of rollout')
parser.add_argument('--cost_price', type=int, default=8, 
                    help='Cost of the baloon')
parser.add_argument('--seller_init_price', type=int, default=20, 
                    help='initial seller price')
parser.add_argument('--buyer_init_price', type=int, default=10, 
                    help='initial buyer price')
parser.add_argument('--output_path', type=str, default="./outputs/", 
                    help='path to save the output')
parser.add_argument('--game_version', type=str, default="test", 
                    help='version to record the game')
args = parser.parse_args()
openai.api_key = args.api_key


# define logging
from utils import * 
logger = Logger(args.output_path + args.game_version + ".txt", args.verbose)


def run(buyer, seller, moderator, 
        n_round=10, who_is_first="seller", no_deal_thres=10):
    """Run single game.
    """
    
    if(who_is_first == "buyer"):
        seller_run = seller.last_response
        buyer_run = buyer.call(seller_run)

    logger.write('  seller: %s' % seller.last_response)
    logger.write('  buyer: %s' % buyer.last_response)
    
    logger.write('---- start bargaining ----')
    buyer_run = buyer.last_response
    start_involve_moderator = False
    deal_at = "none"
    no_deal_cnt = 0
    for _ in range(n_round):
        seller_run = seller.call(buyer_run)
        logger.write('  seller: %s' % seller.last_response)
        
        if(start_involve_moderator is False and involve_moderator(buyer_run, seller_run)):
            start_involve_moderator = True
            logger.write('---- start moderating ----')
        
        if(start_involve_moderator):
            moderate = moderator.moderate(seller.dialog_history, who_was_last="seller")
            logger.write('MODERATE have the seller and the buyer achieved a deal? Yes or No: %s' % moderate)
            if("yes" in moderate.lower()): 
                deal_at = "seller"
                break
            else: 
                no_deal_cnt += 1
                if(no_deal_cnt == no_deal_thres): break
            
        buyer_run = buyer.call(seller_run)
        logger.write('  buyer: %s' % buyer.last_response)
        
        if(start_involve_moderator is False and involve_moderator(buyer_run, seller_run)):
            start_involve_moderator = True
            logger.write('---- start moderating ----')
            
        if(start_involve_moderator):
            moderate = moderator.moderate(buyer.dialog_history, who_was_last="buyer")
            logger.write('MODERATE have the seller and the buyer achieved a deal? Yes or No: %s' % moderate)
            if("yes" in moderate.lower()): 
                deal_at = "buyer"
                break
            else: 
                no_deal_cnt += 1
                if(no_deal_cnt == no_deal_thres): break
                
    if(deal_at != "none"):
        if(deal_at == "seller"):
            final_price = parse_final_price(seller.dialog_history)
        else: 
            final_price = parse_final_price(buyer.dialog_history)
        return final_price
    else: return -1
    
# def run_w_critic(buyer, seller, moderator, critic, game_type, n_round=10, who_is_first="seller"):
#     """Run two rounds of bargaining with a critic
#     """
#     # RUN 1
#     logger.write('==== RUN 1 ====')
#     buyer.reset()
#     seller.reset()
#     moderator.reset()
#     run_1_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
#     logger.write('PRICE: %s' % run_1_price)
    
#     # Round 2 after critic
#     if(game_type == "criticize_seller"):
#         buyer.reset()
#     elif(game_type == "criticize_buyer"):
#         seller.reset()
#     else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")

#     moderator.reset()
#     if(game_type == "criticize_seller"):
#         ai_feedback = critic.criticize(seller.dialog_history)
#         logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
#         acknowledgement = seller.receive_feedback(ai_feedback, run_1_price)
#         logger.write("ACK:\n%s\n\n" % acknowledgement)
#     elif(game_type == "criticize_buyer"):
#         ai_feedback = critic.criticize(buyer.dialog_history)
#         logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
#         acknowledgement = buyer.receive_feedback(ai_feedback, run_1_price)
#         logger.write("ACK:\n%s\n\n" % acknowledgement)
#     else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")
    
#     logger.write('==== RUN 2 ====')
#     run_2_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
#     logger.write('PRICE: %s' % run_2_price)
#     return run_1_price, run_2_price

# def run_w_critic_n_exp(args, buyer, seller, moderator, critic, game_type, 
#                           n_exp=100, n_round=10, who_is_first="seller"):
#     """run multiple experiments with critic
#     """
#     run_1_prices = []
#     run_2_prices = []
#     for i in tqdm(range(n_exp)):
#         logger.write("==== CASE %d ====" % i)
#         buyer.reset()
#         seller.reset()
#         moderator.reset()
#         run_1_price, run_2_price = run_w_critic(buyer, seller, moderator, critic, game_type, 
#                                                     n_round=n_round, who_is_first=who_is_first)
#         if(check_price_range(run_1_price) and check_price_range(run_2_price)):
#             run_1_prices.append(float(run_1_price))
#             run_2_prices.append(float(run_2_price))
#         logger.write("\n\n\n\n")

#     logger.write("Run 1 price: %.2f std: %.2f" % (np.mean(run_1_prices), np.std(run_1_prices)))
#     logger.write("Run 2 price: %.2f std: %.2f" % (np.mean(run_2_prices), np.std(run_2_prices)))
#     logger.write("%d runs, %d effective" % (n_exp, len(run_1_prices)))

#     with open(args.output_path + args.game_version + "_final_prices.txt", 'w') as fd:
#         for p1, p2 in zip(run_1_prices, run_2_prices): fd.write('%.2f ; %.2f\n' % (p1, p2))
#     return

def run_w_critic_rollout(buyer, seller, moderator, critic, game_type, 
                            n_rollout=3,
                            n_round=10, who_is_first="seller"):
    """Run multiple rounds of bargaining with a critic
    """
    logger.write('==== RUN 1 ====')
    buyer.reset()
    seller.reset()
    moderator.reset()
    run_n_prices = []

    run_1_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
    logger.write('PRICE: %s' % run_1_price)
    run_n_prices.append(run_1_price)
    for i in range(n_rollout - 1):
        # Round i after critic
        if(game_type == "criticize_seller"):
            buyer.reset()
        elif(game_type == "criticize_buyer"):
            seller.reset()
        else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")

        moderator.reset()
        if(game_type == "criticize_seller"):
            ai_feedback = critic.criticize(seller.dialog_history)
            logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
            acknowledgement = seller.receive_feedback(ai_feedback, run_1_price)
            logger.write("ACK:\n%s\n\n" % acknowledgement)
        elif(game_type == "criticize_buyer"):
            ai_feedback = critic.criticize(buyer.dialog_history)
            logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
            acknowledgement = buyer.receive_feedback(ai_feedback, run_1_price)
            logger.write("ACK:\n%s\n\n" % acknowledgement)
        else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")
        
        logger.write('==== RUN %d ====' % (i + 2))
        run_i_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
        logger.write('PRICE: %s' % run_i_price)
        run_n_prices.append(run_i_price)
    return run_n_prices

def run_with_critic_infinite(args, buyer, seller, moderator, critic, game_type,
                            n_exp=100, n_rollout=3, n_round=10, who_is_first="seller"):
    """run multiple experiments with critic
    """
    round_k_prices = {k: [] for k in range(n_rollout)}

    for i in tqdm(range(n_exp)):
        logger.write("==== CASE %d ====" % i)
        buyer.reset()
        seller.reset()
        moderator.reset()
        round_prices = run_w_critic_rollout(buyer, seller, moderator, critic, game_type, 
                                            n_rollout=n_rollout,
                                            n_round=n_round, who_is_first=who_is_first)
        
        if(check_k_price_range(round_prices)):
            for k in range(n_rollout):
                round_k_prices[k].append(float(round_prices[k]))
        logger.write("\n\n\n\n")

    for k in range(n_rollout):
        logger.write("Round %d price: %.2f std: %.2f" % (k+1, np.mean(round_k_prices[k]), np.std(round_k_prices[k])))
    logger.write("%d runs, %d effective" % (n_exp, len(round_k_prices[0])))
    return 

def main(args):
    # seller init
    seller_initial_dialog_history = load_initial_instructions('instructions/seller.txt')
    print(args.seller_engine)
    seller = SellerAgent(initial_dialog_history=seller_initial_dialog_history, 
                         agent_type="seller", engine=args.seller_engine,
                         cost_price=args.cost_price, 
                         buyer_init_price=args.buyer_init_price,
                         seller_init_price=args.seller_init_price
                         )

    # buyer init
    buyer_initial_dialog_history = load_initial_instructions('instructions/%s.txt' % args.buyer_instruction)
    buyer = BuyerAgent(initial_dialog_history=buyer_initial_dialog_history, 
                       agent_type="buyer", engine=args.buyer_engine, 
                       buyer_instruction=args.buyer_instruction,
                       buyer_init_price=args.buyer_init_price,
                       seller_init_price=args.seller_init_price
                       )

    # moderator init 
    moderator_initial_dialog_history = load_initial_instructions("instructions/%s.txt" % args.moderator_instruction)
    moderator = ModeratorAgent(initial_dialog_history=moderator_initial_dialog_history, 
                               agent_type="moderator", engine=args.moderator_engine,
                               trace_n_history=args.moderator_trace_n_history
                               )

    # critic init 
    if(args.game_type == "criticize_seller"): 
         # seller critic init
        seller_critic_initial_dialog_history = load_initial_instructions('instructions/seller_critic.txt')
        seller_critic = SellerCriticAgent(initial_dialog_history=seller_critic_initial_dialog_history, 
                                agent_type="critic", engine=args.seller_critic_engine)
        critic = seller_critic
    elif(args.game_type == "criticize_buyer"): 
        # buyer critic init
        buyer_critic_initial_dialog_history = load_initial_instructions('instructions/%s.txt' % args.buyer_critic_instruction)
        buyer_critic = BuyerCriticAgent(initial_dialog_history=buyer_critic_initial_dialog_history, 
                                agent_type="critic", engine=args.buyer_critic_engine)
        critic = buyer_critic
    else: raise ValueError("game_type must be either 'criticize_seller' or 'criticize_buyer'")

    # run
    who_is_first = "seller"
    if(args.buyer_instruction == "buyer_no_initial_price"): who_is_first = "buyer"
    # run_w_critic_n_exp(args, buyer, seller, moderator, critic, 
    #                       game_type=args.game_type, n_exp=args.n_exp, n_round=args.n_round,
    #                       who_is_first=who_is_first)
    run_with_critic_infinite(args, buyer, seller, moderator, critic, 
                            game_type=args.game_type, n_exp=args.n_exp, 
                            n_rollout=args.n_rollout, n_round=args.n_round,
                            who_is_first=who_is_first)
    return 

if __name__ == "__main__":
    main(args)