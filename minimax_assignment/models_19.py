
import random
import math, time
import numpy as np
import random, string
from fishing_game_core.shared import ACTION_TO_STR

class MinimaxModel(object): 
    def __init__(self, initial_data): 
        #self.get_fish_scores_and_types(initial_data)
        self.max_time =  0.058
        self.states = {}
        #return None

    def next_move(self, root_node, max_depth=math.inf): 
        #start the timer
        self.start = time.time()
        #initialise beta and alpha
        alpha = -math.inf
        beta = math.inf
        self.max_depth = max_depth
        self.max_player = root_node.state.player
        depth = 0
        #possible actions at root node
        actions = root_node.compute_and_get_children()
        best_move = 0
        best_moves = {}
        #continue iterative minmax until time is out
        while (time.time() < self.start + self.max_time):
            best_value = -math.inf
            alpha = -math.inf
            beta = math.inf
            for a in actions: 
                #save current state
                key = self.hash_funct(a.state)
                #check if state has been seen before
                if key in self.states:
                    value = self.states[key][1]
                else:
                    #call min value as max player goes first
                    value = self.min_value(depth, a, alpha, beta)

                #check if new vlaue is better than the last
                if value > best_value: 
                    best_value = value
                    best_move = a.move
                    alpha = value

            #save the best move at each depth
            best_moves[depth] = (best_value, best_move)
            depth += 1

            '''
            optimal_index = max(best_moves, key=best_moves.get)
            optimal_action = best_moves[optimal_index][1]
            '''
            #return the best action
            optimal_action = best_move
        return ACTION_TO_STR[optimal_action]


    def max_value(self, depth, node, alpha=-math.inf, beta=math.inf): 
        #get hash key
        key = self.hash_funct(node.state)
        #check if its been seen before
        if key in self.states:
            return self.states[key][1]
        #get actions for this state
        actions = node.compute_and_get_children()
        #try the moves which are likely the best moves first
        actions.sort(key=self.compute_heuristic, reverse = True)
        value = -math.inf
        #if terminal state reached - compute heuristic
        if depth == 0 or (len(actions) == 0): 
            return self.compute_heuristic(node)
        else: 
            for a in actions:
                value = max(value, self.min_value(depth - 1, a, alpha, beta))    
                #if the new value is greater than beta we can break as we know that min wont choose this so we can break            
                if value >= beta: 
                    break
                #if this value is greater than the current alpha update
                alpha = max(alpha,value)
                if time.time() - self.start > self.max_time:
                    break
        #save current depth and value
        self.states[key] = [depth,value]
        return value
        
    def min_value(self, depth, node, alpha=0, beta=0):
        #get hash key
        key = self.hash_funct(node.state)
        #check if its been seen before
        if key in self.states:
          return self.states[key][1]
        #get actions for this state
        actions = node.compute_and_get_children()
        value = math.inf
        #try the moves which are likely the best moves first
        actions.sort(key=self.compute_heuristic, reverse = False)
        #if terminal state reached - compute heuristic
        if depth == 0 or (len(actions) == 0): 
            return self.compute_heuristic(node)
        else: 
            for a in actions: 
                value = min(value, self.max_value(depth - 1, a, alpha, beta))     
                #if the new value is less than alpha we can break as we know that max wont choose this so we can break     
                if value <= alpha: 
                    break
                #update beta if new value is lower than current beta
                beta = min(beta,value)
                if time.time() - self.start > self.max_time:
                    break
        #save current depth and value
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
        val = -math.inf
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
            #val += fish_scores[fish]/math.exp(proximity)
            val = max(val, fish_scores[fish]/math.exp(proximity))

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