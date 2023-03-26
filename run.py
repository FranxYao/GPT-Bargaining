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
parser.add_argument('--buyer_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--seller_critic_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--buyer_critic_engine', type=str, default="gpt-3.5-turbo")
parser.add_argument('--moderator_instruction', type=str, default="moderator_buyer")

parser.add_argument('--verbose', type=int, default=1, help="0: not print, 1: print")
parser.add_argument('--api_key', type=str, default=None, help='openai api key')
parser.add_argument('--game_type', type=str, default=None, 
                    help='[criticize_seller, criticize_buyer]')
parser.add_argument('--n_exp', type=int, default=1, 
                    help='number of experiments')
parser.add_argument('--n_round', type=int, default=10, 
                    help='number of rounds')
parser.add_argument('--output_path', type=str, default="./outputs/", 
                    help='path to save the output')
parser.add_argument('--game_version', type=str, default="test", 
                    help='version to record the game')
args = parser.parse_args()
openai.api_key = args.api_key

# define logging
from utils import * 
logger = Logger(args.output_path + args.game_version + ".txt", args.verbose)


def run(buyer, seller, moderator, n_round=10):
    logger.write('  seller: %s' % seller.last_response)
    logger.write('  buyer: %s' % buyer.last_response)
    
    logger.write('---- start bargaining ----')
    buyer_run = buyer.last_response
    start_involve_moderator = False
    deal_at = "none"
    for _ in range(n_round):
        seller_run = seller.call(buyer_run)
        logger.write('  seller: %s' % seller.last_response)
        
        if(start_involve_moderator is False and involve_moderator(buyer_run, seller_run)):
            start_involve_moderator = True
            logger.write('---- start moderating ----')
        
        if(start_involve_moderator):
            moderate = moderator.moderate(seller.last_response, buyer.last_response, who_is_first="buyer", debug=False)
            logger.write('MODERATE have the seller and the buyer achieved a deal? Yes or No: %s' % moderate)
            if("yes" in moderate.lower()): 
                deal_at = "seller"
                break
            else: pass
            
        buyer_run = buyer.call(seller_run)
        logger.write('  buyer: %s' % buyer.last_response)
        
        if(start_involve_moderator is False and involve_moderator(buyer_run, seller_run)):
            start_involve_moderator = True
            logger.write('---- start moderating ----')
            
        if(start_involve_moderator):
            moderate = moderator.moderate(seller.last_response, buyer.last_response, who_is_first="seller", debug=False)
            logger.write('MODERATE have the seller and the buyer achieved a deal? Yes or No: %s' % moderate)
            if("yes" in moderate.lower()): 
                deal_at = "buyer"
                break
            else: pass
                
    if(deal_at != "none"):
        if(deal_at == "seller"):
            final_price = parse_final_price(seller.dialog_history)
        else: 
            final_price = parse_final_price(buyer.dialog_history)
        return final_price
    else: return -1
    
def run_w_critic(buyer, seller, moderator, critic, game_type, n_round=10):
    # Round 1
    logger.write('==== ROUND 1 ====')
    buyer.reset()
    seller.reset()
    moderator.reset()
    round_1_price = run(buyer, seller, moderator, n_round=n_round)
    logger.write('PRICE: %s' % round_1_price)
    
    # Round 2 after critic
    if(game_type == "criticize_seller"):
        buyer.reset()
    elif(game_type == "criticize_buyer"):
        seller.reset()
    else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")

    moderator.reset()
    if(game_type == "criticize_seller"):
        ai_feedback = critic.criticize(seller.dialog_history)
        logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
        acknowledgement = seller.receive_feedback(ai_feedback, round_1_price)
        logger.write("ACK:\n%s\n\n" % acknowledgement)
    elif(game_type == "criticize_buyer"):
        ai_feedback = critic.criticize(buyer.dialog_history)
        logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
        acknowledgement = buyer.receive_feedback(ai_feedback, round_1_price)
        logger.write("ACK:\n%s\n\n" % acknowledgement)
    else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")
    
    logger.write('==== ROUND 2 ====')
    round_2_price = run(buyer, seller, moderator, n_round=n_round)
    logger.write('PRICE: %s' % round_2_price)
    return round_1_price, round_2_price

def run_w_critic_multiple(args, buyer, seller, moderator, critic, game_type, n_exp=100, n_round=10):
    round_1_prices = []
    round_2_prices = []
    for i in tqdm(range(n_exp)):
        logger.write("==== CASE %d ====" % i)
        buyer.reset()
        seller.reset()
        moderator.reset()
        round_1_price, round_2_price = run_w_critic(buyer, seller, moderator, critic, game_type, n_round=n_round)
        if(check_price_range(round_1_price) and check_price_range(round_2_price)):
            round_1_prices.append(float(round_1_price))
            round_2_prices.append(float(round_2_price))
        logger.write("\n\n\n\n")

    print("Round 1 price: %.2f std: %.2f" % (np.mean(round_1_prices), np.std(round_1_prices)))
    print("Round 2 price: %.2f std: %.2f" % (np.mean(round_2_prices), np.std(round_2_prices)))
    print("%d runs, %d effective" % (n_exp, len(round_1_prices)))

    with open(args.output_path + args.game_version + "_final_prices.txt", 'w') as fd:
        for p1, p2 in zip(round_1_prices, round_2_prices): fd.write('%.2f ; %.2f\n' % (p1, p2))
    return

def main(args):
    # seller init
    seller_initial_dialog_history = load_initial_instructions('instructions/seller.txt')
    seller = SellerAgent(initial_dialog_history=seller_initial_dialog_history, 
                         agent_type="seller", engine=args.seller_engine)

    # seller critic init
    seller_critic_initial_dialog_history = load_initial_instructions('instructions/critic_seller.txt')
    seller_critic = SellerCriticAgent(initial_dialog_history=seller_critic_initial_dialog_history, 
                               agent_type="critic", engine=args.seller_critic_engine)

    # buyer init
    buyer_initial_dialog_history = load_initial_instructions('instructions/buyer.txt')
    buyer = BuyerAgent(initial_dialog_history=buyer_initial_dialog_history, 
                       agent_type="buyer", engine=args.buyer_engine)

    # buyer critic init
    buyer_critic_initial_dialog_history = load_initial_instructions('instructions/critic_buyer.txt')
    buyer_critic = BuyerCriticAgent(initial_dialog_history=buyer_critic_initial_dialog_history, 
                               agent_type="critic", engine=args.buyer_critic_engine)

    # moderator init 
    moderator_initial_dialog_history = load_initial_instructions("instructions/%s.txt" % args.moderator_instruction)
    moderator = ModeratorAgent(initial_dialog_history=moderator_initial_dialog_history, 
                               agent_type="moderator", engine="gpt-3.5-turbo")

    # critic init 
    if(args.game_type == "criticize_seller"): critic = seller_critic
    elif(args.game_type == "criticize_buyer"): critic = buyer_critic
    else: raise ValueError("game_type must be either 'criticize_seller' or 'criticize_buyer'")

    # run
    run_w_critic_multiple(args, buyer, seller, moderator, critic, 
                          game_type=args.game_type, n_exp=args.n_exp, n_round=args.n_round)
    return 

if __name__ == "__main__":
    main(args)