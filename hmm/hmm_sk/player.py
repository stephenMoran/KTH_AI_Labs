#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
from baum_welch import bm_alg, guess_fw_alg
import random

class species_model:
    def __init__(self, N_states, N_obs):
        #Init pi, A, B
        #Uniform

        '''
        self.pi = [1/N_states for _ in range(N_states)]
        self.A = [[1/N_states for _ in range(N_states)] for _ in range(N_states)]
        self.B = [[1/N_states for _ in range(N_obs)] for _ in range(N_states)]
        '''

        self.init_A = self.init_semiuniform_matrix(N_states, N_states)
        self.init_B = self.init_semiuniform_matrix(N_states, N_obs)
        self.init_pi = self.init_semiuniform_matrix(1, N_states)[0]

        self.A, self.B, self.pi = self.init_A, self.init_B, self.init_pi

        #print(self.B)

        #print(self.pi[0])

        self.fish_list = []
        self.obs_movements = []

        self.guess_reaady = False

    def init_matrix(self, n_row, n_col):
        to_rtn = []
        #Create a row with noise (list with n_col elements), then shuffle it n_row - 1 times
        noise = n

    def init_semiuniform_matrix(self, row, col):
        random.seed(30)
        M = []
        for i in range(row):
            # make a uniform row
            r = [1 / col for i in range(col)]
            # generate some noise
            noise = [random.uniform(-0.05, 0.05) for k in range(col - 1)]
            # add/remove noise from the first n-1 elements
            for j in range(col - 1):
                r[j] = r[j] + noise[j]
            # assign last element such that the sum of the row is 1
            r[-1] = 1 - sum(r[:-1])
            M.append(r)
        return M


class my_fish:
    def __init__(self, fish_id):
        self.fish_id = fish_id
        self.movements = []



class PlayerControllerHMM(PlayerControllerHMMAbstract):
    def init_parameters(self):
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """

        #7 different models, 1 for each species
        #2 different states
        #Try with 7 states
        self.hmm_models = [species_model(7, N_EMISSIONS) for i in range(N_SPECIES)]

        #List of fish to guess
        self.fish = [my_fish(n) for n in range(N_FISH)]
        self.next_guess_f = 0
        

    def guess(self, step, observations):
        """
        This method gets called on every iteration, providing observations.
        Here the player should process and store this information,
        and optionally make a guess by returning a tuple containing the fish index and the guess.
        :param step: iteration number
        :param observations: a list of N_FISH observations, encoded as integers
        :return: None or a tuple (fish_id, fish_type)
        """

        # This code would make a random guess on each step:
        # return (step % N_FISH, random.randint(0, N_SPECIES - 1))

        #For each fish, append the movement (observation) to its mov_lists (movements)
        for i in range(len(self.fish)):
            self.movements = self.fish[i].movements.append(observations[i])

        #If we still have time, return None
        time_lim = 62
        if step < time_lim:
            return None

        #When step = time_lim make a random guess in order to update the params
        if step == time_lim:
            return (self.fish[self.next_guess_f].fish_id, random.randint(0, N_SPECIES-1))
            self.next_guess_f += 1


        #Run the forward
        if step > time_lim:
            guess_id = self.fish[self.next_guess_f].fish_id
            self.next_guess_f += 1
            #If model ready for guessing
            max_lik = 0
            max_index = -1
            for i in range(N_SPECIES):
                cur_hmm = self.hmm_models[i]
                if cur_hmm.guess_reaady:
                    #Run FW and compare probs
                    new_lik = guess_fw_alg(cur_hmm.A, cur_hmm.B, cur_hmm.pi, self.fish[guess_id].movements)
                    if new_lik > max_lik:
                        #Update max
                        max_lik = new_lik
                        max_index = i
            return (guess_id, max_index)

    def reveal(self, correct, fish_id, true_type):
        """
        This methods gets called whenever a guess was made.
        It informs the player about the guess result
        and reveals the correct type of that fish.
        :param correct: tells if the guess was correct
        :param fish_id: fish's index
        :param true_type: the correct type of the fish
        :return:
        """
        #Add fish to its true model
        self.hmm_models[true_type].fish_list.append(fish_id)

        #Add fish to its model, update model
        self.hmm_models[true_type].fish_list.append(fish_id)
        mov_seq = self.fish[fish_id].movements

        self.hmm_models[true_type].obs_movements.extend(mov_seq)
        mod_seq = self.hmm_models[true_type].obs_movements

        A,B,pi = self.hmm_models[true_type].init_A, self.hmm_models[true_type].init_B, self.hmm_models[true_type].init_pi

        self.hmm_models[true_type].A, self.hmm_models[true_type].B, self.hmm_models[true_type].pi = bm_alg(A,B, pi, mod_seq, len(mod_seq))
        self.hmm_models[true_type].guess_reaady = True
        



