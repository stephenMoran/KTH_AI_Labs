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


'''
#Forward algorithm
def forward_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0]
    N = len(init)
    o_0 = seq[0]
    a0 = []
    a0_ind
    to_rtn = []
    for i in range(N):
        a0.append(init[i]*B[i][o_0])
        a0_ind.append(-1)

    to_rtn.append(a0)

    #Evaluate a1 ... aT-1
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1]
        #Matrix multiplication
        a = []
        for i in range(N):
            sum = 0
            for j in range(N):
                sum += prev_a[j] * A[j][i]
            a.append(sum*B[i][o])
        
        to_rtn.append(a)
        t += 1

    return to_rtn
'''

#Viterbi algorithm
def viterbi_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0]
    N = len(init)
    o_0 = seq[0]
    a0 = []
    a0_ind = []
    a_ind = []
    to_rtn = []
    to_rtn_ind = []
    for i in range(N):
        a0.append(init[i]*B[i][o_0])
        a0_ind.append(-1)

    to_rtn.append(a0)
    to_rtn_ind.append(a0_ind)

    #Get most likely state


    #Evaluate a1 ... aT-1
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1]
        #Matrix multiplication
        a = []
        a_ind = []
        for i in range(N):
            tmp_max = 0
            tmp_m_ind = -1
            for j in range(N):
                new_v = prev_a[j] * A[j][i]
                if new_v > tmp_max:
                    #Update max and index
                    tmp_max = new_v
                    tmp_m_ind = j

            a.append(tmp_max*B[i][o])
            a_ind.append(tmp_m_ind)
        
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
    prec = argmax_index(pred[-1])
    to_rtn.append(prec)
    for i in ind[::-1]:
        prec = i[prec]
        to_rtn.append(prec)
    
    #Remove last el and return reversed list
    return to_rtn[:-1][::-1]


#Read the input
A, B, init, seq = read_input()



'''
print('A: ', A)
print('B: ', B)
print('Init: ', init)
print('Seq: ', seq)
'''

vit_lik, vit_ind = viterbi_alg(A, B, init, seq)

'''
print("Probabilities: ", vit_lik)
print("Indeces: ", vit_ind)
'''

state_seq = backtrack(vit_lik, vit_ind)

print(*state_seq)


#Sum probsabilities for the last alpha
#print('sum: ', sum(for_alg[-1]))

#with open('output.txt')
#print(sum(for_alg[-1]))

#Forward algorithm
