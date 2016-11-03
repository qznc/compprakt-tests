import os
import sys
from glob import glob
from sisyphus import test
from sisyphus.test.test import Test
from sisyphus.test.steps import execute
from sisyphus.test.checks import check_retcode_zero, create_check_reference_output

def setup_argparser(argparser, default_env):
    group = argparser.add_argument_group("Compiler Praktikum")
    group.add_argument("--compiler", dest="compiler", metavar="COMPILER",
        help="Use COMPILER to change minijava compiler")
    default_env.set(
        compiler="compprakt-reference",
    )
test.suite.add_argparser_setup(setup_argparser)

def step_lextest(env):
    """Command to execute as lextest step"""
    return execute(env, "%(compiler)s --lextest %(testname)s" % env, timeout=60)

def lex_test(name):
    """How performing a lexer test is actually done"""
    t = Test(name)
    # Sisyphus supports multiple steps like "compile" and "run".
    # Here we need only one.
    # Check return code and output against reference file.
    t.add_step("lextest", step_lextest, checks=[
        check_retcode_zero,
        create_check_reference_output(name+".ref"),
    ])
    return t

lex_testfiles = [p for p in glob("lexer/*") if not p.endswith(".ref")]
test.suite.make("lex", tests=map(lex_test, lex_testfiles))

def step_parsetest(env):
    """Command to execute as parsetest step"""
    return execute(env, "%(compiler)s --parsetest %(testname)s" % env, timeout=60)

def step_asttest(env):
    """Command to execute as AST parsetest step"""
    return execute(env, "%(compiler)s --print-ast %(testname)s" % env, timeout=60)

def parse_test(name):
    t = Test(name)
    t.add_step("parsetest", step_parsetest, checks=[ check_retcode_zero ])
    return t

def ast_test(name):
    t = Test(name)
    t.add_step("AST test", step_asttest, checks=[
        check_retcode_zero,
        create_check_reference_output(name+".ref"),
    ])
    return t

parse_testfiles = [p for p in glob("parser/*") if not p.endswith(".ref")]
test.suite.make("parse", tests=map(parse_test, parse_testfiles))
test.suite.make("ast", tests=map(ast_test, parse_testfiles))

def step_semantictest(env):
    """Command to execute as semantictest step"""
    return execute(env, "%(compiler)s --check %(testname)s" % env, timeout=60)

def semantic_test(name):
    t = Test(name)
    t.add_step("semantictest", step_semantictest, checks=[ check_retcode_zero ])
    return t

semantic_testfiles = [p for p in glob("semantic/*.java")]
test.suite.make("semantic", tests=map(semantic_test, semantic_testfiles))
