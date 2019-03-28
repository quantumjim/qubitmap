from PIL import Image
import numpy as np
import random

try:
    from apng import APNG
except:
    pass


def save_frames (frame_list,scale=None) :
    
    size = tuple([L+1 for L in max(frame_list[0])])
    
    filename_list = []
    for f in range(len(frame_list)):
        frame = frame_list[f]

        img = Image.new('RGB',size)

        for x in range(img.size[0]):
            for y in range(img.size[1]):
                img.load()[x,y] = frame[x,y]

        if scale:
            img = img.resize(scale)

        filename = 'output/frame'+str(f)+'.png'
        img.save(filename)
        filename_list.append(filename)

    try:
        APNG.from_files(filename_list, delay=100).save("output/result.png")
    except:
        pass


# this is made from github.com/qiskit/qiskit-tutorials/community/games/random_terrain_generation.ipynb
# it needs to be redone in order to comply with the rules
def make_grid(n,center=None,shuffle=True):

    if not center:
        center = '0'*n

    Lx = int(2**np.ceil(n/2))
    Ly = int(2**np.floor(n/2))

    strings = {}
    for y in range(Ly):
        for x in range(Lx):
            strings[(x,y)] = ''

    for (x,y) in strings:
        for j in range(n):
            if (j%2)==0:
                xx = np.floor(x/2**(j/2))
                strings[(x,y)] = str( int( ( xx + np.floor(xx/2) )%2 ) ) + strings[(x,y)]
            else:
                yy = np.floor(y/2**((j-1)/2))
                strings[(x,y)] = str( int( ( yy + np.floor(yy/2) )%2 ) ) + strings[(x,y)]

    if shuffle:
        order = [j for j in range(n)]
        random.shuffle(order)

        for (x,y) in strings:
            new_string = ''
            for j in order:
                new_string = strings[(x,y)][j] + new_string
            strings[(x,y)] = new_string

    current_center = strings[ ( int(np.floor(Lx/2)),int(np.floor(Ly/2)) ) ]
    diff = ''
    for j in range(n):
        diff += '0'*(current_center[j]==center[j]) + '1'*(current_center[j]!=center[j])
    for (x,y) in strings:
            newstring = ''
            for j in range(n):
                newstring += strings[(x,y)][j]*(diff[j]=='0') + ('0'*(strings[(x,y)][j]=='1')+'1'*(strings[(x,y)][j]=='0'))*(diff[j]=='1')
            strings[(x,y)] = newstring
            
    return strings


def image2state(image,grid):
    
    N = len(grid)
    state = [[0]*N,[0]*N,[0]*N]

    for pos in image:
        for j in range(3):
            state[j][ int(grid[pos],2) ] = image[pos][j]

    for j in range(3):        
        Z = sum(np.absolute(state[j])**2)
        state[j] = [amp / np.sqrt(Z) for amp in state[j]]
        
    return state


def counts2image(counts,grid):
    
    image = { pos:[0,0,0] for pos in grid}

    for j in range(3):

        rescale = 255/max(counts[j].values())

        for pos in image:
            try:
                image[pos][j] = int( rescale*counts[j][grid[pos]] )
            except:
                image[pos][j] = int( rescale*counts[j][grid[pos]] )

    for pos in image:
        image[pos] = tuple(image[pos])

    return image


def ket2counts (ket):
    
    counts = {}
    
    N = len(ket)
    n = int( np.log(N)/np.log(2) )
        
    for j in range(N):
        
        string = bin(j)[2:]
        string = '0'*(n-len(string)) + string
        
        counts[string] = np.absolute(ket[j])**2
    
    return counts

def ask4gate(qc,q):

    c1 = True
    while c1:
        gate= input('> Select a gate to apply by typing x, y, h, q, qdg or cx\n').lower()
        if gate in ('x','y','h','q','qdg','cx'):
            c1 = False
            if gate=='cx':
                c2 = True
                while c2:
                    control = int(input('> Select a control qubit by typing a qubit number (0 to 5)\n'))
                    target = int(input('> Select a target qubit by typing a different qubit number (0 to 5)\n'))
                    if (control in range(6)) and (target in range(6)) and (control!=target):
                        qc.cx(q[control],q[target])
                        c2 = False
                    else:
                        input("> That's not a valid pair of choices. Press Enter to try again") 
            else:
                c3 = True
                while c3:
                    qubit = input('> Select a qubit by typing a qubit number (0 to 5)\n')
                    if qubit in ['0','1','2','3','4','5']:
                        if gate in ['q','qdg']:
                            eval('qc.ry('+(gate[-1]=='g')*'-'+'np.pi/8,q['+qubit+'])')
                        else:
                            eval('qc.'+gate+'(q['+qubit+'])')
                        c3 = False
                    else:
                        input("> That's not a valid choice. Press Enter to try again")
        else:
            input("> That's not a valid choice. Press Enter to try again")