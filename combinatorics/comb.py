print('combinatorics/comb.py')
from typing import overload
from itertools import permutations, combinations, combinations_with_replacement as comb_w_rep, product
from string import ascii_uppercase, ascii_lowercase
from pprint import pprint
import re
from copy import deepcopy
from collections import defaultdict
from math import factorial

import doctest

_print = deepcopy(print)
def newprint(*args, **kwargs):
    if len(args)>1:
        if kwargs.get('sep') is not None:
            sep =  kwargs.get('sep')
        else:
            sep =  ', '
        s = sep.join(args)
    elif len(args) == 1:
        s = args[0]
    else:
        s=""
    _print(dim_ver(bold_num(s)), **kwargs)
print=newprint

def fac_str(start, stop=1):
    length = start - stop + 1
    if length <= 6:
        string = f"{start}"
        for n in reversed(range(stop, start)):
            if n == 0:
                n = 1
            string += f"·{n}"
        if string == "0":
            return 1
        return string
    if start - 1 > stop:
        return f"{start}·{start-1}·…·{stop}"
    else:
        return f"{start}·…·{stop}"
    
def fac(a, b=None):
    """
    Inclusive both sides.
    
    >>> all(fac(n) == factorial(n) == fac(0, n) == fac(1, n) for n in range(7))
    True
    
    >>> [f'2→{n}={fac(2, n)}' for n in range(7)]
    ['2→0=2', '2→1=2', '2→2=2', '2→3=6', '2→4=24', '2→5=120', '2→6=720']
    
    >>> [f'{n}→2={fac(n, 2)}' for n in range(7)]
    ['0→2=2', '1→2=2', '2→2=2', '3→2=6', '4→2=24', '5→2=120', '6→2=720']
    
    >>> [f'3→{n}={fac(3, n)}' for n in range(7)]
    ['3→0=6', '3→1=6', '3→2=6', '3→3=3', '3→4=12', '3→5=60', '3→6=360']
    
    >>> [f'{n}→3={fac(n, 3)}' for n in range(7)]
    ['0→3=6', '1→3=6', '2→3=6', '3→3=3', '4→3=12', '5→3=60', '6→3=360']
    
    """
    
    if b is None:
        return factorial(a)
    high = max(a,b)+1
    low = min(a,b) or 1
    mult = 1
    # mult = start if start!=0 else 1
    for n in range(low, high):
        mult = mult * n
    return mult




def bold_num(s):
    bold = re.sub(r"\d+\b", lambda match: f"\x1b[1m{match.group()}\x1b[0m", s)
    return bold



def dim_ver(s):
    if 'I' in s:
        dim = re.sub(r"(vI+[ab]?|(?<=\))I+)", lambda match: f"\x1b[97m{match.group()}\x1b[0m", s)
        return dim
    else:
        return s

    
    
###############
# ORDER MATTERS
###############

def P(n, k, *, explain=True, example=False, identities=False):
    if isinstance(n, int):
        rv = len(list(permutations(range(n), k)))
        if explain:
            print(
                f"P({n},{k})",
                f"{rv} ways to organize {k} letters from a collection of {n} letters",
                "• Order matters, so 'BA' and 'AB' are both counted.",
                "• No repetitions allowed",
                sep="\n\t",
            )
        if identities:
            print(P_id(n, k, "I"))
            print(P_id(n, k, "II"))
            print(P_id(n, k, "III"))
        if example:
            print(f"\n\x1b[1mP Examples\x1b[0m")
            letters = ascii_uppercase[:n]
            print(f"P({n},{k}) from {letters}:")
            [print(f"{i}:\t", *perm, sep="") for i, perm in enumerate(permutations(letters, k), 1)]

    else:
        rv = list(permutations(n, k))
    return rv

def P_id(n, k=1, v=None):
    v1 = f"P({n},{k}) vI  = {fac_str(n, n-k+1)}"
    v2 = f"P({n},{k}) vII = ({fac_str(n)})/({fac_str(n-k)}) = {fac(n)}/{fac(n-k)}"
    v3 = f"P({n},{k}) vIII = ({fac_str(k)}) · ( ({fac_str(n, n-k+1)})/({fac_str(k)}) ) = {fac(k)} · {fac(n, n-k+1)}/{fac(k)}"
    if "III" in v:
        return v3
    elif "II" in v:
        return v2
    else:
        return v1

def P_spam(*, byres=False):
    results = defaultdict(list)
    for n in range(1, 10):
        for k in range(1, 10):
            if k > n:
                continue
            rv = P(n,k,example=False,explain=False,identities=False)
            if byres:
                results[rv].append(f"P({n},{k})")
            else:
                print(f"P({n},{k}): {rv}")
        
    if byres:
        for res, how in sorted(results.items()):
            print(f"{res}:\t{', '.join(how)}")
     

    
    
    
    
def Q(n, k, *, explain=True, example=False):
    _Pn = n+k-1
    if isinstance(n, int):
        rv = len(list(permutations(range(_Pn), k)))
        kia = ascii_uppercase[:k]
        vlines = "|" * (n-1)
        if explain:
            if kia:
                orderstr = f"• Order matters, so '{kia}{vlines}' and '{kia[1:]}{kia[0]}{vlines}' are both counted"
            else:
                orderstr="• Order matters, so '△◯|' and '◯△|' are both counted"
            print(
                f"Q({n},{k})",
                f"{rv} ways to organize {k} distinct objects into {n} bins",
                orderstr,
                "• No repetitions allowed",
                sep="\n\t",
            )
        
        if example:
            letters = ascii_uppercase[:k] + vlines
            [print(f"{i}:\t", *comb, sep="") for i, comb in enumerate(set(permutations(letters, len(letters))), 1)]

            print()

    else:
        rv = list(permutations(n, k))
    return rv
    

    
    
    
    
    
def Pnk(n, *nks):
    if isinstance(n, int):
        denominator = 1
        for nk in nks:
            denominator = denominator*fac(nk)
        rv = fac(n)/denominator
    else:
        raise NotImplementedError
    
    return int(rv)
    

def Pnk_spam(*, byres=False, ofnum=None):
    results = defaultdict(list)
    for n in range(2, 11):
        for n1 in range(1, 11):
            if n1>n//2:
                continue
            n2=n-n1
            rv = Pnk(n, n1, n2)
            how = f"P({n}; {n1},{n2})"
            if byres or (ofnum is not None):
                results[rv].append(how)
            else:
                print(f"{how}: {rv}")
        print()       
        
    if ofnum is not None:
        print(f"{ofnum}:\t{', '.join(results[ofnum])}")
    
    elif byres:
        for res, how in sorted(results.items()):
            print(f"{res}:\t{', '.join(how)}")
       
    
    
    
    
    
    
    
    
    
            
def nk(n,k, *, example=False):
    if isinstance(n, int):
        rv = n**k
        if example:
            print("\n\x1b[1mnk Examples\x1b[0m")
            letters = ascii_uppercase[:n]
            print(f"{n}^{k} from {letters}:")
            
            
            perms = sorted(set(permutations(letters, k)).union(comb_w_rep(letters, k)))
            [print(f"{i}:\t", *perm, sep="") for i, perm in enumerate(perms, 1)]
            
#             for i in range(n):
#                 # print "AA", "BB"... which `permutations` doesn't yield
#                 real_i = len(perms)+i+1
#                 print(f"{real_i}:\t", letters[i]*k, sep="")
            
        print()
    else:
        raise NotImplementedError
    
    return rv

def nk_spam(n,k):
    pass


#######################
# ORDER DOES NOT MATTER
#######################

def C(n, k, *, explain=True, example=False, identities=False):
    if isinstance(n, int):
        rv = len(list(combinations(range(n), k)))
        if explain:
            kia = ascii_uppercase[:k]
            if kia:
                orderstr = f"• Order doesn't matter, so '{kia}' and '{kia[1:]}{kia[0]}' count as one thing"
            else:
                orderstr=f"• Order doesn't matter"
            print(
                f"C({n},{k}) vI",
                f"{rv} ways to select {k} different letters from {n} letters",
                f"set {set(range(1, n+1))} has {rv} subsets whose size={k}",
                orderstr,
                f"• No repetitions allowed",
                sep="\n\t",
            )

        if identities:
            print(C_id(n, k, v="I"))
            _k = n - k
            _rv = len(list(combinations(range(n), _k)))
            print(f"C({n},{_k}) vII = {_rv} ways to select {_k} different letters from {n} letters")
            print(C_id(n, k, v="II"))
        if example:
            print("\n\x1b[1mC Examples\x1b[0m")
            letters = ascii_uppercase[:n]
            print(f"C({n},{k}) from {letters}:")
            [print(f"{i}:\t", *comb, sep="") for i, comb in enumerate(combinations(letters, k), 1)]
            if identities:
                print(f"C({n},{_k}) from {letters}:")
                [print(f"{i}:\t", *comb, sep="") for i, comb in enumerate(combinations(letters, _k), 1)]
            print()

    else:
        rv = list(combinations(n, k))
    return rv

def C_spam(*, byres=False):
    results = defaultdict(list)
    for n in range(1, 11):
        for k in range(1, 11):
            if k > n:
                continue
            rv = C(n,k,example=False,explain=False,identities=False)
            if byres:
                results[rv].append(f"C({n},{k})")
            else:
                print(f"C({n},{k}): {rv}")
    if byres:
        for res, how in sorted(results.items()):
            print(f"{res}:\t{', '.join(how)}")
        
def C_id(n, k, v)->str:
    v1 = f"C({n},{k}) vI  = P({n},{k})/P({k}) = ({fac_str(n, n-k+1)})/({fac_str(k)}) = {fac(n, n-k+1)}/{fac(k)}"
    
    _k = n - k
    v2 = f"C({n},{_k}) vII = P({n},{_k})/P({_k}) = ({fac_str(n, n-_k+1)})/({fac_str(_k)}) = {fac(n, n-_k+1)}/{fac(_k)}"
    
    if "II" in v:
        return v2
    else:
        return v1
    
    




    
        
        

def D(n, k, *, explain=True, example=False, identities=False):
    if isinstance(n, int):
        _Cn1 = n - 1 + k
        rv = C(_Cn1, k, explain=False, example=False, identities=False)
        balls = "○" * k
        eq_vars = "+".join(ascii_lowercase[:n])
        
        if explain:
            print(
                f"D({n},{k}) vI",
                f"{rv} ways to place {k} identical balls in {n} partitions",
                f"{rv} ways to choose {k} from '{ascii_uppercase[:n]}' with repetition",
                f"{rv} possible solutions to {eq_vars}={k}",
                "• With repetitions",
                f"• Order doesn't matter, so '{balls}' and '{balls}' count as one thing",
                sep="\n\t",
            )
        if identities:
            print(f"D({n},{k}) vIa  = {C_id(_Cn1, k, 'I')} = {rv}")
            print(f"D({n},{k}) vIb  = {C_id(_Cn1, k, 'II')} = {rv}\n")
            C(_Cn1, k, explain=explain, example=example, identities=False)
            print()
            # D(n,k) = D(k+1, n-1)
            _Dk2 = n - 1
            _Dn2 = k + 1
            if explain:
                print(f"D({_Dn2},{_Dk2}) vII",
                      f"{rv} ways to place {_Dk2} balls in {_Dn2} partitions",
                      f"{rv} ways to choose {_Dk2} from '{ascii_uppercase[:_Dn2]}' with repetition",
                      f'{rv} possible solutions to {"+".join(ascii_lowercase[:_Dn2])}={_Dk2}',
                      sep='\n\t'
                     )
            print(f"D({_Dn2},{_Dk2}) vIIa = {C_id(_Cn1, _Dk2, 'I')}")
            print(f"D({_Dn2},{_Dk2}) vIIb = {C_id(_Cn1, _Dk2, 'II')}\n")
            C(_Cn1, _Dk2, explain=explain, example=example, identities=False)
        if example:
            _print(f"\n\x1b[1mD({n},{k}) Examples\x1b[0m")
            letters = "◯" * k + "|" * (n - 1)
            [print(f"{i}:\t", *comb, sep="") for i, comb in enumerate(set(permutations(letters, len(letters))), 1)]
            if identities:
                _print(f"\n\x1b[1mD({_Dn2},{_Dk2}) Examples\x1b[0m")
                letters = "◯" * _Dk2 + "|" * (_Dn2 - 1)
                [print(f"{i}:\t", *comb, sep="") for i, comb in enumerate(set(permutations(letters, len(letters))), 1)]

            print()
    else:
        letters = ascii_uppercase[:k] + "|" * (n - 1)
        rv = C(letters, k, example=example)
    return rv


def D_spam(*, byres=False, ofnum=None):
    results = defaultdict(list)
    for n in range(1, 11):
        for k in range(1, 11):
            rv = D(n,k,example=False,explain=False,identities=False)
            if byres or (ofnum is not None):
                results[rv].append(f"D({n},{k})")
            else:
                print(f"D({n},{k}): {rv}")
    
    if ofnum is not None:
        print(f"{ofnum}:\t{', '.join(results[ofnum])}")
    
    elif byres:
        for res, how in sorted(results.items()):
            print(f"{res}:\t{', '.join(how)}")



def C2D(n, k):
    """
    D(3,5) prints C(7,5) and C(7,2).
    C2D(7,2) prints D(6,2), D(6,5)
    """
    D(n - k + 1, k, identities=True)
    
    
    
# doctest.testfile(__file__, module_relative=False, globs=globals(), optionflags=doctest.ELLIPSIS)

# for n in range(7):
#     assert fac(n) == factorial(n) == fac(0, n) == fac(1, n)
#     assert fac(2, n) == fac(n)