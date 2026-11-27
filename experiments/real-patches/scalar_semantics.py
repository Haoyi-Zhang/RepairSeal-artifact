"""Closed, independent int32 execution for the published IntroClass scalar arms.

This interpreter does not use RepairSeal's receiver or its source bridge.  It
keeps uninitialized objects uninitialized and rejects unsupported syntax in the
whole function, including unreachable branches.  The only admitted external
operations are supplied-argument atoi, fixed-format scanf/printf, and abs.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pycparser import c_ast as C, c_parser

LO, HI = -(2**31), 2**31 - 1
TOKEN = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|(/\*.*?\*/|//[^\r\n]*)', re.S)


class Unsupported(ValueError):
    pass


class Undefined(Exception):
    def __init__(self, reason, node):
        self.reason = reason
        self.line = node.coord.line if node.coord else None


class Returned(Exception):
    def __init__(self, code):
        self.code = code


def require(ok, message):
    if not ok:
        raise Unsupported(message)


def strip_identity_macro(text):
    # This exact definition is present in the source release.  No general
    # preprocessor or regular-expression guess at macro semantics is used.
    matches = re.findall(r'^\s*#\s*define\s+ANGELIX_OUTPUT\s*\(\s*type\s*,\s*expr\s*,\s*id\s*\)\s+expr\s*$', text, re.M)
    directives = [l for l in text.splitlines() if l.lstrip().startswith('#')]
    for line in directives:
        require(bool(re.fullmatch(r'\s*#\s*(?:include\s*<[a-z]+\.h>|ifndef\s+ANGELIX_OUTPUT|endif|define\s+ANGELIX_OUTPUT\s*\(\s*type\s*,\s*expr\s*,\s*id\s*\)\s+expr)\s*', line)), 'unsupported preprocessing directive')
    text = re.sub(r'^\s*#[^\n]*', '', text, flags=re.M)
    while 'ANGELIX_OUTPUT' in text:
        require(bool(matches), 'identity macro has no verified definition')
        start = text.index('ANGELIX_OUTPUT')
        opening = text.find('(', start)
        require(opening >= 0, 'invalid macro invocation')
        depth, string, escaped, fields, field = 1, False, False, [], opening + 1
        for i in range(opening + 1, len(text)):
            ch = text[i]
            if string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    string = False
            elif ch == '"':
                string = True
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    fields.append(text[field:i])
                    require(len(fields) == 3 and fields[0].strip() == 'int', 'identity macro signature')
                    # The published macro body is the bare token sequence
                    # `expr`, not `(expr)`: preserve its exact precedence.
                    text = text[:start] + fields[1] + text[i+1:]
                    break
            elif ch == ',' and depth == 1:
                fields.append(text[field:i]); field = i + 1
        else:
            raise Unsupported('unterminated macro invocation')
    return text


@dataclass
class Program:
    tree: C.FuncDef
    input_arity: int


def parse(raw: bytes, arity: int) -> Program:
    require(len(raw) < 65536 and b'\0' not in raw and b'??' not in raw, 'source limit')
    text = raw.decode('utf-8')
    require('\\\n' not in text, 'line splicing')
    text = TOKEN.sub(lambda m: m[1] if m[1] else ''.join('\n' if c == '\n' else ' ' for c in m[2]), text)
    text = strip_identity_macro(text)
    try:
        tree = c_parser.CParser().parse(text)
    except Exception as exc:
        raise Unsupported('parse: ' + str(exc)) from exc
    require(len(tree.ext) == 1 and isinstance(tree.ext[0], C.FuncDef) and tree.ext[0].decl.name == 'main', 'one main function required')
    main = tree.ext[0]
    names = set()
    # Shifts are outside this profile; in particular, negative signed right
    # shift must never be mislabeled as undefined C behavior.
    allowed_binary = {'+', '-', '*', '/', '%', '<', '<=', '>', '>=', '==', '!=', '&&', '||', '&', '|', '^'}

    def expr(n):
        if isinstance(n, C.ID):
            require(n.name in names or n.name == 'argc', 'unknown identifier ' + n.name)
        elif isinstance(n, C.Constant):
            require(n.type == 'int' and bool(re.fullmatch(r'(?:0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*)', n.value)), 'integer literal required')
            value = int(n.value, 16 if n.value.lower().startswith('0x') else 8 if n.value.startswith('0') else 10)
            require(0 <= value <= HI, 'literal outside signed int32')
        elif isinstance(n, C.BinaryOp):
            require(n.op in allowed_binary, 'binary operator'); expr(n.left); expr(n.right)
        elif isinstance(n, C.UnaryOp):
            require(n.op in {'+', '-', '!', '~'}, 'side effect or unsupported unary expression'); expr(n.expr)
        elif isinstance(n, C.TernaryOp):
            expr(n.cond); expr(n.iftrue); expr(n.iffalse)
        elif isinstance(n, C.Cast):
            require(isinstance(n.to_type.type, C.TypeDecl) and n.to_type.type.type.names == ['int'], 'only int casts'); expr(n.expr)
        elif isinstance(n, C.FuncCall):
            require(isinstance(n.name, C.ID), 'indirect call')
            args = n.args.exprs if n.args else []
            if n.name.name == 'atoi':
                require(len(args) == 1 and isinstance(args[0], C.ArrayRef) and isinstance(args[0].name, C.ID) and args[0].name.name == 'argv' and isinstance(args[0].subscript, C.Constant), 'fixed argv input')
                require(1 <= int(args[0].subscript.value) <= arity, 'argv bounds')
            elif n.name.name == 'abs':
                require(len(args) == 1, 'abs arity'); expr(args[0])
            else:
                raise Unsupported('function in expression: ' + n.name.name)
        else:
            raise Unsupported('expression ' + type(n).__name__)

    def stmt(n):
        if n is None or isinstance(n, C.EmptyStatement):
            return
        if isinstance(n, C.Compound):
            for s in n.block_items or []:
                stmt(s)
        elif isinstance(n, C.Decl):
            require(isinstance(n.type, C.TypeDecl) and isinstance(n.type.type, C.IdentifierType) and n.type.type.names == ['int'] and not n.storage and not n.quals, 'only automatic signed int variables')
            require(n.name not in names and n.name not in {'argc', 'argv'}, 'shadowing or duplicate variable')
            names.add(n.name)
            if n.init:
                expr(n.init)
        elif isinstance(n, C.Assignment):
            require(isinstance(n.lvalue, C.ID) and n.lvalue.name in names and n.op in {'=', '+=', '-=', '*=', '/=', '%='}, 'assignment')
            expr(n.rvalue)
        elif isinstance(n, C.If):
            expr(n.cond); stmt(n.iftrue); stmt(n.iffalse)
        elif isinstance(n, C.Return):
            expr(n.expr)
        elif isinstance(n, C.FuncCall):
            require(isinstance(n.name, C.ID), 'indirect statement call')
            args = n.args.exprs if n.args else []
            require(args and isinstance(args[0], C.Constant) and args[0].type == 'string', 'literal format required')
            fmt = ast.literal_eval(args[0].value)
            require(fmt.isascii() and '\0' not in fmt and not re.search(r'%(?!d)', fmt), 'only percent-d conversions')
            require(fmt.count('%d') == len(args)-1, 'format arity')
            if n.name.name == 'printf':
                for a in args[1:]: expr(a)
            elif n.name.name == 'scanf':
                require(re.fullmatch(r'\s*(?:%d\s*)+', fmt), 'scanf format')
                for a in args[1:]:
                    require(isinstance(a, C.UnaryOp) and a.op == '&' and isinstance(a.expr, C.ID) and a.expr.name in names, 'scanf target')
            else:
                raise Unsupported('statement call ' + n.name.name)
        else:
            raise Unsupported('statement ' + type(n).__name__)
    stmt(main.body)
    return Program(main, arity)


def evaluate(program: Program, values) -> dict:
    require(len(values) == program.input_arity and all(type(v) is int and LO <= v <= HI for v in values), 'input contract')
    env = {'argc': len(values)+1}; output = []; numeric = []; consumed = 0; steps = 0
    def checked(v, n):
        if not LO <= v <= HI:
            raise Undefined('signed-overflow', n)
        return v
    def read(name, n):
        if name not in env:
            raise Undefined('uninitialized-read:' + name, n)
        return env[name]
    def binary(op, a, b, n):
        if op in {'/', '%'}:
            if b == 0: raise Undefined('division-by-zero', n)
            if a == LO and b == -1: raise Undefined('signed-division-overflow', n)
            q = (abs(a)//abs(b)) * (-1 if (a < 0) != (b < 0) else 1)
            return q if op == '/' else a-q*b
        if op in {'<<', '>>'}:
            if not 0 <= b < 32: raise Undefined('shift-count', n)
            if a < 0: raise Undefined('negative-shift-operand-outside-profile', n)
            return checked(a << b, n) if op == '<<' else a >> b
        if op == '+': return checked(a+b,n)
        if op == '-': return checked(a-b,n)
        if op == '*': return checked(a*b,n)
        if op == '<': return int(a<b)
        if op == '<=': return int(a<=b)
        if op == '>': return int(a>b)
        if op == '>=': return int(a>=b)
        if op == '==': return int(a==b)
        if op == '!=': return int(a!=b)
        if op == '&': return a&b
        if op == '|': return a|b
        if op == '^': return a^b
        raise Unsupported(op)
    def expr(n):
        nonlocal steps
        steps += 1
        if isinstance(n,C.ID): return read(n.name,n)
        if isinstance(n,C.Constant): return int(n.value,16 if n.value.lower().startswith('0x') else 8 if n.value.startswith('0') else 10)
        if isinstance(n,C.Cast): return expr(n.expr)
        if isinstance(n,C.TernaryOp): return expr(n.iftrue if expr(n.cond) else n.iffalse)
        if isinstance(n,C.UnaryOp):
            v=expr(n.expr)
            if n.op=='+':return v
            if n.op=='-':return checked(-v,n)
            if n.op=='!':return int(not v)
            if n.op=='~':return ~v
        if isinstance(n,C.BinaryOp):
            a=expr(n.left)
            if n.op=='&&': return int(bool(a) and bool(expr(n.right)))
            if n.op=='||': return int(bool(a) or bool(expr(n.right)))
            return binary(n.op,a,expr(n.right),n)
        if isinstance(n,C.FuncCall):
            if n.name.name=='atoi': return values[int(n.args.exprs[0].subscript.value)-1]
            return checked(abs(expr(n.args.exprs[0])),n)
        raise Unsupported(type(n).__name__)
    def stmt(n):
        nonlocal consumed,steps
        steps+=1
        if n is None or isinstance(n,C.EmptyStatement):return
        if isinstance(n,C.Compound):
            for s in n.block_items or []:stmt(s)
        elif isinstance(n,C.Decl):
            env.pop(n.name,None)
            if n.init is not None: env[n.name]=expr(n.init)
        elif isinstance(n,C.Assignment):
            v=expr(n.rvalue)
            if n.op!='=':v=binary(n.op[:-1],read(n.lvalue.name,n),v,n)
            env[n.lvalue.name]=v
        elif isinstance(n,C.If):stmt(n.iftrue if expr(n.cond) else n.iffalse)
        elif isinstance(n,C.Return):raise Returned(expr(n.expr))
        elif isinstance(n,C.FuncCall):
            args=n.args.exprs;fmt=ast.literal_eval(args[0].value)
            if n.name.name=='scanf':
                for a in args[1:]:
                    if consumed>=len(values):raise Undefined('missing-input',n)
                    env[a.expr.name]=values[consumed];consumed+=1
            else:
                nums=[expr(a) for a in args[1:]]
                output.append(fmt % tuple(nums) if nums else fmt);numeric.extend(nums)
    try:
        try:stmt(program.tree.body)
        except Returned as r:code=r.code
        else:code=0
        return {'defined':True,'stdout':''.join(output),'numeric_values':numeric,'returncode':code,'undefined_reason':None,'undefined_line':None,'steps':steps}
    except Undefined as e:
        return {'defined':False,'stdout':None,'numeric_values':None,'returncode':None,'undefined_reason':e.reason,'undefined_line':e.line,'steps':steps}
