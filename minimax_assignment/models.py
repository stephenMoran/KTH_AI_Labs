
import random
import math, time
import numpy as np
import random, string
from fishing_game_core.shared import ACTION_TO_STR

class MinimaxModel(object): 
    def __init__(self, initial_data,space_subdivisions): 
        self.get_fish_scores_and_types(initial_data)
        self.space_subdivisions = space_subdivisions
        self.max_time =  0.055
        self.states = {}
        return None

    def get_fish_scores_and_types(self, data):
        data.pop('game_over', None)
        self.fish_scores = {int(key.split('fish')[1]):value['score'] for key, value in data.items()}
        scores_to_type = {s:t for t, s in enumerate(set(self.fish_scores.values()))}
        self.fish_types = {f:scores_to_type[s] for f, s in self.fish_scores.items()}

    def next_move(self, root_node, max_depth=7): 
         self.start = time.time()
        alpha = -math.inf
        beta = math.inf
        #self.max_depth = max_depth
        #self.max_player = root_node.state.player
        depth = 0
        actions = root_node.compute_and_get_children()
    
        #best_move = 0
        #best_moves = {}
        time_left = True
        #(depth <= max_depth) and (time.time() < self.start + self.max_time)
        while time_left:
            best_value = 0
            try:
                for a in actions: 
                    value = self.min_value(depth, a, alpha, beta)
                    if value > best_value: 
                        best_value = value
                        best_move = a.move
                """
                best_moves[depth] = (best_value, best_move)
                depth += 1
                optimal_index = max(best_moves, key=best_moves.get)
                optimal_action = best_moves[optimal_index][1]
                """

                optimal_action = best_move
            except TimeoutError: 
                time_left = False
        return ACTION_TO_STR[optimal_action]

    def max_value(self, depth, node, alpha=0, beta=0): 
        key = self.hash_funct(node.state)
        if key in self.states:
            return self.states[key]
        actions = node.compute_and_get_children()
        value = -math.inf
        actions.sort(key=self.compute_heuristic, reverse = True)
        if depth == 0 or (len(actions) == 0): 
            return self.compute_heuristic(node)
        else: 
            for a in actions:
                value = max(value, self.min_value(depth - 1, a, alpha, beta))
                if value >= beta: 
                    break
                alpha = max(alpha,value)
                if time.time() - self.start > self.max_time:
                    break
        self.states[key] = [depth,value]
        return value
        
    def min_value(self, depth, node, alpha=0, beta=0):
        key = self.hash_funct(node.state)
        if key in self.states:
          return self.states[key]
        actions = node.compute_and_get_children()
        value = math.inf
        actions.sort(key=self.compute_heuristic, reverse = True)
        if depth == 0 or (len(actions) == 0): 
            return self.compute_heuristic(node)
        else: 
            for a in actions: 
                value = min(value, self.max_value(depth - 1, a, alpha, beta))
                if value <= alpha: 
                    break
                beta = min(beta,value)
                if time.time() - self.start > self.max_time:
                    break
        self.states[key] = [depth,value]
        return value
    

    def reorder(self): 

        return None

    def hash_funct(self, state):
        sc = ''
        fp = str(state.fish_positions).translate(str.maketrans('', '', string.punctuation+" "))
        hp = (str(state.hook_positions[0]) + str(state.hook_positions[1])).translate(str.maketrans('', '', string.punctuation+" "))
        #sc = (str(state.player_scores[0]) + str(state.player_scores[1])).translate(str.maketrans('', '', string.punctuation))
        return (fp + hp + sc)

#HEURISTICS
    def compute_heuristic(self, node): 
        return self.heur_2(node.state)

    def man_distance(self, fish, hook):
        x = min(abs(fish[0] - hook[0]), 20-abs(fish[0]-hook[0]))
        y = abs(hook[1] - fish[1])

        return x + y

    def heur_1(self, node):

        player_scores = node.player_scores
        fish = node.fish_positions
        fish_scores = node.fish_scores
        n_fish = len(fish)

        hook_p1, hook_p2 = node.get_hook_positions().values()
        scores_diff = player_scores[0] - player_scores[1]

        #If no fish, return score difference
        if n_fish == 0:
            return scores_diff

        #Evaluate distance for every fish
        val = 0
        for fish, pos in fish.items():
            proximity = self.man_distance(pos, hook_p1)
            #Check distance
            if proximity <= 0: 
                proximity = 0.1
            
            val += fish_scores[fish]  / (proximity)

        #Linear combination of val and scores difference
        return  val


    def heur_2(self, node):
        player_scores = node.player_scores
        fish = node.fish_positions
        fish_scores = node.fish_scores
        n_fish = len(fish)

        hook_p1, hook_p2 = node.get_hook_positions().values()
        scores_diff = player_scores[0] - player_scores[1]

        #If no fish, return score difference
        if n_fish == 0:
            return scores_diff

        #Evaluate distance for every fish
        val = 0
        for fish, pos in fish.items():
            proximity = self.man_distance(pos, hook_p1)
            #Check distance

            #if proximity == 0 and n_fish == 1: return math.inf

            #print(f"Proximity: {proximity}, Score: {fish_scores[fish]}")
            #Else, most valuable fish, scaled by the distance

            #val += fish_scores[fish] / (proximity + 1)

            val = max(val, fish_scores[fish]*math.exp(-proximity))

        #Linear combination of val and scores difference
        '''
        print("Scores diff: ", scores_diff)
        print("Value: ", val)
        '''
        return val + (scores_diff)*2

    def example_heur(self, state, only_scores=False):
        scores = state.get_player_scores()
        hook_positions = state.get_hook_positions()
        fish_positions = state.get_fish_positions()
        caught_fish = state.get_caught()
        score_based_value = self.get_score_based_value(caught_fish, scores)
        n_fish = len(fish_positions)
        n_caught = int(caught_fish[0] != None) + int(caught_fish[1] != None)
        if n_fish == 0 or n_fish == n_caught:
            if score_based_value > 0:
                return math.inf
            if score_based_value < 0:
                  return -math.inf
            return 0.0
        if only_scores:
            return score_based_value
        value_max_player = self.get_proximity_value(hook_positions, fish_positions, caught_fish, self.max_player)
        value_min_player = self.get_proximity_value(hook_positions, fish_positions, caught_fish, 1 - self.max_player)
        proximity_value = value_max_player - value_min_player
        return score_based_value + proximity_value

    def get_score_based_value(self, caught_fish, scores):
        extra_score_max = self.fish_scores[caught_fish[self.max_player]] if caught_fish[self.max_player] is not None else 0
        extra_score_min = self.fish_scores[caught_fish[(1 - self.max_player)]] if caught_fish[(1 - self.max_player)] is not None else 0
        value = 100 * (scores[self.max_player] - scores[(1 - self.max_player)] + extra_score_max - extra_score_min)
        return value

    def get_proximity_value(self, hook_positions, fish_positions, caught_fish, player):
        value = 0.0
        for fish, fish_position in fish_positions.items():
            if fish in caught_fish:
                continue
            else:
                distance_x = min(abs(fish_position[0] - hook_positions[player][0]), self.space_subdivisions - abs(fish_position[0] - hook_positions[player][0]))
                distance_y = abs(fish_position[1] - hook_positions[player][1])
                distance = distance_x + distance_y
            value += float(self.fish_scores[int(fish)]) * math.exp(-2 * distance)
        return value

   