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
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
    '''
    #print('lines: ', lines[0])
    lines = get_lines()
    A = build_matrix([float(n) for n in lines[0].split()])
    B = build_matrix([float(n) for n in lines[1].split()])
    init = build_matrix([float(n) for n in lines[2].split()])
    seq = [int(n) for n in lines[3].split()[1:]]

    return A, B, init, seq


#Viterbi algorithm
def viterbi_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0] #Get pi as list
    N = len(init) #N number of states
    o_0 = seq[0] #First observation
    a0 = [] #Alpha_0
    a0_ind = [] #Alpha_0 indeces
    to_rtn = [] #Alphas
    to_rtn_ind = [] #Alphas indexes

    #Init alpha(0)
    for i in range(N):
        a0.append(init[i]*B[i][o_0])
        a0_ind.append(-1)#time step = 0, initialise indeces to a non-valid value (-1)

    #Add alpha_0 to the alphas
    to_rtn.append(a0)
    to_rtn_ind.append(a0_ind)

    #Evaluate a1 ... aT-1
    #Iterate over observations, excluding the first one
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1] #Get previous alpha
        #Matrix multiplication
        a = [] #alpha_o
        a_ind = [] #alpha_o indeces
        for i in range(N):
            #Init max variables
            tmp_max = 0
            tmp_m_ind = -1
            for j in range(N):
                new_v = prev_a[j] * A[j][i] #Get the new value, previous alpha multiplied by transaction from i to new state j
                #Check for max value
                if new_v > tmp_max:
                    #Update max and index
                    tmp_max = new_v
                    tmp_m_ind = j

            a.append(tmp_max*B[i][o]) #Append to alpha_o the max value multiplied by the observation probability, state i
            a_ind.append(tmp_m_ind) #Append max index to alpha_o index list
        
        #Add alpha_o and alpha_index to the lists
        to_rtn.append(a)
        to_rtn_ind.append(a_ind)
        t += 1

    return to_rtn, to_rtn_ind

# given an iterable of pairs return the key corresponding to the greatest value
def argmax(pairs):
    return max(pairs, key=lambda x: x[1])[0]

# given an iterable of values return the index of the greatest value
def argmax_index(values):
    return argmax(enumerate(values))

def backtrack(pred, ind):
    to_rtn = []
    #Get index of the max in the last alpha
    prec = argmax_index(pred[-1])
    #Add the index to the return list
    to_rtn.append(prec)
    #Iterate over the reversed index list
    for i in ind[::-1]:
        prec = i[prec] #Get index of the previous max
        to_rtn.append(prec) #Append the index to the state sequence list
    
    #Remove last el and return reversed list
    return to_rtn[:-1][::-1]


#Read the input
A, B, init, seq = read_input()

#Call the viterbi algorithm on the parameters A, B, pi and observations sequence
vit_lik, vit_ind = viterbi_alg(A, B, init, seq)

#Backtrack the viterby likelihood and the state indeces to get the state sequence
state_seq = backtrack(vit_lik, vit_ind)

#Print the state sequence
print(*state_seq)
