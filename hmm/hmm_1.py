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


#Forward algorithm
def forward_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0] #Get pi as list
    N = len(init) #N number of states
    o_0 = seq[0] #First observation
    a0 = [] #Create list for alpha initialization
    to_rtn = [] #Create alphas list

    #Initialize alpha0
    for i in range(N):
        a0.append(init[i]*B[i][o_0])

    to_rtn.append(a0) #Add alpha0 to the alpha list

    #Evaluate a1 ... aT-1
    #Iterate over observations, excluding the first one
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1] #Ger previous alpha
        #Initialize alpha_o
        a = []
        #Matrix multiplication
        for i in range(N):
            sum = 0
            for j in range(N):
                sum += prev_a[j] * A[j][i] #Sum previous alpha for state j and transaction prob from j to i
            a.append(sum*B[i][o]) #Multiply the sum by the probability of observation o in state i, and add it to the alpha_o list
        
        #Add the alpha_o to the alphas
        to_rtn.append(a)
        t += 1

    return to_rtn



#Read the input
A, B, init, seq = read_input()

#Call the forward algorithm on params A, B, pi and seq
for_alg = forward_alg(A, B, init, seq)

#Print sum of the probabilities in the last alpha
print(sum(for_alg[-1]))

#Forward algorithm
