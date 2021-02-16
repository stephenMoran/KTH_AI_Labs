import sys 

class HMM():
    def __init__(self): 
        self.hello = []

    def div_chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    def build_matrix(self, line_in):
        col = int(line_in[1])
        
        to_rtn = list(self.div_chunks(line_in[2:], col))
        return to_rtn
    
    def get_lines(self): 
        lines = []
        for line in sys.stdin: 
            lines.append(line)
        return lines

    
    def read_input(self):
        lines = self.get_lines()
        A = self.build_matrix([float(n) for n in lines[0].split()])
        B = self.build_matrix([float(n) for n in lines[1].split()])
        init = self.build_matrix([float(n) for n in lines[2].split()])

        return A, B, init[0]
    
    
    def matrix_multiply(self, m_a, m_b): 
        result = []
        for i in range(len(m_b[0])): #iterate over column 
            total = 0
            for j in range(len(m_a)): #iterate over rows
                total += float(m_a[j]) * float(m_b[j][i])
            result.append(total)
        return result

def create_output(result):
    row = 1 
    column = len(result)
    output = str(row) + " " + str(column)
    for i in result: 
        output += " " + str(i)
    print(output)

def main(): 
    hmm0 = HMM()
    A, B, pi =  hmm0.read_input()
    res = hmm0.matrix_multiply(pi,A)
    res = hmm0.matrix_multiply(res,B)
    create_output(res)

if __name__ == "__main__": 
    main()

    

