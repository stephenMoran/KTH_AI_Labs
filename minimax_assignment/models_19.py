
import random
import math, time
import numpy as np
import random, string
from fishing_game_core.shared import ACTION_TO_STR

class MinimaxModel(object): 
    def __init__(self, initial_data): 
        #self.get_fish_scores_and_types(initial_data)
        self.max_time =  0.060
        self.states = {}
        #return None

    def get_fish_scores_and_types(self, initial_data):
        '''
        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }
        '''
        '''
        self.fish_scores = {}
        for f in initial_data:
            #Check if fish
            
            if f[:4] == 'fish':
                fish_n = f[4:]
                el = {int(fish_n):initial_data[f]['score']}
                self.fish_scores[fish_n] = el
        '''
        '''
        print(self.fishes)
        '''

    def next_move(self, root_node, max_depth=15): 
        self.start = time.time()
        alpha = -math.inf
        beta = math.inf
        self.max_depth = max_depth
        self.max_player = root_node.state.player
        depth = 0
        actions = root_node.compute_and_get_children()
        #best_value = 0
        best_move = 0
        best_moves = {}
        while (time.time() < self.start + self.max_time):
            best_value = -math.inf
            for a in actions: 
                key = self.hash_funct(a.state)
                if key in self.states:
                    value = self.states[key][1]
                else:
                    value = self.min_value(depth, a, alpha, beta)

                if value > best_value: 
                    best_value = value
                    best_move = a.move
                    alpha = value
            
            best_moves[depth] = (best_value, best_move)
            depth += 1

            '''
            optimal_index = max(best_moves, key=best_moves.get)
            optimal_action = best_moves[optimal_index][1]
            '''
            
            optimal_action = best_move
        return ACTION_TO_STR[optimal_action]

    def max_value(self, depth, node, alpha=0, beta=0): 
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
                if time.time() - self.start > self.max_time:
                    break

        self.states[key] = [depth,value]
        return value
        
    def min_value(self, depth, node, alpha=0, beta=0):
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
                #print("Value: ", value)
                value = min(value, self.max_value(depth - 1, a, alpha, beta))          
                if value <= alpha: 
                    break
                beta = min(beta,value)
                if time.time() - self.start > self.max_time:
                    break
        self.states[key] = [depth,value]
        return value

    def hash_funct(self, state):
        sc = ''
        pt = ''
        #Fish position in string representation
        fp = str(state.fish_positions)#.translate(str.maketrans('', '', string.punctuation+" "))
        #Fish scores in string representation
        fs = str(state.fish_scores)
        #Position of the two hooks
        hp = (str(state.hook_positions[0]) + str(state.hook_positions[1]))#.translate(str.maketrans('', '', string.punctuation+" "))
        #Scores of the two players
        sc = (str(state.player_scores[0]) + str(state.player_scores[1])).translate(str.maketrans('', '', string.punctuation))

        #pt = '_' + str(state.player)
        return (fp + hp + fs + sc + pt)


#HEURISTICS
    def compute_heuristic(self, node): 
        #Container function
        return self.heur_1(node.state)

    def man_distance(self, fish, hook):
        #Function to compute a slightly modified manhattan distance
        x = min(abs(fish[0] - hook[0]), 20-abs(fish[0]-hook[0]))
        y = abs(hook[1] - fish[1]) + (20-(fish[1])) #Add the y to go back from the fish to the boat
        return x + y

    def heur_1(self, node):
        #Get state info
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
            #Get distance from our hook to the fish
            proximity = self.man_distance(pos, hook_p1)

            #If I'm closer to the fish than hook_p2 and score_diff is positive, go for it
            #proximity_p2 = self.man_distance(pos, hook_p2)

            #If hook is on the fish and last fish remaning, go for it
            if proximity == (20-pos[1]) and n_fish == 1: return math.inf

            '''
            #val = max(val, 1/(abs(proximity-proximity_p2)+1))

            #val = max(val, 1/proximity)

            #print(f"Proximity: {proximity}, Score: {fish_scores[fish]}")
            #Else, most valuable fish, scaled by the distance

            #val += fish_scores[fish] / (proximity + 1)
            '''

            #
            val += fish_scores[fish]/math.exp(proximity)
            #val = max(val, fish_scores[fish]/math.exp(proximity))

            #val += fish_scores[fish] - proximity#/math.exp(proximity)
            #val += math.exp(proximity)
            

        #Linear combination of val and scores difference
        '''
        print("Scores diff: ", scores_diff)
        print("Value: ", val)
        '''
        return val + (scores_diff)

def sign(x):
    return math.copysign(1, x)