# Minimal Lambda Calculus Interpreter

Super simple call-by-value lambda calculus interpreter ! Made for a Purdue Hackers session !
Read the code to help yourself sleep at night !

<https://groups.seas.harvard.edu/courses/cs152/2010sp/lectures/lec08.pdf>

```py
def subst(t1, v, t2):
    match t1:
        case ("variable", x) if x == v: return t2
        case ("variable", x) if x != v: return t1
        case ("function", x, t) if x == v: return t1
        case ("function", x, t) if x != v: return ("function", x, subst(t, v, t2))
        case ("application", lhs, rhs): return ("application", subst(lhs, v, t2), subst(rhs, v, t2))

def eval_subst(term):
    eval = eval_subst
    match term:
        case ("variable", x): raise Exception(f"unbound variable {x}")
        case ("function", x, t): return ("function", x, t)
        case ("application", t1, t2):
            match eval(t1):
                case ("function", x, t): return eval(subst(t, x, eval(t2)))
                case _: raise Exception("not a function")
```
