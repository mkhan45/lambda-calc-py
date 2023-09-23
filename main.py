# lambda_term: x # variable
#            | \x → lambda_term # function
#            | lambda_term lambda_term # application

# variable: ("variable", str)
# function: ("function", variable, lambda_term)
# application: ("application", lambda_term, lambda_term)

def parse_term(s, bp=0):
    if s == "": raise Exception("unexpected end of input")

    def parse_function(s):
        assert s[0] in ("\\", "λ")
        v = s[1]
        assert s[2] in (".", "→")
        (e, rest) = parse_term(s[3:])
        return ("function", v, e), rest

    t, rest = None, None
    match s[0]:
        case "\\" | "λ": 
            t, rest = parse_function(s)
        case "(":
            (t, rest) = parse_term(s[1:])
            assert rest[0] == ")"
            rest = rest[1:]
        case ")":
            raise Exception("unexpected )")
        case _:
            t, rest = ("variable", s[0]), s[1:]
    
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

def eval_env(term, env):
    eval = eval_env
    match term:
        case ("variable", x): return env[x], env
        case ("function", x, t): return ("function", x, t), env
        case ("application", t1, t2):
            arg, env = eval(t2, env)
            f, env = eval(t1, env)
            match f:
                case ("function", x, t):
                    return eval(t, {**env, x: arg})
                case _:
                    raise Exception("not a function")

def eval_subst(term):
    def subst(t1, v, t2):
        match t1:
            case ("variable", x) if x == v: return t2
            case ("variable", x) if x != v: return t1
            case ("function", x, t) if x == v: return t1
            case ("function", x, t) if x != v: return ("function", x, subst(t, v, t2))
            case ("application", lhs, rhs): return ("application", subst(lhs, v, t2), subst(rhs, v, t2))

    eval = eval_subst
    match term:
        case ("variable", x): raise Exception(f"unbound variable {x}")
        case ("function", x, t): return ("function", x, t)
        case ("application", t1, t2):
            match eval(t1):
                case ("function", x, t): return eval(subst(t, x, t2))
                case _: raise Exception("not a function")

if __name__ == '__main__':
    parsed, rest = parse_term("(λx.λy.y) (λa.a) (λb.b)")
    print(f"{display(parsed)=}, {parsed=}, {rest=}")
    res1, _ = eval_env(parsed, {})
    res2 = eval_subst(parsed)
    print(display(res1))
    print(display(res2))

    true = "λx.λy.x"
    false = "λx.λy.y"
    and_ = "λp.λq.p q p"
    or_ = "λp.λq.p p q"
    not_ = "λp.p (λx.λy.y) (λx.λy.x)"
    xor = "λp.λq.p (not q) q"

    parsed, _ = parse_term(f"({and_}) ({true}) ({false})")
    print(f"{display(parsed)=}, {parsed=}, {rest=}")
    res1, _ = eval_env(parsed, {})
    res2 = eval_subst(parsed)
    print(display(res1))
    print(display(res2))
