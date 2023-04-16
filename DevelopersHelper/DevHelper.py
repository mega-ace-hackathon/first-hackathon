import json
import hashlib

def GenerateTEAL(filename : str):
    data = {}
    with open(filename, 'rb') as file:
        data = json.load(file)
    
    teal_top = "#pragma version 6\ntxn NumAppArgs\nint 0\n==\n"
    teal_bottom = ""
    sig_list = []
    for interf in data['Interfaces']:
        (teal_top, teal_bottom) = process_interface(interf, teal_top, teal_bottom, sig_list)

    teal = teal_top + teal_bottom + add_support_interface_method(sig_list)
    return teal  #should return your generated TEAL code


# helpers

def process_interface( interface, teal_top, teal_bottom, sig_list):
    name = interface['name']
    desc = interface['desc']
    methods = interface['methods']
    for m in methods:
        (teal_top, teal_bottom ) = process_method(m, teal_top, teal_bottom, sig_list)
    return (teal_top, teal_bottom)

def process_method(method, t_t, t_b, sig_list):
    call_config = method["call_config"]
    name = method['name']
    args = method['args']
    returns = method['returns']
    
    if "readonly" in method:
        readonly = method["readonly"]
    
    (x, y) = compute_selector(name, args, returns)

    sig_list.append(x)
    route = add_route(name, y)
    call_teal = process_call_config(call_config)
    method_teal = ""
    if name != "supportsInterface":
        method_teal = f"{name}:\n{call_teal}byte {x}\nint 1\nreturn\n"

    t_t += route
    t_b += method_teal
    return (t_t, t_b)

def add_support_interface_method(sig_list):
    method_teal = "supportsInterface:\n"
    for s in sig_list:
        method_teal += f"txna ApplicationArgs 1\nbyte {s}\n==\nbnz success\n"
    
    method_teal += "int 0\nreturn \nsuccess:\nint 1\nreturn\n"
    return method_teal

def process_call_config( call_configs):
    for call_config in call_configs:
        teal = ""
        for k in call_config:
            teal += f"txn {k}\n"
            val = call_config[k].split()
            if val[1] == "0":
                teal += f"int {val[1]}\n"
            if val[1] in ["NoOp", "UpdateApplication","DeleteApplication", "CloseOut"]:
                teal += f"int {val[1]}\n"
            if len(val[1]) == 58:
                teal += f"addr {val[1]}\n"
            if val[0] == 'eq':
                teal += "==\n"
            if val[0] == 'neq':
                teal += "!=\n"
            teal += "&&\n"
        teal += "assert\n"
        return teal

def compute_selector( method_name, method_args, method_returns):
    args = ""
    for a in method_args:
        args += a["type"] + ',' 
    ret = method_returns["type"]
    signature = f"{method_name}({args[:-1]}){ret}"
    h = hashlib.new("sha512_256")
    h.update(signature.encode())
    hash = h.digest()
    val = '0x' + (hash[0:4]).hex()
    return (val, signature)

def add_route(name, sig):
    teal = f'txna ApplicationArgs 0\nmethod "{sig}"\n==\nbnz {name}\n'
    return teal