from itertools import product as prod, combinations, combinations_with_replacement as cwr
from typing import Callable, Union, Tuple, Set, overload, Optional
from operator import le, lt, ge, gt, ne  # lower-equal, lower-than, greater-equal, greater-than, not-equal
from random import randint
import inspect
from pprint import pformat

powerset = lambda v: {tuple(combo) for r in range(len(v) + 1) for combo in combinations(v, r)}
cartesian_prod = lambda v:prod(v, v) # cartesian_prod({1,2}) = [(1, 1), (1, 2), (2, 1), (2, 2)]
universal_rel = lambda a,b:True
empty_rel = lambda a,b:False
identity_rel = lambda a,b:a==b
opposite_rel = lambda a,b:a==-b

# inverse_rel = lambda a,b:
R = Callable[[int, int], bool]
Prod = Set[Tuple[int, int]] # {<1,2>, <3,4>}
Vec = Set[int] # {1, 2, 3, 4}
RawRelation = Union[Tuple[R, Vec], Tuple[R,Vec,Vec]] # ( lambda a,b:... , {1,2,3}, {3,4,5}? )
Relation = Union[
    Prod, 
    RawRelation
    ] 


def is_product(thing):
    """
    Returns True if thing is Prod, i.e. is of the form { <a,b>, <c,d>, ... }. Don't care about exact types (tuples, sets, etc)
    """
    try:
        for x in thing:
            if not isinstance(x, (tuple, list)):
                return False
        return True
            
    except:
        return False


def is_raw_relation(thing):
    """
    Returns True if thing is (lambda, Vec, Vec?)
    """
    try:
        length = len(thing)
        if not isinstance(thing, (tuple, list)) or length < 2 or length > 3:
            return False
        
        maybe_ok = callable(thing[0]) and isinstance(thing[1], (list,tuple,set))
        if length == 3:
            return maybe_ok and isinstance(thing[2], (list,tuple,set))
        else:
            return maybe_ok
        
    except:
        return False

def partition_to_equiv_classes(prod:Prod)->Prod:
    """
    >>> partition = { (1,2,), (3,) }
    >>> partition_to_equiv_classes(partition)
    {(1, 1), (1, 2), (2, 1), (2, 2), (3, 3)}
    """
    if not is_product(prod):
        raise ValueError(f"partition_to_equiv_classes(prod) expecting a 2D+ structure, got {pformat(prod)}")
    equiv_classes = set()
    for subset in prod:
        for x in cartesian_prod(subset):
            equiv_classes.add(x)
    return equiv_classes
    
def get_lambda_src(rel:R):
    try:
        fn_srcline:str=inspect.getsourcelines(rel)[0][0].strip()
    except TypeError:
        return rel.__qualname__
    if 'lambda' in fn_srcline:
        _,_,after_lam = map(str.strip,fn_srcline.partition('lambda'))
        lam_content,_,_=map(str.strip,after_lam.partition(' '))
        if ' ' in after_lam:
            return f'`lambda {lam_content[:-1]}`'
        else:
            return f'`lambda {lam_content}`'
    else:
        return fn_srcline

def randset(length, start=None, stop=None) -> Set[int]:
    """
    `start` is inclusive, `stop` is exclusive.
    >>> randset(10) == {-4, -3, -2, -1, 0, 1, 2, 3, 4}
    True

    >>> randset(5, 1, 4)
    {1, 2, 3}
    
    >>> 15 <= sum(randset(5, 1, 7)) <= 20
    True
    """
    if start is None and stop is None:
        if length % 2 == 0:
            length -= 1
        half = length // 2
        start = -half
        stop = half + 1
        tmp = set(range(start, stop))
        return tmp
    tmp = set()
    stop -= 1  # randint stop is inclusive
    tmp_len = len(tmp)
    while tmp_len < length and tmp_len < stop - start + 1:
        tmp.add(randint(start, stop))
        tmp_len = len(tmp)
    return tmp


def relate(rawrelation: Relation, *, quiet=True)->Prod:
    """Creates a relation between vec1 and vec2? by filtering their cartesian product.
    If only one vector is given, creates a relation between it and itself (vec1×vec1).
    Basically, `for x in A: for y in B: yield <x,y> if rel(x,y)`
    Returns a set of ordered pairs that's a subset of cart product.
    Examples:
    
    >>> V = {1, 2, 3}
    >>> relate(lambda a,b: a>b, V)
    {(3, 1), (3, 2), (2, 1)}
    
    >>> relate(gt, V) # same as example above
    {(3, 1), (3, 2), (2, 1)}
    
    >>> V_cart_prod = set(cartesian_prod(V))
    >>> relate(universal_rel, V) == V_cart_prod
    True
    """
    if quiet:
        qprint= lambda *args, **kwargs: True
    else:
        qprint = print
    if not is_raw_relation(rawrelation):
        if not is_product(rawrelation):
            raise ValueError(f"relate() | not a raw relation, not a product: {rawrelation}")
        print(f"WARN relate() | got a product, returning as is: {rawrelation}")
        return rawrelation
    relation = set()
    
    
    if len(rawrelation) == 3:
        fn, vec1, vec2 = rawrelation
    else:
        fn, vec1 = rawrelation
        vec2 = None
    fn_src=get_lambda_src(fn)
    if vec2 is None:
        sig_repr=f'relate({fn_src}, vec1 ({len(vec1)}) × vec1)'
            
        vec2=vec1
    else:
        
        sig_repr=f'relate({fn_src}, vec1 ({len(vec1)}) × vec2 (({len(vec2)}))'
            

    print(f'{sig_repr} |\n\t{vec1=}\n\t{vec2=}')
    
    for x,y in prod(vec1,vec2):
        if fn(x, y):
            relation.add((x, y))        
            qprint(f'\trelate() | added <x:{x}, y:{y}>')
    if quiet:
        print(f'{sig_repr} → {{ < , > ... }}({len(relation)})')
    else:
        print(f'{sig_repr} → {relation}')
    return relation

@overload
def multiply(relation: Relation,*, quiet=True)->Prod:
    """
    If (R:lambda, vec1, vec2), then R^2 of vec1 × vec2. 
    If (R:lambda, vec1), then R^2 of vec1 × vec1.
    If a single product, then product·product.
    """
    ...
@overload
def multiply(relation1: Relation, relation2:Relation,*, quiet=True)->Prod:
    """
    If (R1:lambda, vec1a, vec1b?), (R2:lambda, vec2a, vec2b?), then (R1 over vec1a×vec1b)·(R2 over vec2a×vec2b)
    if two products, then prod1 · prod2
    """
    ...

def multiply(relation1, relation2 = None, *, quiet=True)->Prod:
    """
    R1: A -> B, R2: B -> C; R1·R2 = {<a,c> ∈ A×C | ∃b ∈ B(aR1b ∧ bR2c)}
    
    Each pair from R1 (a,b) is compared against each pair from R2 (b,c).
    If a pair can shake hands (b1 == b2), then <a, c> is in the multipication result.
    
    >>> multiply({(2,3),(2,5)}, {(3,3),(5,9),(6,9)})
    ...
    {(2, 3), (2, 9)}
    
    >>> vec = {-1, 0, 1}
    >>> vec_cart = relate((universal_rel, vec))
    >>> just_vec = relate((identity_rel, vec))
    >>> multiply(vec_cart, just_vec) == vec_cart
    True
    """
    if is_raw_relation(relation1):
        R1 = relate(relation1)
        if relation2:
            R2 = relate(relation2)
            print(f'multiply | two pairs of (fn:R, vec:Vec), (fn:R, vec:Vec) overload | {R1=} | {R2=}')
        else:
            R2 = None
            print(f'multiply | one pair of (fn:R, vec:Vec) overload')
    else:
        R1 = relation1
        R2 = relation2
        print(f'multiply | products multiplication overload')
    
    mutiplied = set()
    if R2 is None:
        R2 = R1
    for a, b1 in R1:
        for b2, c in R2:
            if b1 == b2:
                mutiplied.add((a, c))
                print(f'multiply() | <\x1b[1ma:{a}\x1b[0m → b:{b1} → \x1b[1mc:{c}\x1b[0m>')
    return mutiplied

def inverse(A: Prod)->Prod:
    inverted = set()
    for a, b in A:
        inverted.add((b, a))
    return inverted


def relate_sqr(rel_or_product: Union[R, Prod], vec:Vec=None, quiet=True, alt=False):
    """Computes the squared relation.
    ⟨a,c⟩ ∈ 𝑹×𝑹: {⟨a,c⟩ | ∃b ∈ A (⟨a,b⟩ ∈ 𝑹 ∧ ⟨b,c⟩ ∈ 𝑹)}
    
    Forms:
    
    Returns a set of {} 
    >>> relate_sqr(lambda a,b:a>b, {1,2,3})
    {(3, 1)}
    
    
    >>> r2 = relate_sqr({(1, 1),(2, 2)})
    identity_rel
    
    Examples:
    
    >>> V = randset(30)
    >>> opposite_of_opposite = relate_sqr(opposite_rel, V)
    >>> I = relate(identity_rel, V)
    >>> I == opposite_of_opposite
    True

    
    
    """
    
    r2 = set()
    if callable(rel_or_product):
        rel = rel_or_product
        print(f'relate_sql({get_lambda_src(rel)}, vec:{vec})')
        # relate_sqr(lambda a,b:..., {1,2,3})
        if not alt:
            for a, c in cartesian_prod(vec):
                for b in vec:
                    if rel(a, b) and rel(b, c):
                        r2.add((a, c))
                        if not quiet:
                            print(f'relate_sqr() | added <a:{a}, c:{c}> (b:{b})')
        else:
            print(f'relate_sqr() | creating relation of {get_lambda_src(rel)} over vec={vec}')
            product:Prod = relate(rel, vec, quiet=quiet)
            print(f'relate_sqr() | multiplying {product} with itself')
            r2 = multiply(product, product, quiet=quiet) 
            print(f'relate_sqr() | multiply result = r2: {r2}')
            return r2
            #return relate_sqr(product, v, quiet=quiet, alt=False)
    
    else:
        # relate_sqr({<5,6>,<7,8>})
        # p111 / q15
        
        product = rel_or_product
        if not isinstance(next(iter(product)), tuple):
            raise TypeError((f"Can create a squared relation only with either a vector and a filter function, "
                             f"or with a product (set of ordered pairs).\n"
                            f"got: {product}"))
        print(f'relate_sql({product})\n\tmultiplying product * product')
        r2 = multiply(product, product, quiet=quiet)
        print(f'relate_sqr() | multiply result = r2: {r2}')
        if vec is not None:
            # ONLY FOR DEBUGGING, v has no use here
            try:
                known_rels = dict(
                        universal_rel=universal_rel,
                        empty_rel=empty_rel,
                        identity_rel=identity_rel,
                        opposite_rel=opposite_rel,
                        lower_equal=le,
                        lower_then=lt,
                        greater_equal=ge,
                        greater_then=gt,
                        not_equal=ne
                        )
                print(next(name for name, rel in known_rels.items() if r2 == relate(product, vec)))
            except StopIteration:
                pass
    return r2
@overload
def is_symmetric(fn:R, vec:Vec,*, quiet=True):
    ...
@overload
def is_symmetric(prod:Prod, vec:Vec,*, quiet=True):
    ...
def is_symmetric(fn_or_prod: Union[R,Prod], vec:Vec, quiet=True):
    """A relation is symmetric if for every pair <a,b> in R, also <b,a> in R
    In other words: rel(a,b) is True and rel(b,a) is True
    >>> symmetric = [universal_rel, empty_rel, identity_rel, opposite_rel, ne]
    >>> all(is_symmetric(_,randset(100)) for _ in symmetric)
    |R|: ...
    |R|: ...
    True
    
    >>> not_symmetric = [lt, le, gt, ge]
    >>> any(is_symmetric(_,randset(100)) for _ in not_symmetric)
    |R|: ...
    |R|: ...
    False
    
    """
    if callable(fn_or_prod):
        fn = fn_or_prod
        product = relate((fn, vec))
        def _cond(_x,_y):
            return fn(_y,_x) and (_y,_x) in product
    else:
        product = fn_or_prod
        def _cond(_x,_y):
            return (_y,_x) in product
    # relation = relate((rel, v1), quiet=quiet)
    # rel_len = len(relation)
    # if not quiet:
    #     try:
    #         print(f'|R|: {rel_len} ({(rel_len / len((set(prod(v1, v1))))) * 100}%)')
    #     except ZeroDivisionError:
    #         pass
    for x, y in product:
        if not _cond(x, y):
            print(f'fail: <x:{x}, y:{y}> OK but <y:{y}, x:{x}> is not')
            return False
        if not quiet:
            print(f'good: rel(<x:{x}, y:{y}>) is True and rel(<y:{y}, x:{x}>) is True')
    return True

def is_anti_symmetric(rel: R, v1, v2=None, *, quiet=True):
    """A relation is anti symmetric if for every pair <a,b> in R, <b,a> is not in R
    In other words: rel(a,b) is True but rel(b,a) is False
    >>> anti_symmetric = [lt, gt, empty_rel] # also "⊆"
    >>> all(is_anti_symmetric(_,randset(100)) for _ in anti_symmetric)
    |R|: ...
    |R|: ...
    True
    
    >>> not_anti_symmetric = [universal_rel, identity_rel, opposite_rel, ne, le, ge, lambda a,b:b<a**2]
    >>> any(is_anti_symmetric(_,randset(100)) for _ in not_anti_symmetric)
    |R|: ...
    False
    """
    relation = relate(rel, v1, v2, quiet=quiet)
    rel_len = len(relation)
    print(f'|R|: {rel_len} ({(rel_len / len((set(prod(v1, v2 if v2 else v1))))) * 100}%)')
    for x, y in relation:
        if rel(y, x):
            if not quiet:
                print(f'fail: rel(<x:{x}, y:{y}>) is True but also rel(<y:{y}, x:{x}>) is True')
            return False
        if not quiet:
            print(f'good: rel(<x:{x}, y:{y}>) is True and rel(<y:{y}, x:{x}>) is False')
    return True

@overload
def is_reflexive(fn:R, vec:Vec,*, quiet=True):
    ...
@overload
def is_reflexive(prod:Prod, vec:Vec,*, quiet=True):
    ...

def is_reflexive(fn_or_prod: Union[R,Prod], vec:Vec,*, quiet=True):
    """A relation is reflexive if every x in v satisfies rel(x,x)
    >>> reflexive = [universal_rel, identity_rel, le, ge]
    >>> all(is_reflexive(_,randset(100)) for _ in reflexive)
    ...
    True
    >>> not_reflexive = [ne, lt, gt, empty_rel, opposite_rel]
    >>> any(is_reflexive(_,randset(100)) for _ in not_reflexive)
    ...
    False

    >>> reflexive = ((1,1),(2,2),(3,3))
    >>> is_reflexive(reflexive, {1,2})
    ...
    True
    
    """
    if callable(fn_or_prod):
        fn = fn_or_prod
        product = relate((fn, vec))
        def _cond(_x):
            return fn(_x,_x) and (_x,_x) in product
    else:
        product = fn_or_prod
        def _cond(_x):
            return (_x,_x) in product
    
    
    for x in vec:
        if not _cond(x):
        # if not fn(x, x):
            print(f'fail: <{x},{x}> is False')
            return False
        # if (x,x) not in product:
        #     raise Exception(f"fn(x,x) is True but (x,x) not in product. {x=}")
        if not quiet:
            print(f'good: <{x},{x}> is True')
    return True

def is_anti_reflexive(rel: R, v, *, quiet=True):
    """A relation is anti reflexive if no x in v satisfies rel(x,x)
    >>> anti_reflexive = [ne, lt, gt, empty_rel]
    >>> all(is_anti_reflexive(_,randset(100)) for _ in anti_reflexive)
    ...
    True
    >>> not_anti_reflexive = [universal_rel, identity_rel, opposite_rel, le, ge]
    >>> any(is_anti_reflexive(_,randset(100)) for _ in not_anti_reflexive)
    ...
    False
    
    """
    for x in v:
        if rel(x, x):
            if not quiet:
                print(f'fail: rel(<{x},{x}>) is True')
            return False
        if not quiet:
            print(f'good: rel(<{x},{x}>) is False')
    return True

def is_empty_relation(rel: R, v1, v2=None, *, quiet=True):
    if v2 is None:
        product = set(prod(v1, v1))
    else:
        product = set(prod(v1, v2))
    for x, y in product:
        if rel(x, y) and (x, y) in product:
            return False
    return True

def is_universal_relation(rel: R, v1, v2=None, *, quiet=True):
    if v2 is None:
        product = set(prod(v1, v1))
    else:
        product = set(prod(v1, v2))
    for x, y in product:
        if rel(x, y) and (x, y) not in product:
            return False
    return True


def is_identity_relation(relation: Relation, *, quiet=True):
    """
    >>> is_identity_relation(lambda a,b: a == b, {-1,0,1})
    True
    
    >>> is_identity_relation({(-1,-1), (0,0), (1,1)}, {-1,0,1})
    True
    
    >>> is_identity_relation({(-1,-1), (0,0), (1,1)}, {-1,0,1}, {-1,0,1,2})
    True
    """
    def _is_identity(_product:Prod):
        _leftsides = [_x for _x,_y in _product]
        _rightsides = [_y for _x,_y in _product]
        return _leftsides == _rightsides
    
    if is_product(relation):
        return _is_identity(relation)
            
    product = relate(relation, quiet=quiet)
    return _is_identity(product)
