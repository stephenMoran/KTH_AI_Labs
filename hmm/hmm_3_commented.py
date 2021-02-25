import sys

def div_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def build_matrix(line_in):
    #print('Line in: ', line_in)
    row = int(line_in[0])
    col = int(line_in[1])
    #to_rtn = [[int(el)] for el in line_in[2:]]
    
    to_rtn = list(div_chunks(line_in[2:], col))
    return to_rtn

def get_lines():
    lines = []
    for line in sys.stdin:
        lines.append(line)
    return lines

def read_input():
    lines = get_lines()
    A = build_matrix([float(n) for n in lines[0].split()])
    B = build_matrix([float(n) for n in lines[1].split()])
    init = build_matrix([float(n) for n in lines[2].split()])
    seq = [int(n) for n in lines[3].split()[1:]]

    return A, B, init, seq

#Forward algorithm
def forward_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0] #Get pi as list
    N = len(init) #N number of states
    scale_vec = [] #Init scale vector
    o_0 = seq[0] #First observation
    a0 = [] #Create list for alpha initialization
    to_rtn = [] #Create alphas list

    #Initialize alpha0
    for i in range(N):
        a0.append(init[i]*B[i][o_0])

    to_rtn.append(a0) #Add alpha0 to the alpha list

    #Get scaling factor of alpha_o
    sum_a0 = sum(a0)
    #Add it to the scale_vec
    scale_vec.append(sum_a0)
    #Append to the alphas the scaled alpha_o 
    to_rtn.append([el/sum_a0 for el in a0])

    #Evaluate a1 ... aT-1
    #Iterate over observations, excluding the first one
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1] #Ger previous alpha
        #Initialize alpha_o
        a = []
        #Matrix multiplication
        for i in range(N):
            sum_v = 0
            for j in range(N):
                sum_v += prev_a[j] * A[j][i] #Sum previous alpha for state j and transaction prob from j to i
            a.append(sum_v*B[i][o]) #Multiply the sum by the probability of observation o in state i, and add it to the alpha_o list

        #Get scaling vector c
        c = sum(a)
        #Append it to the scaling vector list
        scale_vec.append(c)
        #Append to the alphas the scaled alpha
        to_rtn.append([el/c for el in a])
        t += 1

    return to_rtn, scale_vec


def backward_alg(A,B, init, seq, scale_vec):
    N = len(init[0]) #N number of states
    to_rtn = []

    #Get time t
    t = len(seq)

    #Init bT
    #1 scaled by the last scale_vector
    to_rtn.append([1/scale_vec[-1] for i in range(N)])

    #Decrease t to start with T-1
    t -= 1

    #Get last observation    
    o_prev = seq[-1]

    #Iterate from T-2 to 0
    for t in range(len(seq)-2, -1, -1):
        prev_b = to_rtn[-1] #Get last b
        #init row b
        b= [] #beta_o
        for i in range(N):
            sum_b = 0 #Init beta at time t for state i
            for j in range(N):
                #Perform beta calculation
                sum_b = sum_b + A[i][j]*B[j][seq[t+1]]*prev_b[j]

            #add values to beta_o, for every state i
            b.append(sum_b)

        #Scale before appending
        #get the scaling value from the vector
        c = scale_vec[t]
        #Append to the betas the scaled beta_o
        to_rtn.append([el/c for el in b])

    #Return the reversed list    
    return to_rtn[::-1]

def compute_gammas(A, B, seq, alphas, betas):
    N = len(alphas[0]) #N number of statez
    #Initialize gammas and di_gammas lkst
    gammas = []
    di_gammas = []

    #Iterate over time, until T-1
    for t in range(len(seq)-1):
        o_1 = seq[t+1] #Observation at next time t+1
        g = [] #init gamma_t
        di_g = [] #init di_gamma_t
        for i in range(N):
            sum_di_g = [] #Init di_g[i] to empty list
            for j in range(N):
                #Add values for every state j
                sum_di_g.append(alphas[t][i]*A[i][j]*B[j][o_1]*betas[t+1][j])

            #Add the line created before to the matrix di_g[i]
            di_g.append(sum_di_g)
            #Perform gamma at time t for state i, summing the values in di_gamma[i]
            g.append(sum(sum_di_g))

        #Append the matrix di_gammas[i][j] to the 3-D matrix for each time step t
        di_gammas.append(di_g)
        #Append the list of gammas at each time step t
        gammas.append(g)
        
    #Case for T for gammas
    gammas.append([alphas[-1][i] for i in range(N)])

    return di_gammas, gammas


def re_estimate_param(A, B, init, di_gammas, gammas, seq):
    N = len(init[0]) #N number of states
    M = len(B[0]) #M number of observations
    T = len(seq) #T time steps
    #Initialite the new model parameters
    init_rtn = []
    A_rtn = []
    B_rtn = []

    #Re estimate init
    for i in range(N):
        init_rtn.append(gammas[0][i])

    #Re estimate A
    #Iterate over states i
    for i in range(N):
        den = 0
        ai = [] #Init list for A[i]
        for t in range(T-1):
            #Calculate the denominator through gammas
            den = den + gammas[t][i]
        for j in range(N):
            num = 0
            for t in range(T-1):
                #Calculate the numerator through di_gammas
                num =  num + di_gammas[t][i][j]
            #Append new values to list for A[i]
            ai.append(num/den)

        #Add to matrix A the row ai
        A_rtn.append(ai)

    #Re estimate B
    #Iterate over states i
    for i in range(N):
        den = 0
        bi = [] #Init list for B[i]
        for t in range(T):
            #Calculate the denominator through gammas
            den = den + gammas[t][i]
        for j in range(M):
            num = 0
            for t in range(T):
                #Check for observed observation at time t
                if seq[t] == j:
                    #Calculate numerator through gammas
                    num += gammas[t][i]
            #Append new values to list for B[i]
            bi.append(num/den)

        #Add to matrix B the row ai
        B_rtn.append(bi)
    
    #Return pi as a matrix of length 1, to respect the same notation used before
    init_rtn = [init_rtn]
    return A_rtn, B_rtn, init_rtn

#Read the input, init delta
#Step 1: init A,B, pi
A, B, init, seq = read_input()

#Set convergence iterations
max_i = 100
for i in range(max_i):
    #Step 2: Compute alphas, betas, digammas and gammas
    alphas, scale_vec = forward_alg(A, B, init, seq)
    betas = backward_alg(A, B, init, seq, scale_vec)

    di_gammas, gammas = compute_gammas(A, B, seq, alphas, betas)

    #Step 3: Re-Estimate A, B. Pi
    A, B, init = re_estimate_param(A,B,init, di_gammas, gammas, seq)

    #Repeat until convergence (used fixed number of iterations)



print(len(A), len(A[0]), end=' ')
for l in A:
    print(*l, end=' ')

print('')

print(len(B), len(B[0]), end=' ')
for l in B:
    print(*l, end=' ')

