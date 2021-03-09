
import random
import math, time
import numpy as np
import random, string
from fishing_game_core.shared import ACTION_TO_STR

class MinimaxModel(object): 
    def __init__(self, initial_data): 
        self.get_fish_scores_and_types(initial_data)
        self.max_time =  0.040
        self.states = {}
        return None

    def get_fish_scores_and_types(self, data):
        data.pop('game_over', None)
        self.fish_scores = {int(key.split('fish')[1]):value['score'] for key, value in data.items()}
        scores_to_type = {s:t for t, s in enumerate(set(self.fish_scores.values()))}
        self.fish_types = {f:scores_to_type[s] for f, s in self.fish_scores.items()}

    def next_move(self, root_node, max_depth=8): 
        self.start = time.time()
        alpha = -math.inf
        beta = math.inf
        self.max_depth = max_depth
        #self.max_player = root_node.state.player
        depth = 0
        actions = root_node.compute_and_get_children()
        #best_move = 0
        #best_moves = {}
        time_left = True
        #(depth <= max_depth) and (time.time() < self.start + self.max_time)
        while time_left:
            best_value = -math.inf
            try:
                
                #values = []
                for a in actions: 
                    value = self.min_value(depth, a, alpha, beta)
                    #values.append(value)
                    if value > best_value: 
                        best_value = value
                        best_move = a.move
                """
                best_moves[depth] = (best_value, best_move)
                depth += 1
                optimal_index = max(best_moves, key=best_moves.get)
                optimal_action = best_moves[optimal_index][1]
                """
                depth = depth + 1
                optimal_action = best_move
            except TimeoutError: 
                time_left = False
        return ACTION_TO_STR[optimal_action]

    def max_value(self, depth, node, alpha=0, beta=0): 
        if time.time() - self.start > self.max_time:
            raise TimeoutError
        else: 
            key = self.hash_funct(node.state)
            if key in self.states and self.states[key][0] >= depth:
                return self.states[key][1]
            actions = node.compute_and_get_children()
            actions.sort(key=self.compute_heuristic, reverse = True)
            value = -math.inf
            if depth == 0 or (len(actions) == 0): 
                return self.compute_heuristic(node)
            else: 
                for a in actions:
                    value = max(value, self.min_value(depth - 1, a, alpha, beta))
                    if value >= beta: 
                        break
                    alpha = max(alpha,value)
            self.states[key] = [depth,value]
        return value
        
    def min_value(self, depth, node, alpha=0, beta=0):
        if time.time() - self.start > self.max_time:
            raise TimeoutError
        else:
            key = self.hash_funct(node.state)
            if key in self.states and self.states[key][0] >= depth:
                return self.states[key][1]
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
            self.states[key] = [depth,value]
        return value

    def hash_funct(self, state):
        sc = ''
        fp = str(state.fish_positions).translate(str.maketrans('', '', string.punctuation+" "))
        hp = (str(state.hook_positions[0]) + str(state.hook_positions[1])).translate(str.maketrans('', '', string.punctuation+" "))
        #sc = (str(state.player_scores[0]) + str(state.player_scores[1])).translate(str.maketrans('', '', string.punctuation))
        return (fp + hp + sc)

#HEURISTICS
    def compute_heuristic(self, node): 
        return self.heur_1(node.state)

    def man_distance(self, fish, hook):
        x = min(abs(fish[0] - hook[0]), 20-abs(fish[0]-hook[0]))
        y = abs(hook[1] - fish[1]) + (20-(fish[1])) #Add the y to go back from the fish to the boat
        #add in influence of other ship i.e. go for fish that you can reach before them 
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

            #If I'm closer to the fish than hook_p2 and score_diff is positive, go for it
            #proximity_p2 = self.man_distance(pos, hook_p2)

            #if proximity > proximity_p2:
                #Get the max
            #val = max(val, fish_scores[fish] * sign(proximity-proximity_p2))

            
            if proximity == (20-pos[1]) and n_fish == 1: return math.inf

            #val = max(val, 1/(abs(proximity-proximity_p2)+1))

            #val = max(val, 1/proximity)

            #print(f"Proximity: {proximity}, Score: {fish_scores[fish]}")
            #Else, most valuable fish, scaled by the distance

            #val += fish_scores[fish] / (proximity + 1)

            val = max(val, fish_scores[fish]/math.exp(proximity))
            #val += fish_scores[fish] - proximity#*math.exp(-proximity)
            #val += math.exp(-proximity)
            

        #Linear combination of val and scores difference
        return val + (scores_diff)


    def heur_2(self, state):
        r = state.player_scores[0]
        op_score = state.player_scores[1]
        su = 0
        for i in state.fish_positions:
            distance = self.calculate_distance(state.fish_positions[i], state.hook_positions[0])
            if distance == 0 and len(state.fish_positions)==1:
                return float('inf')
            su = max(su, state.fish_scores[i]*math.exp(-distance))
        return su + (r - op_score)*2

    def calculate_distance(self, fish_positions, hook_positions):
        y_distance = abs(fish_positions[1] - hook_positions[1])
        x_distance = min(abs(fish_positions[0] - hook_positions[0]), 20 - abs(fish_positions[0] - hook_positions[0]))
        distance = x_distance + y_distance
        return distance