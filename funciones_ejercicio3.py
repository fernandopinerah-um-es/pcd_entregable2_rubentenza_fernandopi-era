from functools import reduce

temperaturas = [31.1, 32.1, 32.2, 33.0, 33.5, 33.0, 32.7]

def media(temperaturas):
    return reduce(lambda x, y: x+y, temperaturas)/len(temperaturas)

def median(temperaturas):
    temperaturas.sort()
    if len(temperaturas)%2 == 0:
        return reduce(lambda x,y : x+y/2, temperaturas[(len(temperaturas)//2):(len(temperaturas)//2)+1])
    else:
        return temperaturas[len(temperaturas)//2]
    
def dev_tipica(temperaturas):
    media_tem = media(temperaturas)
    variacion = list(map(lambda x: (x-media_tem)**2, temperaturas))
    sum_variacion = sum(variacion)
    promedio_sum = sum_variacion/len(temperaturas)
    return (promedio_sum)**0.5

def sobrepasar(temperaturas, limite):
    bool=list(map(lambda x: x>limite, temperaturas))
    if True in bool:
        return True
    else: return False

def sobrepasar_tiempo(temperaturas, limite):
    bool=list(map(lambda x, y: abs(x-y)>=limite, temperaturas, temperaturas[1:]))
    if True in bool:
        return True
    else: return False