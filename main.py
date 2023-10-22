# lambda_term: x # variable
#            | \x → lambda_term # function
#            | lambda_term lambda_term # application

#            # extensions, not actually part of the lambda calculus
#            | n # number literal
#            | + lambda_term lambda_term # addition

# variable: ("variable", str)
# function: ("function", variable, lambda_term)
# application: ("application", lambda_term, lambda_term)

# extensions, not part of the base lambda calculus
# number: ("number", int)
# addition: ("addition", lambda_term, lambda_term)

# dumb pratt parser
# Can't use spaces except for function application
# Make sure to parenthesize everything
def parse_term(s, bp=0):
    if s == "": raise Exception("unexpected end of input")

    t, rest = None, None
    # recursion for right associativity
    # we accumulate the term into t, and leave the remainder of the string in rest
    match s[0]:
        case "\\" | "λ": 
            v = s[1]
            assert s[2] in (".", "→")
            (e, rest) = parse_term(s[3:])
            t = ("function", v, e)
        case "(":
            (t, rest) = parse_term(s[1:])
            assert rest[0] == ")"
            rest = rest[1:]
        case ")":
            raise Exception("unexpected )")
        case n if n.isdigit():
            t, rest = ("number", int(n)), s[1:]
        case "+":
            rest = s[1:]
            assert rest[0] == " "
            (t1, rest) = parse_term(rest[1:], 1)
            assert rest[0] == " "
            (t2, rest) = parse_term(rest[1:], 1)
            t = ("addition", t1, t2)
            return t, rest
        case _:
            t, rest = ("variable", s[0]), s[1:]
    
    # iteration for left associativity
    while rest != "":
        if rest[0] == " " and bp == 0:
            rest = rest[1:]
            (t2, rest) = parse_term(rest, 1)
            t = ("application", t, t2)
        else:
            break

    return t, rest

def display(term):
    match term:
        case ("variable", x): return x
        case ("function", x, t): return f"λ{x}.{display(t)}"
        case ("application", t1, t2): return f"({display(t1)}) ({display(t2)})"
        case ("number", n): return str(n)
        case ("addition", t1, t2): return f"+ ({display(t1)}) ({display(t2)})"

#        (f x, "x", 15) # ("application", f, ("variable", x))
#         f 15
def subst(t1, v, t2):
    match t1:
        case ("variable", x) if x == v: return t2 # subst
        case ("variable", x) if x != v: return t1 # leaf
        case ("number", n): return t1 # leaf
        case ("function", x, t) if x == v: return t1 # shadowing
        case ("function", x, t) if x != v: return ("function", x, subst(t, v, t2)) # recurse
        case ("application", lhs, rhs): return ("application", subst(lhs, v, t2), subst(rhs, v, t2)) # recurse
        case ("addition", lhs, rhs): return ("addition", subst(lhs, v, t2), subst(rhs, v, t2)) # recurse

# (λx.x+5) (5 + 10)
# ("application", ("function", "x", ("plus", "x", 5)) ("plus", 5, 10))
# → ("plus", ("plus", 5, 10), 5)
def eval_subst(term):
    eval = eval_subst
    match term:
        case ("variable", x): raise Exception(f"unbound variable {x}") # free variable, wasn't substed
        case ("function", x, t): return ("function", x, t) # irreducible
        case ("application", t1, t2): # all three rules at once here
            match eval(t1): # first eval lhs
                case ("function", x, t): return eval(subst(t, x, eval(t2))) # eval rhs, then beta reduction
                case _: raise Exception("not a function")
        # extensions, not part of the base lambda calculus
        case ("number", n): return term
        case ("addition", t1, t2):
            match (eval(t1), eval(t2)):
                case (("number", n1), ("number", n2)): return ("number", n1 + n2)
                case _: raise Exception("not a number")

# beta reduces all inner terms
def simplify(term):
    match term:
        case ("variable" | "number", _): return term
        case ("function", x, t): return ("function", x, simplify(t))
        case ("application", t1, t2):
            match (simplify(t1), simplify(t2)):
                case (("function", x, t), t2): return simplify(subst(t, x, t2))
                case (t1, t2): return ("application", t1, t2)
        # extensions, not part of the base lambda calculus
        case ("addition", t1, t2):
            match (simplify(t1), simplify(t2)):
                case (("number", n1), ("number", n2)): return ("number", n1 + n2)
                case (t1, t2): return ("addition", t1, t2)

def eval_subst_str(str, do_simplify=True):
    parsed, _ = parse_term(str)
    res = eval_subst(parsed)

    if do_simplify: return display(simplify(res))
    else: return display(res)

if __name__ == '__main__':
    # parsed, rest = parse_term("(λx.λy.y) (λa.a) (λb.b)")
    # print(f"{display(parsed)=}, {parsed=}, {rest=}")
    # res1, _ = eval_env(parsed, {})
    # res2 = eval_subst(parsed)
    # print(display(res1))
    # print(display(res2))

    # (2 + 3) → 5

    # ((λx.λy.x+y) 5) 10
    # (λy.5+y) 10
    # 5+10

    # true = "λx.λy.x"
    # false = "λx.λy.y"
    # _and = "λp.λq.p q p"

    # print(eval_subst_str(f"(λp.λq.p q p) (λx.λy.x) (λx.λy.x)"))

    # parsed, _ = parse_term("(λx.x) (λy.y)")
    # (lambda x: x)(lambda y: y)
    # (x => x)(y => y)
    # res = eval_subst(parsed)
    # print(parsed)
    # print(display(res))

    # parsed, _ = parse_term("(λx.x) (+ 5 10)")
    # print(parsed)

    # true = "λx.λy.x"
    # false = "λx.λy.y"
    # and_ = "λp.λq.p q p"
    # or_ = "λp.λq.p p q"
    # not_ = "λp.p (λx.λy.y) (λx.λy.x)"
    # xor = "λp.λq.p (not q) q"

    # parsed, _ = parse_term(f"({and_}) ({true}) ({false})")
    # print(f"{display(parsed)=}, {parsed=}, {rest=}")
    # res1, _ = eval_env(parsed, {})
    # res2 = eval_subst(parsed)
    # print(display(res1))
    # print(display(res2))

    print(eval_subst_str("(λx.+ x 5) 3"))

    zero = "λf.λx.x"
    # # zero = "λf.λx.x"
    succ = "λn.λf.λx.f (n f x)"
    one = f"({succ}) ({zero})"
    # print(one)
    plus = "(λm.λn.((m (λn.(λf.(λy.f ((n f) y))))) n))"
    mul = "(λm.λn.λf.m (n f))"
    two = f"({plus}) ({one}) ({one})"
    print(eval_subst_str(f"({mul}) ({two}) ({two})"))

    # parsed, _ = parse_term(one)
    # print(f"{display(parsed)=}, {parsed=}")
    # # res1, _ = eval_env(parsed, {})
    # res2 = eval_subst(parsed)
    # # print(display(res1))
    # print(display(res2))

    # # print(f"{plus=}")
    # # print(f"{one=}")
    # # print(f"{two=}")
    # print(eval_subst_str(two))
    # print(eval_subst_str(two, do_simplify=False))

    real_succ = "λn.(+ n 1)"
    # print(eval_subst_str(f"({real_succ}) 0"))
    # church_to_int = f"λn.n ({real_succ}) 0"
    # print(eval_subst_str(f"({church_to_int}) ({sixteen})"))

    church_to_int = f"λn.n ({real_succ}) 0"
    four = f"({plus}) ({two}) ({two})"
    sixteen = f"({mul}) ({four}) ({four})"
    # print(f"{sixteen=}")
    print(eval_subst_str(f"({church_to_int}) ({sixteen})"))
    
    # # parsed, rest = parse_term("+ 1 1")
    # # res = eval_subst(parsed)
    # # print(f"{display(parsed)=}, {parsed=}, {rest=}")
    # # print(display(res))

    # # parsed, _ = parse_term(f"{one} (λx.+ x 1) 0")
    # # res = eval_subst(parsed)
    # # print(display(res))

    # print(eval_subst_str("(λx.x x) (λy.y y)"))
    # (λx.x x) (λy.y y)
    # (λy.y y) (λy.y y)
    #     |
    #   (λy.y y)
