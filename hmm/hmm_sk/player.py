#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
from baum_welch import bm_alg, guess_fw_alg
import numpy as np
import random

class species_model:
    def __init__(self, N_states, N_obs):
        #init mat A,B, pi
        self.init_A = self.init_matrix(N_states, N_states)
        self.init_B = self.init_matrix(N_states, N_obs)
        self.init_pi = self.init_matrix(1, N_states)[0]

        self.A, self.B, self.pi = self.init_A, self.init_B, self.init_pi

        self.fish_list = []
        self.obs_movements = []

        self.guess_reaady = False

    def init_matrix(self, n_row, n_col):
        random.seed(42)
        to_rtn = []
        #Create a row with noise (list with n_col elements), then shuffle it n_row - 1 times
        #stoc_row = np.random.dirichlet(np.ones(n_col),size=1).tolist()[0]
        #noise = np.random.uniform(-0.05, 0.05, n_col).tolist()
        for i in range(n_row):
            noise_row = [random.uniform(-0.050, 0.050) for _ in range(n_col-1)]

        sum_noise = 0
        stoc_row = []
        for i in range(n_col-1):
            stoc_row.append((1/n_col) + noise_row[i])
            sum_noise += noise_row[i]
        stoc_row.append((1/n_col) - sum_noise)

        for i in range(n_row):
            #Append to to_rtn a random shuffle of the row created previously
            to_rtn.append(random.sample(stoc_row, n_col))

        return to_rtn


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
        #Try with 7 states
        #The observation is given by the number of Emissions, 8
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

        #For each fish, append the movement (observation) to its mov_lists (movements)
        for i in range(len(self.fish)):
            self.movements = self.fish[i].movements.append(observations[i])

        #If we still have time, return None
        time_lim = 63
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
            #Initialise probability variables
            max_lik = 0
            max_index = -1
            for i in range(N_SPECIES):
                cur_hmm = self.hmm_models[i]
                if cur_hmm.guess_reaady: #If model ready for guessing
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

        #Add fish to its model, update model
        self.hmm_models[true_type].fish_list.append(fish_id)
        mov_seq = self.fish[fish_id].movements

        self.hmm_models[true_type].obs_movements.extend(mov_seq)
        mod_seq = self.hmm_models[true_type].obs_movements

        A,B,pi = self.hmm_models[true_type].init_A, self.hmm_models[true_type].init_B, self.hmm_models[true_type].init_pi
        #A,B,pi = self.hmm_models[true_type].A, self.hmm_models[true_type].B, self.hmm_models[true_type].pi

        self.hmm_models[true_type].A, self.hmm_models[true_type].B, self.hmm_models[true_type].pi = bm_alg(A,B, pi, mod_seq, len(mod_seq))
        self.hmm_models[true_type].guess_reaady = True
        



