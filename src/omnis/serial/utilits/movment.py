from ..util.customException import axisundefined

convert = lambda _array, _convert: tuple(_array) if _convert else _array

def setPositon(vector, **kargs):
    
    # Cria vetor de movimentos com o maior tamanho nescessário.
    
    ordem = [[] for _ in range(len(vector))]
    try:
        # Desccompacta no formato 'eixo, cordenada' e salva em uma tupla se for para esperar o movimento, e em lista caso posso prosseguir.
        [ordem[v['channel']].append(convert([v["axis"],kargs.get("replace")[v["axis"]] if v['coordinate'] == "variable" else v['coordinate']], v['await'])) for v in vector]
    except KeyError as axis:
        raise axisundefined(axis,kargs.get("id"),kargs)
    except TypeError:
        print(f"Você definiu algum eixo como 'variable', mas o 'replace' está ausente. Favor conferir! [{kargs.get('id')}]")
        raise
    # Limpra as posições que não foram usadas.
    ordem = list(filter(None, ordem))
    # print(ordem)
    # Executa a função de movimentação passando as posições como *args, define se 'nonsync'
    # é True ou False/None com base no tipo da variavel da posição (lista ou tupla)
    if kargs.get('function'):
        [list(map(lambda a: kargs.get('function')("sending: ", *a, nonsync=None if isinstance(l[0], tuple) else True), [l])) for l in ordem]
    return ordem

def showMoves(name, *args, **kwargs):
    # print(f"{name}")
    if not kwargs.get('nonsync'):
        pass
        #print( "await...")
        #time.sleep(2)
    for k in args:
        print(k)
        pass
        #print(k)

"""
movments ={
    "get":[
        [
            {"axis": "X", "coordinate": 0.0, "channel": 0, "await":False},
            {"axis": "Y", "coordinate": 0.0, "channel": 0, "await":False},
            {"axis": "F", "coordinate": 150000.0, "channel": 0, "await":False},     #// Define a velocidade de movimentação do conjunto no canal 0

            {"axis": "Z", "coordinate": 0.0, "channel": 1, "await":True },
            {"axis": "E", "coordinate": 0.0, "channel": 1, "await":True },
            {"axis": "F", "coordinate": 150000.0, "channel": 1, "await":True},      #// Define a velocidade de movimentação do conjunto no canal 1

            {"axis": "A", "coordinate": 0.0, "channel": 2, "await":False},
            {"axis": "B", "coordinate": 0.0, "channel": 2, "await":False},
            {"axis": "F", "coordinate": 150000.0, "channel": 2, "await":False},     #// Define a velocidade de movimentação do conjunto no canal 2

            {"axis": "D", "coordinate": 0.0, "channel": 3, "await":True },
            {"axis": "F", "coordinate": 150000.0, "channel": 3, "await":True},      #// Define a velocidade de movimentação do conjunto no canal 3

            {"axis": "C", "coordinate": 0.0, "channel": 4, "await":False},
            {"axis": "F", "coordinate": 9000.0, "channel": 4, "await":True}        #// Define a velocidade de movimentação do conjunto no canal 4

            
        ],
        [
            #// Não houve definição de velocidade, portanto o marlin mantem a velocidade atual. ( 9000 ) passada no eixo "C", canal 4,  do bloco anterior.
            {"axis": "X", "coordinate": 10.0, "channel": 0, "await":False},
            {"axis": "Y", "coordinate": 20.0, "channel": 0, "await":False},
            {"axis": "Z", "coordinate": 30.0, "channel": 1, "await":True },
            {"axis": "E", "coordinate": 40.0, "channel": 1, "await":True },
            {"axis": "A", "coordinate": 50.0, "channel": 2, "await":False},
            {"axis": "B", "coordinate": 60.0, "channel": 2, "await":False},
            {"axis": "D", "coordinate": "variable", "channel": 3, "await":True },
            {"axis": "C", "coordinate": "variable", "channel": 4, "await":False}
        ]   
    ]
}
#Função de movimento que receber argumento de eixo e posição,
#"(Eixo, posição), nonsync=True"

def movefunc(name, *args, **kwargs):
    print(f"{name}")
    if not kwargs.get('nonsync'):
        print( "await...")
        #time.sleep(2)
    for k in args:
        print(k)

#movendo de forma dinamica com base no dicionário pre-definido.
for steps in movments.values():
    for moves in steps:
        setPositon(moves, movefunc, replace={'C':700})
"""

