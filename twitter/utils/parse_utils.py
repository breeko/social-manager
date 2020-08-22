""" parse_utils.py """
import math
import operator
import re
from typing import Callable

from pyparsing import (CaselessLiteral, Combine, Forward, Group, Literal,
                       Optional, Word, ZeroOrMore, alphas, nums, oneOf)
from tweepy.models import User

comps_f = {
  "=": lambda a, b: a == b,
  ">": lambda a, b: a > b,
  ">=": lambda a, b: a >= b,
  "<": lambda a, b: a < b,
  "<=": lambda a, b: a <= b
}

def valid_expr(user: User, expr: str) -> bool:
  """ Returns whether an expression is valid or not """
  try:
    _ = apply_expr(user, expr)
    return True
  except:
    return False

def apply_expr(user: User, expr: str) -> str:
  """ Parses an expression and applies it to a user. Throws ValueError if invalid """
  tokens = expr.split()
  subed_tokens = []
  for token in tokens:
    if hasattr(user, token):
      sub = user.__getattribute__(token)
      subed_tokens.append(str(sub))
    else:
      subed_tokens.append(token)
  subed_expr = " ".join(subed_tokens)

  comps = re.findall(r"=|>=|<=|>|<", subed_expr)
  if len(comps) != 1:
    raise ValueError("one comp required")
  comp = comps[0]
  left, right = subed_expr.split(comp)
  comp_f = comps_f.get(comp)
  if comp_f is None:
    raise ValueError("invalid comp")

  parser = NumericStringParser()
  left_val = parser.eval(left)
  right_val = parser.eval(right)
  return comp_f(left_val, right_val)

def build_expr(expr: str) -> Callable[['User'], bool]:
  """ Builds an expression that takes a User and returns a boolean """
  def app(u: User):
    try:
      return apply_expr(u, expr)
    except:
      return True
  return app

class NumericStringParser(object):
  """ Most of this code comes from the fourFn.py pyparsing example
    https://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string
  """

  def pushFirst(self, _strg, _loc, toks):
    self.exprStack.append(toks[0])

  def pushUMinus(self, _strg, _loc, toks):
    if toks and toks[0] == '-':
      self.exprStack.append('unary -')

  def __init__(self):
    """
      expop   :: '^'
      multop  :: '*' | '/'
      addop   :: '+' | '-'
      integer :: ['+' | '-'] '0'..'9'+
      atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
      factor  :: atom [ expop factor ]*
      term    :: factor [ multop factor ]*
      expr    :: term [ addop term ]*
    """
    point = Literal(".")
    e = CaselessLiteral("E")
    fnumber = Combine(Word("+-" + nums, nums) +
                      Optional(point + Optional(Word(nums))) +
                      Optional(e + Word("+-" + nums, nums)))
    ident = Word(alphas, alphas + nums + "_$")
    plus = Literal("+")
    minus = Literal("-")
    mult = Literal("*")
    div = Literal("/")
    lpar = Literal("(").suppress()
    rpar = Literal(")").suppress()
    addop = plus | minus
    multop = mult | div
    expop = Literal("^")
    pi = CaselessLiteral("PI")
    expr = Forward()
    atom = ((Optional(oneOf("- +")) +
      (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
    | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
    ).setParseAction(self.pushUMinus)
    # by defining exponentiation as "atom [ ^ factor ]..." instead of
    # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
    # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
    factor = Forward()
    factor << atom + ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
    term = factor + ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
    expr << term + ZeroOrMore((addop + term).setParseAction(self.pushFirst))
    # addop_term = ( addop + term ).setParseAction( self.pushFirst )
    # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
    # expr <<  general_term
    self.bnf = expr
    # map operator symbols to corresponding arithmetic operations
    epsilon = 1e-12
    self.opn = {"+": operator.add,
                "-": operator.sub,
                "*": operator.mul,
                "/": operator.truediv,
                "^": operator.pow}
    self.fn = {"sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "abs": abs,
                "trunc": lambda a: int(a),
                "round": round,
                "sgn": lambda a: abs(a) > epsilon or 0}

  def evaluateStack(self, s):
    op = s.pop()
    if op == 'unary -':
      return -self.evaluateStack(s)
    if op in "+-*/^":
      op2 = self.evaluateStack(s)
      op1 = self.evaluateStack(s)
      return self.opn[op](op1, op2)
    elif op == "PI":
      return math.pi  # 3.1415926535
    elif op == "E":
      return math.e  # 2.718281828
    elif op in self.fn:
      return self.fn[op](self.evaluateStack(s))
    elif op[0].isalpha():
      return 0
    else:
      return float(op)

  def eval(self, num_string, parseAll=True):
    self.exprStack = []
    results = self.bnf.parseString(num_string, parseAll)
    val = self.evaluateStack(self.exprStack[:])
    return val
