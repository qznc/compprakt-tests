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

def generic_step(param):
    def step(env):
        """Command to execute as step"""
        cmd = "%(compiler)s --"+param+" %(testname)s"
        return execute(env, cmd % env, timeout=60)
    return step

def generic_test(stepname, stepcmd, check_output=True):
    def create_test(name):
        t = Test(name)
        checks = [check_retcode_zero]
        if check_output:
            checks.append(create_check_reference_output(name+".ref"))
        # Sisyphus supports multiple steps like "compile" and "run".
        # Here we need only one.
        # Check return code and output against reference file.
        t.add_step(stepname, generic_step(stepcmd), checks=checks)
        return t
    return create_test

lex_test = generic_test("lex", "lextest")
parse_test = generic_test("parse", "parsetest", check_output=False)
ast_test = generic_test("ast", "print-ast")
semantic_test = generic_test("semantic", "check", check_output=False)

lex_testfiles = [p for p in glob("lexer/*") if not p.endswith(".ref")]
test.suite.make("lex", tests=map(lex_test, lex_testfiles))

parse_testfiles = [p for p in glob("parser/*") if not p.endswith(".ref")]
test.suite.make("parse", tests=map(parse_test, parse_testfiles))
test.suite.make("ast", tests=map(ast_test, parse_testfiles))

semantic_testfiles = [p for p in glob("semantic/*.java")]
test.suite.make("semantic", tests=map(semantic_test, semantic_testfiles))
