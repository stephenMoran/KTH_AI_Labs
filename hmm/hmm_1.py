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


def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        #print('lines: ', lines[0])
        A = build_matrix([float(n) for n in lines[0].split()])
        B = build_matrix([float(n) for n in lines[1].split()])
        init = build_matrix([float(n) for n in lines[2].split()])
        seq = [int(n) for n in lines[3].split()[1:]]

    return A, B, init, seq


#Forward algorithm
def forward_alg(A, B, init, seq):
    #Evaluate a0
    init = init[0]
    N = len(init)
    o_0 = seq[0]
    a0 = []
    to_rtn = []
    for i in range(N):
        a0.append(init[i]*B[i][o_0])

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



#Read the input
A, B, init, seq = read_input('input.txt')

'''
print('A: ', A)
print('B: ', B)
print('Init: ', init)
print('Seq: ', seq)
'''

for_alg = forward_alg(A, B, init, seq)

print(for_alg)
#Sum probsabilities for the last alpha
print('sum: ', sum(for_alg[-1]))

#Forward algorithm
