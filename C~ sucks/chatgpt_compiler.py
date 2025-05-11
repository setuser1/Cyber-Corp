#!/usr/bin/env python3
import sys
import os
import llvmlite.ir as ir
import llvmlite.binding as llvm
import codecs
import shlex
import re

# AST node classes
class Function:
    def __init__(self, ret_type, name, params, body):
        self.ret_type = ret_type
        self.name = name
        self.params = params
        self.body = body

class IfStmt:
    def __init__(self, cond, body, elifs=None, else_body=None):
        self.cond = cond
        self.body = body
        self.elifs = elifs or []
        self.else_body = else_body

class ElifStmt:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class ElseStmt:
    def __init__(self, body):
        self.body = body

class WhileStmt:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class ReturnStmt:
    def __init__(self, expr):
        self.expr = expr  # None for void

def unescape_string(s):
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return codecs.decode(s, 'unicode_escape')

# Parser (brace-based)
def parse_block(lines, i):
    stmts = []
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line == '}':
            return stmts, i+1
        if line.endswith('{'):
            hdr = line[:-1].strip()
            if hdr.startswith('if '):
                cond = hdr[3:].strip()
                body, i = parse_block(lines, i+1)
                elifs = []
                else_body = None
                # Parse xif (elif) and else blocks
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('xif '):
                        xif_cond = next_line[4:].trip()
                        if xif_cond.endswith('{'):
                            xif_cond = xif_cond[:-1].strip()
                        xif_body, i = parse_block(lines, i+1)
                        elifs.append(ElifStmt(xif_cond, xif_body))
                    elif next_line.startswith('else'):
                        i += 1  # skip 'else {'
                        else_body, i = parse_block(lines, i)
                        break
                    else:
                        break
                stmts.append(IfStmt(cond, body, elifs, else_body))
                continue
            if hdr.startswith('while '):
                cond = hdr[6:].strip()
                body, i = parse_block(lines, i+1)
                stmts.append(WhileStmt(cond, body))
                continue
        if line.startswith('return'):
            expr = line[6:].strip() or None
            stmts.append(ReturnStmt(expr))
            i += 1; continue
        stmts.append(line)
        i += 1
    return stmts, i

def parse(lines):
    functions = []
    i = 0
    valid_types = ('int', 'float', 'double', 'void', 'expr', 'char')
    while i < len(lines):
        raw = lines[i].strip()
        if raw.startswith('#include'):
            i += 1; continue
        # Only accept known types
        if any(raw.startswith(t + ' ') for t in valid_types) and raw.endswith('{'):
            hdr = raw[:-1].strip()
            parts = hdr.split(' ',1)
            ret_type, rest = parts
            if ret_type == 'expr':
                ret_type = 'void'
            elif ret_type not in ('int', 'float', 'double', 'void', 'char'):
                raise SyntaxError(f"Unknown return type '{ret_type}' in function definition: {hdr}")
            name = rest[:rest.find('(')].strip()
            params_str = rest[rest.find('(')+1:rest.find(')')].strip()
            params = [p.strip().split()[-1] for p in params_str.split(',') if p.strip()] if params_str else []
            body, i = parse_block(lines, i+1)
            functions.append(Function(ret_type, name, params, body))
            continue
        elif raw.endswith('{'):
            raise SyntaxError(f"Missing or unknown return type in function definition: {raw}")
        i += 1
    return functions

def get_llvm_type(typ):
    if typ == 'int':
        return ir.IntType(32)
    elif typ == 'float':
        return ir.FloatType()
    elif typ == 'double':
        return ir.DoubleType()
    elif typ == 'char':
        return ir.IntType(8)
    elif typ == 'void':
        return ir.VoidType()
    else:
        raise ValueError(f"Unknown type: {typ}")

def build_module(functions):
    module = ir.Module(name='module')
    module.triple = llvm.get_default_triple()
    # declare external functions
    f_printf = ir.Function(module, ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True), name='printf')
    f_scanf  = ir.Function(module, ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True), name='scanf')
    # Add strcmp for string comparison
    f_strcmp = ir.Function(module, ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8)), ir.PointerType(ir.IntType(8))]), name='strcmp')
    # constants
    fmt_int  = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), 4), name='fmt_int')
    fmt_int.global_constant = True
    fmt_int.initializer = ir.Constant(fmt_int.type.pointee, bytearray(b"%d\n\0"))
    fmt_in = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), 3), name='fmt_in')
    fmt_in.global_constant = True
    fmt_in.initializer = ir.Constant(fmt_in.type.pointee, bytearray(b"%d\0"))
    fmt_str = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), 3), name='fmt_str')
    fmt_str.global_constant = True
    fmt_str.initializer = ir.Constant(fmt_str.type.pointee, bytearray(b"%s\0"))

    # --- Predeclare all functions for forward references ---
    llvm_fns = {}
    for fn in functions:
        ftype = get_llvm_type(fn.ret_type)
        arg_types = [ir.IntType(32)] * len(fn.params)
        func_ty = ir.FunctionType(ftype, arg_types)
        llvm_fns[fn.name] = ir.Function(module, func_ty, name=fn.name)

    for fn in functions:
        llvm_fn = llvm_fns[fn.name]
        block = llvm_fn.append_basic_block('entry')
        builder = ir.IRBuilder(block)
        locals = {}
        arrays = {}
        array_types = {}
        array_sizes = {}

        # First pass: allocate all locals and arrays
        for stmt in fn.body:
            if isinstance(stmt, str):
                stmt_stripped = stmt.lstrip()
                # Support all types
                if stmt_stripped.startswith('int ') or stmt_stripped.startswith('char ') or stmt_stripped.startswith('float ') or stmt_stripped.startswith('double '):
                    decl = stmt_stripped[stmt_stripped.find(' ')+1:].strip().rstrip(';:')
                    if '[' in decl and decl.endswith(']'):
                        var = decl[:decl.find('[')].strip()
                        size = decl[decl.find('[')+1:-1].strip()
                        size_val = int(size) if size.isdigit() else 10
                        if stmt_stripped.startswith('char '):
                            arr_ptr = builder.alloca(ir.IntType(8), ir.Constant(ir.IntType(32), size_val), name=var)
                            arrays[var] = arr_ptr
                            array_types[var] = 'char'
                            array_sizes[var] = size_val
                        elif stmt_stripped.startswith('float '):
                            arr_ptr = builder.alloca(ir.FloatType(), ir.Constant(ir.IntType(32), size_val), name=var)
                            arrays[var] = arr_ptr
                            array_types[var] = 'float'
                            array_sizes[var] = size_val
                        elif stmt_stripped.startswith('double '):
                            arr_ptr = builder.alloca(ir.DoubleType(), ir.Constant(ir.IntType(32), size_val), name=var)
                            arrays[var] = arr_ptr
                            array_types[var] = 'double'
                            array_sizes[var] = size_val
                        else:
                            arr_ptr = builder.alloca(ir.IntType(32), ir.Constant(ir.IntType(32), size_val), name=var)
                            arrays[var] = arr_ptr
                            array_types[var] = 'int'
                            array_sizes[var] = size_val
                    else:
                        var = decl.strip()
                        if stmt_stripped.startswith('char '):
                            locals[var] = builder.alloca(ir.IntType(8), name=var)
                        elif stmt_stripped.startswith('float '):
                            locals[var] = builder.alloca(ir.FloatType(), name=var)
                        elif stmt_stripped.startswith('double '):
                            locals[var] = builder.alloca(ir.DoubleType(), name=var)
                        else:
                            locals[var] = builder.alloca(ir.IntType(32), name=var)

        # Allocate and store function parameters
        for idx, param in enumerate(fn.params):
            param_name = param.strip()
            ptr = builder.alloca(ir.IntType(32), name=param_name)
            builder.store(llvm_fn.args[idx], ptr)
            locals[param_name] = ptr

        fmt_str_cache = {}

        def gen_cond(cond):
            cond = cond.strip()
            # Handle string/char[] == "literal" or != "literal"
            for op in ['==', '!=']:
                if op in cond:
                    lhs, rhs = cond.split(op, 1)
                    lhs = lhs.strip().lstrip('(').rstrip(')')
                    rhs = rhs.strip().lstrip('(').rstrip(')')
                    # Detect char array vs string literal
                    if lhs in arrays and array_types[lhs] == 'char' and (
                        (rhs.startswith('"') and rhs.endswith('"')) or (rhs.startswith("'") and rhs.endswith("'"))
                    ):
                        arr_ptr = arrays[lhs]
                        string_val = unescape_string(rhs)
                        arr_ty = ir.ArrayType(ir.IntType(8), len(string_val)+1)
                        str_const = ir.GlobalVariable(module, arr_ty, name=f"str_{abs(hash(string_val))}")
                        str_const.global_constant = True
                        str_const.initializer = ir.Constant(arr_ty, bytearray(string_val.encode('utf8')+b'\0'))
                        str_ptr = builder.gep(str_const, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                        cmp_result = builder.call(f_strcmp, [arr_ptr, str_ptr], name="strcmp_call")
                        if op == '==':
                            return builder.icmp_signed('==', cmp_result, ir.Constant(ir.IntType(32), 0))
                        else:
                            return builder.icmp_signed('!=', cmp_result, ir.Constant(ir.IntType(32), 0))
                    # Detect string literal vs char array (reverse order)
                    if rhs in arrays and array_types[rhs] == 'char' and (
                        (lhs.startswith('"') and lhs.endswith('"')) or (lhs.startswith("'") and lhs.endswith("'"))
                    ):
                        arr_ptr = arrays[rhs]
                        string_val = unescape_string(lhs)
                        arr_ty = ir.ArrayType(ir.IntType(8), len(string_val)+1)
                        str_const = ir.GlobalVariable(module, arr_ty, name=f"str_{abs(hash(string_val))}")
                        str_const.global_constant = True
                        str_const.initializer = ir.Constant(arr_ty, bytearray(string_val.encode('utf8')+b'\0'))
                        str_ptr = builder.gep(str_const, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                        cmp_result = builder.call(f_strcmp, [arr_ptr, str_ptr], name="strcmp_call")
                        if op == '==':
                            return builder.icmp_signed('==', cmp_result, ir.Constant(ir.IntType(32), 0))
                        else:
                            return builder.icmp_signed('!=', cmp_result, ir.Constant(ir.IntType(32), 0))
                    # Fallback to numeric/variable comparison
                    l = builder.load(locals[lhs], name=f'load_{lhs}')
                    r = ir.Constant(ir.IntType(32), int(rhs)) if rhs.isdigit() else builder.load(locals[rhs], name=f'load_{rhs}')
                    cmp_map = {'==':'==', '!=':'!='}
                    return builder.icmp_signed(cmp_map[op], l, r)
            # Support <, >, <=, >= as before
            for op in ['<=', '>=', '<', '>']:
                if op in cond:
                    lhs, rhs = cond.split(op, 1)
                    lhs = lhs.strip().lstrip('(').rstrip(')')
                    rhs = rhs.strip().lstrip('(').rstrip(')')
                    l = builder.load(locals[lhs], name=f'load_{lhs}')
                    r = ir.Constant(ir.IntType(32), int(rhs)) if rhs.isdigit() else builder.load(locals[rhs], name=f'load_{rhs}')
                    cmp_map = {'<':'<', '>':'>', '<=':'<=', '>=':'>='}
                    return builder.icmp_signed(cmp_map[op], l, r)
            raise ValueError(f"Unsupported condition: {cond}")

        def emit(stmt):
            if isinstance(stmt, str):
                stmt = stmt.rstrip(':;').strip()
                if stmt.startswith('scanf'):
                    var = stmt[stmt.find('(')+1:stmt.rfind(')')].split(',')[1].strip().lstrip('&')
                    if var in arrays and array_types[var] == 'char':
                        # Use "%s" format string and cast array pointer to i8*
                        ptr = builder.gep(fmt_str, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                        char_ptr = builder.bitcast(arrays[var], ir.PointerType(ir.IntType(8)))
                        builder.call(f_scanf, [ptr, char_ptr])
                    else:
                        # Use "%d" format string and i32* pointer
                        ptr = builder.gep(fmt_in, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                        builder.call(f_scanf, [ptr, locals[var]])
                elif stmt.startswith('printf'):
                    argstr = stmt[stmt.find('(')+1:stmt.rfind(')')]
                    lexer = shlex.shlex(argstr, posix=True)
                    lexer.whitespace_split = True
                    lexer.whitespace = ','
                    args = list(lexer)
                    args = [a.strip() for a in args if a]

                    if not args:
                        raise ValueError("printf requires at least a format string")
                    fmt_literal = args[0]
                    # Accept both quoted and unquoted strings
                    if (fmt_literal.startswith('"') and fmt_literal.endswith('"')) or (fmt_literal.startswith("'") and fmt_literal.endswith("'")):
                        fmt_user_str = unescape_string(fmt_literal)
                    else:
                        fmt_user_str = unescape_string('"' + fmt_literal + '"')

                    # Find all {var} in the format string
                    var_matches = list(re.finditer(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", fmt_user_str))
                    values = []
                    fmt_out = ""
                    last_idx = 0
                    for match in var_matches:
                        varname = match.group(1)
                        # Append text before the {var}
                        fmt_out += fmt_user_str[last_idx:match.start()]
                        # Substitute with %d or %s
                        if varname in arrays and array_types[varname] == 'char':
                            fmt_out += "%s"
                            values.append(builder.bitcast(arrays[varname], ir.PointerType(ir.IntType(8))))
                        elif varname in locals:
                            fmt_out += "%d"
                            values.append(builder.load(locals[varname], name=f'load_{varname}'))
                        else:
                            raise ValueError(f"Unknown variable in printf f-string: {varname}")
                        last_idx = match.end()
                    # Append the rest of the string
                    fmt_out += fmt_user_str[last_idx:]
                    fmt_out += "\0"

                    # Build or reuse the format string global
                    fmt_hash = abs(hash(fmt_out))
                    if fmt_hash not in fmt_str_cache:
                        arr_ty = ir.ArrayType(ir.IntType(8), len(fmt_out.encode('utf8')))
                        str_const = ir.GlobalVariable(module, arr_ty, name=f"fmt_str_{fmt_hash}")
                        str_const.global_constant = True
                        str_const.initializer = ir.Constant(arr_ty, bytearray(fmt_out.encode('utf8')))
                        fmt_str_cache[fmt_hash] = str_const
                    else:
                        str_const = fmt_str_cache[fmt_hash]
                    ptr = builder.gep(str_const, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
                    builder.call(f_printf, [ptr] + values)
                elif '=' in stmt:
                    lhs, expr = stmt.split('=', 1)
                    lhs = lhs.strip()
                    expr = expr.strip().rstrip(';:')
                    # String assignment to char array: arr = "hello" or arr = 'hello'
                    if lhs in arrays and array_types[lhs] == 'char' and (
                        (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'"))
                    ):
                        arr_ptr = arrays[lhs]
                        string_val = unescape_string(expr)
                        for idx, ch in enumerate(string_val):
                            if idx >= array_sizes[lhs]:
                                break
                            elem_ptr = builder.gep(arr_ptr, [ir.Constant(ir.IntType(32), idx)])
                            builder.store(ir.Constant(ir.IntType(8), ord(ch)), elem_ptr)
                        # Null-terminate if space
                        if len(string_val) < array_sizes[lhs]:
                            elem_ptr = builder.gep(arr_ptr, [ir.Constant(ir.IntType(32), len(string_val))])
                            builder.store(ir.Constant(ir.IntType(8), 0), elem_ptr)
                    # Char assignment: arr[0] = 'h'
                    elif '[' in lhs and lhs.endswith(']') and (
                        (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'"))
                    ):
                        arrname = lhs[:lhs.find('[')].strip()
                        idx = lhs[lhs.find('[')+1:-1].strip()
                        if arrname not in arrays or array_types[arrname] != 'char':
                            raise ValueError(f"Unknown char array '{arrname}'")
                        arr_ptr = arrays[arrname]
                        idx_val = ir.Constant(ir.IntType(32), int(idx)) if idx.isdigit() else builder.load(locals[idx], name=f'load_{idx}')
                        elem_ptr = builder.gep(arr_ptr, [idx_val])
                        builder.store(ir.Constant(ir.IntType(8), ord(unescape_string(expr))), elem_ptr)
                    # Array assignment: arr[0] = x
                    elif '[' in lhs and lhs.endswith(']'):
                        arrname = lhs[:lhs.find('[')].strip()
                        idx = lhs[lhs.find('[')+1:-1].strip()
                        if arrname not in arrays:
                            raise ValueError(f"Unknown array '{arrname}'")
                        arr_ptr = arrays[arrname]
                        idx_val = ir.Constant(ir.IntType(32), int(idx)) if idx.isdigit() else builder.load(locals[idx], name=f'load_{idx}')
                        elem_ptr = builder.gep(arr_ptr, [idx_val])
                        # Right side: variable, int, or arr[x]
                        if '[' in expr and expr.endswith(']'):
                            rarr = expr[:expr.find('[')].strip()
                            ridx = expr[expr.find('[')+1:-1].strip()
                            rarr_ptr = arrays[rarr]
                            ridx_val = ir.Constant(ir.IntType(32), int(ridx)) if ridx.isdigit() else builder.load(locals[ridx], name=f'load_{ridx}')
                            relem_ptr = builder.gep(rarr_ptr, [ridx_val])
                            rval = builder.load(relem_ptr, name=f'load_{rarr}_{ridx}')
                            builder.store(rval, elem_ptr)
                        elif expr in locals:
                            rval = builder.load(locals[expr], name=f'load_{expr}')
                            builder.store(rval, elem_ptr)
                        elif expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                            # Store as correct type
                            if array_types[arrname] == 'char':
                                rval = ir.Constant(ir.IntType(8), int(expr))
                            elif array_types[arrname] == 'float':
                                rval = ir.Constant(ir.FloatType(), float(expr))
                            elif array_types[arrname] == 'double':
                                rval = ir.Constant(ir.DoubleType(), float(expr))
                            else:
                                rval = ir.Constant(ir.IntType(32), int(expr))
                            builder.store(rval, elem_ptr)
                        else:
                            raise ValueError(f"Unsupported array assignment: {stmt}")
                    # Array access: x = arr[0]
                    elif '[' in expr and expr.endswith(']'):
                        arrname = expr[:expr.find('[')].strip()
                        idx = expr[expr.find('[')+1:-1].strip()
                        if arrname not in arrays:
                            raise ValueError(f"Unknown array '{arrname}'")
                        arr_ptr = arrays[arrname]
                        idx_val = ir.Constant(ir.IntType(32), int(idx)) if idx.isdigit() else builder.load(locals[idx], name=f'load_{idx}')
                        elem_ptr = builder.gep(arr_ptr, [idx_val])
                        builder.store(builder.load(elem_ptr, name=f'load_{arrname}_{idx}'), locals[lhs])
                    else:
                        if lhs not in locals:
                            raise ValueError(f"Variable '{lhs}' used before declaration")
                        # Simple support for 'a = b + c' or 'a = 3 + 4'
                        if '+' in expr:
                            left, right = expr.split('+', 1)
                            left = left.strip()
                            right = right.strip()
                            if left in locals:
                                left_val = builder.load(locals[left], name=f'load_{left}')
                            elif left.isdigit() or (left.startswith('-') and left[1:].isdigit()):
                                left_val = ir.Constant(ir.IntType(32), int(left))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{left}'")
                            if right in locals:
                                right_val = builder.load(locals[right], name=f'load_{right}')
                            elif right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
                                right_val = ir.Constant(ir.IntType(32), int(right))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{right}'")
                            result = builder.add(left_val, right_val, name=f'add_{lhs}')
                            builder.store(result, locals[lhs])
                        elif '-' in expr:
                            left, right = expr.split('-', 1)
                            left = left.strip()
                            right = right.strip()
                            if left in locals:
                                left_val = builder.load(locals[left], name=f'load_{left}')
                            elif left.isdigit() or (left.startswith('-') and left[1:].isdigit()):
                                left_val = ir.Constant(ir.IntType(32), int(left))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{left}'")
                            if right in locals:
                                right_val = builder.load(locals[right], name=f'load_{right}')
                            elif right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
                                right_val = ir.Constant(ir.IntType(32), int(right))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{right}'")
                            result = builder.sub(left_val, right_val, name=f'sub_{lhs}')
                            builder.store(result, locals[lhs])
                        elif '*' in expr:
                            left, right = expr.split('*', 1)
                            left = left.strip()
                            right = right.strip()
                            if left in locals:
                                left_val = builder.load(locals[left], name=f'load_{left}')
                            elif left.isdigit() or (left.startswith('-') and left[1:].isdigit()):
                                left_val = ir.Constant(ir.IntType(32), int(left))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{left}'")
                            if right in locals:
                                right_val = builder.load(locals[right], name=f'load_{right}')
                            elif right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
                                right_val = ir.Constant(ir.IntType(32), int(right))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{right}'")
                            result = builder.mul(left_val, right_val, name=f'mul_{lhs}')
                            builder.store(result, locals[lhs])
                        elif '/' in expr:
                            left, right = expr.split('/', 1)
                            left = left.strip()
                            right = right.strip()
                            if left in locals:
                                left_val = builder.load(locals[left], name=f'load_{left}')
                            elif left.isdigit() or (left.startswith('-') and left[1:].isdigit()):
                                left_val = ir.Constant(ir.IntType(32), int(left))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{left}'")
                            if right in locals:
                                right_val = builder.load(locals[right], name=f'load_{right}')
                            elif right.isdigit() or (right.startswith('-') and right[1:].isdigit()):
                                right_val = ir.Constant(ir.IntType(32), int(right))
                            else:
                                raise ValueError(f"Unknown variable or invalid literal: '{right}'")
                            result = builder.sdiv(left_val, right_val, name=f'div_{lhs}')
                            builder.store(result, locals[lhs])
                        else:
                            expr_clean = expr.strip()
                            # Function call assignment: a = func(x, y)
                            if '(' in expr_clean and expr_clean.endswith(')'):
                                fname = expr_clean[:expr_clean.find('(')].strip()
                                argstr = expr_clean[expr_clean.find('(')+1:-1]
                                argnames = [a.strip() for a in argstr.split(',') if a.strip()]
                                call_args = []
                                for a in argnames:
                                    if a in locals:
                                        call_args.append(builder.load(locals[a], name=f'load_{a}'))
                                    elif a.isdigit() or (a.startswith('-') and a[1:].isdigit()):
                                        call_args.append(ir.Constant(ir.IntType(32), int(a)))
                                    elif '[' in a and a.endswith(']'):
                                        arrname = a[:a.find('[')].strip()
                                        idx = a[a.find('[')+1:-1].strip()
                                        arr_ptr = arrays[arrname]
                                        idx_val = ir.Constant(ir.IntType(32), int(idx)) if idx.isdigit() else builder.load(locals[idx], name=f'load_{idx}')
                                        elem_ptr = builder.gep(arr_ptr, [idx_val])
                                        call_args.append(builder.load(elem_ptr, name=f'load_{arrname}_{idx}'))
                                    else:
                                        raise ValueError(f"Unknown argument '{a}' in call to '{fname}'")
                                if fname not in llvm_fns:
                                    raise ValueError(f"Function '{fname}' not declared")
                                callee = llvm_fns[fname]
                                result = builder.call(callee, call_args, name=f'call_{fname}')
                                builder.store(result, locals[lhs])
                            else:
                                try:
                                    # Detect variable type
                                    var_type = locals[lhs].type.pointee
                                    if isinstance(var_type, ir.FloatType):
                                        value = float(expr_clean)
                                        builder.store(ir.Constant(ir.FloatType(), value), locals[lhs])
                                    elif isinstance(var_type, ir.DoubleType):
                                        value = float(expr_clean)
                                        builder.store(ir.Constant(ir.DoubleType(), value), locals[lhs])
                                    elif isinstance(var_type, ir.IntType):
                                        value = int(float(expr_clean))  # Accepts '1.0' as '1' for int
                                        builder.store(ir.Constant(var_type, value), locals[lhs])
                                    else:
                                        raise ValueError(f"Unsupported variable type for '{lhs}'")
                                except ValueError:
                                    if expr_clean in locals:
                                        value = builder.load(locals[expr_clean], name=f'load_{expr_clean}')
                                        builder.store(value, locals[lhs])
                                    else:
                                        raise ValueError(f"Unsupported expression or invalid literal: '{expr_clean}'")
                elif '(' in stmt and stmt.endswith(')'):
                    # Bare function call, e.g., print():
                    fname = stmt[:stmt.find('(')].strip()
                    argstr = stmt[stmt.find('(')+1:-1]
                    argnames = [a.strip() for a in argstr.split(',') if a.strip()]
                    call_args = []
                    for a in argnames:
                        if a in locals:
                            call_args.append(builder.load(locals[a], name=f'load_{a}'))
                        elif a.isdigit() or (a.startswith('-') and a[1:].isdigit()):
                            call_args.append(ir.Constant(ir.IntType(32), int(a)))
                        elif '[' in a and a.endswith(']'):
                            arrname = a[:a.find('[')].strip()
                            idx = a[a.find('[')+1:-1].strip()
                            arr_ptr = arrays[arrname]
                            idx_val = ir.Constant(ir.IntType(32), int(idx)) if idx.isdigit() else builder.load(locals[idx], name=f'load_{idx}')
                            elem_ptr = builder.gep(arr_ptr, [idx_val])
                            call_args.append(builder.load(elem_ptr, name=f'load_{arrname}_{idx}'))
                        else:
                            raise ValueError(f"Unknown argument '{a}' in call to '{fname}'")
                    if fname not in llvm_fns:
                        raise ValueError(f"Function '{fname}' not declared")
                    callee = llvm_fns[fname]
                    builder.call(callee, call_args)
                    return
            elif isinstance(stmt, ReturnStmt):
                if stmt.expr:
                    expr = stmt.expr.strip().rstrip(';:')
                    if expr in locals:
                        builder.ret(builder.load(locals[expr], name=f'load_{expr}'))
                    else:
                        builder.ret(ir.Constant(ir.IntType(32), int(expr)))
                else:
                    builder.ret_void()
            elif isinstance(stmt, IfStmt):
                # Handle if/elif/else chain
                def emit_if_chain(ifstmt, after_bb):
                    cond_val = gen_cond(ifstmt.cond)
                    then_bb = llvm_fn.append_basic_block('then')
                    else_bb = llvm_fn.append_basic_block('else') if (ifstmt.elifs or ifstmt.else_body) else after_bb
                    builder.cbranch(cond_val, then_bb, else_bb)
                    builder.position_at_end(then_bb)
                    for s in ifstmt.body:
                        emit(s)
                    builder.branch(after_bb)
                    if ifstmt.elifs or ifstmt.else_body:
                        builder.position_at_end(else_bb)
                        # Handle elifs
                        elifs = ifstmt.elifs or []
                        for idx, elifstmt in enumerate(elifs):
                            next_else_bb = llvm_fn.append_basic_block(f'elif_else_{idx}') if (idx < len(elifs)-1 or ifstmt.else_body) else after_bb
                            cond_val = gen_cond(elifstmt.cond)
                            then_bb = llvm_fn.append_basic_block(f'elif_then_{idx}')
                            builder.cbranch(cond_val, then_bb, next_else_bb)
                            builder.position_at_end(then_bb)
                            for s in elifstmt.body:
                                emit(s)
                            builder.branch(after_bb)
                            builder.position_at_end(next_else_bb)
                        # Handle else
                        if ifstmt.else_body:
                            for s in ifstmt.else_body:
                                emit(s)
                            builder.branch(after_bb)
                after_bb = llvm_fn.append_basic_block('end_if')
                emit_if_chain(stmt, after_bb)
                builder.position_at_end(after_bb)
            elif isinstance(stmt, WhileStmt):
                loop_bb = llvm_fn.append_basic_block('loop')
                body_bb = llvm_fn.append_basic_block('body')
                after_bb = llvm_fn.append_basic_block('after')
                builder.branch(loop_bb)
                builder.position_at_end(loop_bb)
                cond_val = gen_cond(stmt.cond)
                builder.cbranch(cond_val, body_bb, after_bb)
                builder.position_at_end(body_bb)
                for s in stmt.body:
                    emit(s)
                builder.branch(loop_bb)
                builder.position_at_end(after_bb)

        # Second pass: emit all statements
        for st in fn.body:
            emit(st)

        # default return
        if not builder.block.is_terminated:
            if fn.ret_type=='int':
                builder.ret(ir.Constant(ir.IntType(32), 0))
            elif fn.ret_type=='float':
                builder.ret(ir.Constant(ir.FloatType(), 0.0))
            elif fn.ret_type=='double':
                builder.ret(ir.Constant(ir.DoubleType(), 0.0))
            else:
                builder.ret_void()

    return module

def main():
    if len(sys.argv)!=2:
        print("Usage: python compiler.py file.cpy"); sys.exit(1)
    in_path = sys.argv[1]
    if not os.path.isfile(in_path):
        print(f"Error: '{in_path}' not found."); sys.exit(1)

    with open(in_path) as f:
        lines = [l.rstrip() for l in f]
    funcs = parse(lines)
    mod = build_module(funcs)
    out = os.path.splitext(in_path)[0] + '.ll'
    with open(out,'w') as f:
        f.write(str(mod))
    print(f"LLVM IR written to {out}")

if __name__=='__main__':
    main()
