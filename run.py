import openai
import ai21
import re
import time
import json
import sys
import copy
import random

import numpy as np

from tqdm import tqdm
from pprint import pprint
from agent import (load_initial_instructions, involve_moderator, parse_final_price, 
    BuyerAgent, SellerAgent, ModeratorAgent, SellerCriticAgent, BuyerCriticAgent)
from utils import * 

CONST_CRITIC_PATH = "lib_prompt/constant_feedback.txt"
HUMAN_CRITIC_PATH = "lib_prompt/human_feedback_seller.txt"

import argparse

def define_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--item', type=str, default="balloon")

    # seller arguments
    parser.add_argument('--seller_engine', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--seller_instruction', type=str, default="seller")
    parser.add_argument('--seller_feedback_instruction', type=str, default="seller_receive_feedback")

    parser.add_argument('--seller_critic_engine', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--seller_critic_instruction', type=str, default="seller_critic")

    # buyer arguments
    parser.add_argument('--buyer_engine', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--buyer_instruction', type=str, default="buyer",
                        help="[buyer, buyer_no_initial_price]")

    parser.add_argument('--buyer_critic_engine', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--buyer_critic_instruction', type=str, default="buyer_critic",
                        help="[buyer_critic, buyer_critic_no_initial_price]")

    # moderator arguments
    parser.add_argument('--moderator_instruction', type=str, default="moderator_buyer",
                        help="[moderator_buyer, moderator_seller, moderator_buyer_reason_first]")
    parser.add_argument('--moderator_engine', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--moderator_trace_n_history', type=int, default=5,
                        help="how long the moderator trace history")

    # api keys
    parser.add_argument('--api_key', type=str, default=None, help='openai api key')
    parser.add_argument('--anthropic_api_key', type=str, default=None, help='anthropic api key')
    parser.add_argument('--ai21_api_key', type=str, default=None, help='ai21 api key')
    parser.add_argument('--cohere_api_key', type=str, default=None, help='cohere api key')

    # game arguments
    parser.add_argument('--game_type', type=str, default=None, 
                        help='[criticize_seller, criticize_buyer, seller_compare_feedback]')
    parser.add_argument('--n_exp', type=int, default=1, 
                        help='number of experiments')
    parser.add_argument('--n_round', type=int, default=10, 
                        help='number of rounds')
    parser.add_argument('--n_rollout', type=int, default=3, 
                        help='number of rollout')
    parser.add_argument('--cost_price', type=int, default=8, 
                        help='Cost of the balloon')
    parser.add_argument('--seller_init_price', type=int, default=20, 
                        help='initial seller price')
    parser.add_argument('--buyer_init_price', type=int, default=10, 
                        help='initial buyer price')
    parser.add_argument('--who_is_first', type=str, default="seller", 
                        help='initial buyer price')
    parser.add_argument('--restrict_price', type=str, default="true", 
                        help='initial buyer price')

    parser.add_argument('--verbose', type=int, default=1, help="0: not logger.write, 1: logger.write")
    parser.add_argument('--output_path', type=str, default="./outputs/", 
                        help='path to save the output')
    parser.add_argument('--ver', type=str, default="test", 
                        help='version to record the game')
    parser.add_argument('--game_version', type=str, default="test", 
                        help='version plus arguments')

    # parse and set arguments
    args = parser.parse_args()

    openai.api_key = args.api_key
    ai21.api_key = args.ai21_api_key
    return args


def get_engine_and_api_key(agent_type, engine_name, args):
    """Get engine for players and critic
    agent_type: [seller, buyer, seller_critic, buyer_critic, moderator]
    engine_name: [gpt-3.5-turbo, gpt-4, claude-v1.0, claude-v1.3, claude-instant-v1.0]
    """
    engine_map = {  "seller": SellerAgent, 
                    "buyer":  BuyerAgent, 
                    "seller_critic": SellerCriticAgent, 
                    "buyer_critic":  BuyerCriticAgent,
                    "moderator": ModeratorAgent
                  }

    if("gpt" in engine_name): 
        api_key = args.api_key
    elif("claude" in engine_name): 
        api_key = args.anthropic_api_key
    elif("j2" in engine_name):
        api_key = args.ai21_api_key
    elif("cohere" in engine_name):
        api_key = args.cohere_api_key
    else: 
        raise ValueError("engine name %s not found" % engine_name)

    engine_class = engine_map[agent_type]

    return engine_class, api_key


def run(buyer, seller, moderator, 
        n_round=10, who_is_first="seller", no_deal_thres=10):
    """Run single game.
    """
    import ipdb; ipdb.set_trace()
    if(who_is_first == "buyer"):
        logger.write('  buyer: %s' % buyer.last_response)
        logger.write('  seller: %s' % seller.last_response)
        logger.write('---- start bargaining ----')
        seller_run = seller.last_response
        buyer_run = buyer.call(seller_run)
        logger.write('  buyer: %s' % buyer.last_response)
    else:
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
    
def run_compare_critic_single(buyer, seller, moderator, critic,
                       const_feedback, human_feedback_pool, 
                       game_type, n_round=10, who_is_first="seller"):
    """Run with multiple types of critic then compare the effect of different critics
    """
    logger.write('==== RUN 1 ====')
    buyer.reset()
    seller.reset()
    moderator.reset()
    run_n_prices, run_n_prices_const, run_n_prices_human = [], [], [] 

    run_1_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
    logger.write('PRICE: %s' % run_1_price)
    run_n_prices.append(run_1_price)
    run_n_prices_const.append(run_1_price)
    run_n_prices_human.append(run_1_price)
    
    # Round 2 after critic
    logger.write('==== RUN 2 ====')

    if(game_type == "seller_compare_feedback"):
        seller_hear_const = copy.deepcopy(seller)
        seller_hear_human = copy.deepcopy(seller)

        # ai feedback 
        buyer.reset()
        moderator.reset()

        ai_feedback = critic.criticize(seller.dialog_history)
        
        logger.write("AI FEEDBACK:\n%s\n" % ai_feedback)
        acknowledgement = seller.receive_feedback(ai_feedback, run_1_price)
        logger.write("ACK:\n%s\n\n" % acknowledgement)
        run_2_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
        logger.write('PRICE: %s' % run_2_price)
        run_n_prices.append(run_2_price)

        # const feedback
        buyer.reset()
        moderator.reset()
        logger.write("\n\nCONST FEEDBACK:\n%s\n" % const_feedback)
        acknowledgement = seller_hear_const.receive_feedback(const_feedback, run_1_price)
        logger.write("ACK:\n%s\n\n" % acknowledgement)
        run_2_price = run(buyer, seller_hear_const, moderator, n_round=n_round, who_is_first=who_is_first)
        logger.write('PRICE: %s' % run_2_price)
        run_n_prices_const.append(run_2_price)

        # human feedback
        buyer.reset()
        moderator.reset()
        human_feedback = random.choice(human_feedback_pool)
        logger.write("\n\nHUMAN FEEDBACK:\n%s\n" % human_feedback)
        acknowledgement = seller_hear_human.receive_feedback(human_feedback, run_1_price)
        logger.write("ACK:\n%s\n\n" % acknowledgement)
        run_2_price = run(buyer, seller_hear_human, moderator, n_round=n_round, who_is_first=who_is_first)
        logger.write('PRICE: %s' % run_2_price)
        run_n_prices_human.append(run_2_price)

    elif(game_type == "buyer_compare_feedback"):
        raise NotImplementedError("buyer_compare_feedback not implemented yet")
    else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")
    
    return run_n_prices, run_n_prices_const, run_n_prices_human

def run_compare_critic(args, buyer, seller, moderator, critic, 
                            const_feedback, human_feedback_pool, 
                            game_type,
                            n_exp=100, n_round=10, who_is_first="seller"):
    """run multiple experiments with multiple types of critic
    """
    prices_ai_critic, prices_const_critic, prices_human_critic = [], [], []

    start_time = time.time()
    for i in range(n_exp):
        logger.write("==== ver %s CASE %d / %d, %.2f min ====" % (args.ver, i, n_exp, compute_time(start_time)))
        buyer.reset()
        seller.reset()
        moderator.reset()
        ai_price, const_price, human_price = run_compare_critic_single(buyer, seller, moderator, critic, 
                                            const_feedback, human_feedback_pool,
                                            game_type=game_type, 
                                            n_round=n_round, who_is_first=who_is_first)
        
        if(check_k_price_range(ai_price, p_min=args.buyer_init_price, p_max=args.seller_init_price) and 
           check_k_price_range(const_price, p_min=args.buyer_init_price, p_max=args.seller_init_price) and 
           check_k_price_range(human_price, p_min=args.buyer_init_price, p_max=args.seller_init_price)
           ):
            prices_ai_critic.append(ai_price)
            prices_const_critic.append(const_price)
            prices_human_critic.append(human_price)
            assert(ai_price[0] == const_price[0] == human_price[0])
        logger.write("\n\n\n\n")

    round_0_price = [price[0] for price in prices_ai_critic]
    round_1_price_ai_critic = [price[1] for price in prices_ai_critic]
    round_1_price_const_critic = [price[1] for price in prices_const_critic]
    round_1_price_human_critic = [price[1] for price in prices_human_critic]

    logger.write("Round 0 price:              %.2f std: %.2f" % 
                 (np.mean(round_0_price), np.std(round_0_price))
                 )
    logger.write("Round 1 price ai critic:    %.2f std: %.2f" % 
                 (np.mean(round_1_price_ai_critic), np.std(round_1_price_ai_critic))
                 )
    logger.write("Round 1 price const critic: %.2f std: %.2f" % 
                 (np.mean(round_1_price_const_critic), np.std(round_1_price_const_critic))
                 )
    logger.write("Round 1 price human critic: %.2f std: %.2f" % 
                 (np.mean(round_1_price_human_critic), np.std(round_1_price_human_critic))
                 )
    logger.write("%d runs, %d effective" % (n_exp, len(prices_ai_critic)))
    return 


def run_simple(args, buyer, seller, moderator,
                n_exp=100, n_round=10, who_is_first="seller"):
    """run multiple experiments without critic, simply checking if the model can play the game
    """
    start_time = time.time()
    for i in range(n_exp):
        logger.write("==== ver %s CASE %d / %d, %.2f min ====" % (args.ver, i, n_exp, compute_time(start_time)))
        buyer.reset()
        seller.reset()
        moderator.reset()
        price = run(buyer, seller, moderator)
        logger.write("\n\n\n\n")
    return 

def run_w_critic_rollout(args, buyer, seller, moderator, critic, game_type, 
                            n_rollout=3,
                            n_round=10, who_is_first="seller"):
    """Run multiple rounds of bargaining with one single critic
    """
    logger.write('==== RUN 1 ====')
    # import ipdb; ipdb.set_trace()

    buyer.reset()
    seller.reset()
    moderator.reset()
    run_n_prices = []

    run_1_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_first)
    logger.write('PRICE: %s' % run_1_price)
    run_n_prices.append(run_1_price)
    previous_price = run_1_price
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
            acknowledgement, who_is_next = seller.receive_feedback(ai_feedback, previous_price)
            logger.write("ACK:\n%s\n\n" % acknowledgement)
        elif(game_type == "criticize_buyer"):
            ai_feedback = critic.criticize(buyer.dialog_history)
            logger.write("FEEDBACK:\n%s\n\n" % ai_feedback)
            # TODO: update who is first based on response from feedback
            acknowledgement, who_is_next = buyer.receive_feedback(ai_feedback, previous_price)
            logger.write("ACK:\n%s\n\n" % acknowledgement)
        else: raise ValueError("game_type must be either 'critize_seller' or 'critize_buyer'")
        
        logger.write('==== RUN %d ====' % (i + 2))
        run_i_price = run(buyer, seller, moderator, n_round=n_round, who_is_first=who_is_next)
        logger.write('PRICE: %s' % run_i_price)

        if(args.restrict_price == "true" and check_price_range(
            run_i_price, p_min=args.buyer_init_price, p_max=args.seller_init_price) == False
            ):
            logger.write("run %d did not get a deal, stop unroll" % (i + 2))
            break

        run_n_prices.append(run_i_price)
        previous_price = run_i_price
    return run_n_prices

def run_with_critic(args, buyer, seller, moderator, critic, game_type,
                            n_exp=100, n_rollout=3, n_round=10, who_is_first="seller"):
    """run multiple experiments with one single critic
    """
    round_k_prices = {k: [] for k in range(n_rollout)}

    # for i in tqdm(range(n_exp)):
    start_time = time.time()
    for i in range(n_exp):
        logger.write("==== ver %s CASE %d / %d | %.2f min ====" % (args.ver, i, n_exp, compute_time(start_time)))
        buyer.reset()
        seller.reset()
        moderator.reset()
        round_prices = run_w_critic_rollout(args, buyer, seller, moderator, critic, game_type, 
                                            n_rollout=n_rollout,
                                            n_round=n_round, who_is_first=who_is_first)
        # if(len(round_prices) == 5):
        
        # if(check_k_price_range(round_prices)):
            # for k in range(n_rollout):
            # for k in range(len(round_prices)):
            #     round_k_prices[k].append(float(round_prices[k]))
            #     logger.write("%.2f" % round_prices[k])

        logger.write("Price trace:")
        for k in range(len(round_prices)):
            round_k_prices[k].append(float(round_prices[k]))
            logger.write("%.2f" % round_prices[k])
        logger.write("\n\n\n\n")

    for k in range(n_rollout):
        logger.write("Round %d price: %.2f std: %.2f" % (k+1, np.mean(round_k_prices[k]), np.std(round_k_prices[k])))
    logger.write("%d runs, %d effective" % (n_exp, len(round_k_prices[0])))
    return 

def main(args):
    # seller init
    seller_initial_dialog_history = load_initial_instructions('lib_prompt/%s.txt' % args.seller_instruction)
    seller_engine_class, seller_api_key = get_engine_and_api_key(engine_name=args.seller_engine,
                                                            agent_type="seller", args=args
                                                            )
    feedback_instruction = open('lib_prompt/%s.txt' % args.seller_feedback_instruction).read()
    seller = seller_engine_class(initial_dialog_history=seller_initial_dialog_history, 
                                 item=args.item,
                                agent_type="seller", engine=args.seller_engine, api_key=seller_api_key,
                                feedback_instruction=feedback_instruction,
                                cost_price=args.cost_price, 
                                buyer_init_price=args.buyer_init_price,
                                seller_init_price=args.seller_init_price
                                )

    # buyer init
    buyer_initial_dialog_history = load_initial_instructions('lib_prompt/%s.txt' % args.buyer_instruction)
    buyer_engine_class, buyer_api_key = get_engine_and_api_key(engine_name=args.buyer_engine,
                                                            agent_type="buyer", args=args
                                                            )
    buyer = buyer_engine_class(initial_dialog_history=buyer_initial_dialog_history, 
                               item=args.item,
                                agent_type="buyer", engine=args.buyer_engine, api_key=buyer_api_key,
                                buyer_instruction=args.buyer_instruction,
                                buyer_init_price=args.buyer_init_price,
                                seller_init_price=args.seller_init_price
                                )

    # moderator init 
    moderator_initial_dialog_history = load_initial_instructions("lib_prompt/%s.txt" % args.moderator_instruction)
    moderator_engine_class, moderator_api_key = get_engine_and_api_key(engine_name=args.moderator_engine,
                                                                    agent_type="moderator", args=args
                                                                    )
    moderator = moderator_engine_class(initial_dialog_history=moderator_initial_dialog_history, 
                            agent_type="moderator", engine=args.moderator_engine, api_key=moderator_api_key,
                            trace_n_history=args.moderator_trace_n_history
                            )

    # critic init 
    if(args.game_type in ["criticize_seller", "seller_compare_feedback"]): 
         # seller critic init
        seller_critic_initial_dialog_history = load_initial_instructions('lib_prompt/%s.txt' % args.seller_critic_instruction)
        seller_critic_engine_class, seller_critic_api_key = get_engine_and_api_key(engine_name=args.seller_critic_engine,
                                                                                agent_type="seller_critic", args=args
                                                                                )
        seller_critic = seller_critic_engine_class(initial_dialog_history=seller_critic_initial_dialog_history, 
                                    agent_type="critic", engine=args.seller_critic_engine, api_key=seller_critic_api_key
                                    )
        critic = seller_critic
    elif(args.game_type == "criticize_buyer"): 
        # buyer critic init
        buyer_critic_initial_dialog_history = load_initial_instructions('lib_prompt/%s.txt' % args.buyer_critic_instruction)
        buyer_critic_engine_class, buyer_api_key = get_engine_and_api_key(engine_name=args.buyer_critic_engine,
                                                                        agent_type="buyer_critic", args=args
                                                                        )
        buyer_critic = buyer_critic_engine_class(initial_dialog_history=buyer_critic_initial_dialog_history, 
                                    agent_type="critic", engine=args.buyer_critic_engine, api_key=buyer_api_key
                                    )
        critic = buyer_critic
    elif(args.game_type == "run_simple"): pass
    else: raise ValueError("game_type must be in ['criticize_seller', 'criticize_buyer', 'seller_compare_feedback', 'run_simple']")

    # # run
    # who_is_first = "seller"
    # # TODO: update this argument because it is confusing
    # if(args.buyer_instruction == "buyer_no_initial_price"): who_is_first = "buyer"

    if(args.game_type in ["criticize_seller", "criticize_buyer"]):
        run_with_critic(args, buyer, seller, moderator, critic, 
                                game_type=args.game_type, n_exp=args.n_exp, 
                                n_rollout=args.n_rollout, n_round=args.n_round,
                                who_is_first=args.who_is_first)
    elif(args.game_type == "seller_compare_feedback"):
        const_feedback = open(CONST_CRITIC_PATH).read().strip()
        human_feedback_pool = open(HUMAN_CRITIC_PATH).read().strip().split("\n")
        run_compare_critic(args, buyer, seller, moderator, critic, 
                            const_feedback, human_feedback_pool, 
                            game_type=args.game_type, n_exp=args.n_exp, 
                            n_round=args.n_round,
                            who_is_first=args.who_is_first)
    elif(args.game_type == "run_simple"):
        run_simple(args, buyer, seller, moderator, n_exp=args.n_exp)
    return 

if __name__ == "__main__":
    args = define_arguments()
    logger = Logger(args.output_path + args.game_version + ".txt", args.verbose)
    main(args)