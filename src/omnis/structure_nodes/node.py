import numpy as np

def nodeProcessing(node, _input, _all=None):
    if _all is None: 
        return list(map(node["action"], list(filter(node["condition"], _input))))
    else:
        return node["action"](list(filter(node["condition"], _input)))

test_nodes = {
    "*1": {"condition": lambda _: True, "action": lambda x: x*1},
    "+2": {"condition": lambda _: True, "action": lambda x: x+2},
    "+3": {"condition": lambda _: True, "action": lambda x: x+3},
    "+4": {"condition": lambda _: True, "action": lambda x: x+4},
    "+5": {"condition": lambda _: True, "action": lambda x: x+5},
    "soma_a_b": {"condition": lambda _: True, "action": lambda x: sum(x)},
    "output":{"condition": lambda _,: True, "action": lambda _: print(f"Resposta:{_}")},
}

regras = [
    {"input":['a'], "node":'*1', "save_as":'A'},
    {"input":['b'], "node":'+5', "save_as":'B'},
    {"input":['B'], "node":'+3', "save_as":'C'},
    {"input":['A', 'C'], "node":'soma_a_b', "save_as":'R', "all":True},
    {"input":['R'], "node":"output", "save_as":'R'}
]


def NodeReader(rules, available_nodes, inputs):
    answer={}
    for step in rules:
        _use = answer if any(x in answer for x in step['input']) else inputs
        value = np.array([_use[k] for k in step['input']]).ravel()
        answer[step['save_as']] = nodeProcessing(available_nodes[step['node']], value, step.get('all'))
        print(f"Usando valor: {value}, no node {step['node']}...")
        print(f"node {step['node']} respondeu com : {answer[step['save_as']]}, salvando como {step['save_as']}")
    return answer