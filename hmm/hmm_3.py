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
    init = init[0]
    scale_vec = []
    N = len(init)
    o_0 = seq[0]
    a0 = []
    to_rtn = []
    for i in range(N):
        a0.append(init[i]*B[i][o_0])

    sum_a0 = sum(a0)
    scale_vec.append(sum_a0)
    to_rtn.append([el/sum_a0 for el in a0])

    #Evaluate a1 ... aT-1
    t=1
    for o in seq[1:]:
        prev_a = to_rtn[t-1]
        #Matrix multiplication
        a = []
        for i in range(N):
            sum_a = 0
            for j in range(N):
                sum_a += prev_a[j] * A[j][i]
            a.append(sum_a*B[i][o])

        #Scale
        c = sum(a)
        scale_vec.append(c)
        to_rtn.append([el/c for el in a])
        t += 1

    return to_rtn, scale_vec


def backward_alg(A,B, init, seq, scale_vec):
    N = len(init[0])
    to_rtn = []

    t = len(seq)

    #Init bT
    to_rtn.append([1/scale_vec[i] for i in range(N)])

    t -= 1

    
    for o in seq[:-1][::-1]:
        prev_b = to_rtn[-1] #Get last to_rtn element
        #Mult
        b=[]
        for i in range(N):
            sum_b = 0
            for j in range(N):
                sum_b += prev_b[j]*B[j][o]*A[i][j]

            
            b.append(sum_b)


        #Scale before appending
        c = scale_vec[t]
        to_rtn.append([el/c for el in b])
        '''
        c = sum(b)
        to_rtn.append([el/c for el in b])
        '''

        t-=1

    return to_rtn[::-1]

def compute_gammas(A, B, seq, alphas, betas):
    N = len(alphas[0])
    gammas = []
    di_gammas = []

    for t in range(len(seq)-1):
        o_1 = seq[t+1] #Observation at next time t+1
        g = []
        di_g = []
        di_g_t = []
        for i in range(N):
            sum_di_g = []
            sum_g = []
            for j in range(N):
                sum_di_g.append(alphas[t][i]*A[i][j]*B[j][o_1]*betas[t+1][j])

            #di_gammas.append(sum_di_g)
            di_g_t.append(sum_di_g)
            g.append(sum(sum_di_g))

        di_gammas.append(di_g_t)
        gammas.append(g)
        
    #Case for T
    gammas.append([alphas[-1][i] for i in range(N)])

    return di_gammas, gammas


def re_estimate_param(A, B, init, di_gammas, gammas, seq):
    N = len(init[0])
    M = len(B[0])
    T = len(seq)
    init_rtn = []
    A_rtn = []
    B_rtn = []

    #Re estimate init
    for i in range(N):
        init_rtn.append(gammas[0][i])

    #Re estimate A
    for i in range(N):
        den = 0
        ai = []
        for t in range(T-1):
            den = den + gammas[t][i]
        for j in range(N):
            num = 0
            for t in range(T-1):
    
                num =  num + di_gammas[t][i][j]
            ai.append(num/den)

        A_rtn.append(ai)

    #Re estimate B
    for i in range(N):
        den = 0
        bi = []
        for t in range(T):
            #print(gammas[t][i])
            den = den + gammas[t][i]
        for j in range(M):
            num = 0
            for t in range(T):
                if seq[t] == j:
                    num += gammas[t][i]
            bi.append(num/den)
        B_rtn.append(bi)
    
    init_rtn = [init_rtn]
    return A_rtn, B_rtn, init_rtn

#Read the input, init delta
A, B, init, seq = read_input()

'''
#Compute alpha, beta, di-gamma and gamma
alphas, scale_vec = forward_alg(A, B, init, seq)
betas = backward_alg(A, B, init, seq, scale_vec)
di_gammas, gammas = compute_gammas(A, B, seq, alphas, betas)

#print(gammas[0])


#Re-Estimate A, B. Pi
A, B, init = re_estimate_param(A,B,init, di_gammas, gammas, seq)
'''

'''
print('A: ', A)
print('B: ', B)
print('Init: ', init)
'''

max_i = 300
for i in range(max_i):
    alphas, scale_vec = forward_alg(A, B, init, seq)
    betas = backward_alg(A, B, init, seq, scale_vec)
    di_gammas, gammas = compute_gammas(A, B, seq, alphas, betas)

    #print(gammas[0])


    #Re-Estimate A, B. Pi
    A, B, init = re_estimate_param(A,B,init, di_gammas, gammas, seq)



print('A: ', A)
print('B: ', B)
print('Init: ', init)


'''
print("Alphas: ", alphas[:3])
print("First gamma: ", gammas[0])
'''
#print("Betas: ", betas)