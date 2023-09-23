# lambda_term: x # variable
#            | \x → lambda_term # function
#            | lambda_term lambda_term # application

# variable: ("variable", str)
# function: ("function", variable, lambda_term)
# application: ("application", lambda_term, lambda_term)

def eval(term, env):
    match term:
        case ("variable", x): return env[x]
        case ("function", x, t): return term
        case ("application", t1, t2): return apply(eval(t1, env), eval(t2, env), env)

def apply(f, v, env):
    match f:
        case ("function", x, t): return eval(t, {**env, x: v})
        case _: raise Exception("not a function")

def parse_term(s):
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
    
    if rest == "": return t, rest
    match rest[0]:
        case " ":
            rest = rest[1:]
            (t2, rest) = parse_term(rest)
            return ("application", t, t2), rest
        case _: return t, rest

def display(term):
    match term:
        case ("variable", x): return x
        case ("function", x, t): return f"λ{x}. {display(t)}"
        case ("application", t1, t2): return f"({display(t1)}) ({display(t2)})"

if __name__ == '__main__':
    # term = ("application", ("function", "x", ("variable", "x")), ("variable", "y"))
    # print(eval(term, {'y': 'y'}))
    parsed, rest = parse_term("(λx.x) (λy.y)")
    print(f"{display(parsed)=}, {parsed=}, {rest=}")
    print(display(eval(parsed, {})))
