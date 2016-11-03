import os
import sys
import fnmatch
from glob import glob
from sisyphus import test
from sisyphus.test.test import Test
from sisyphus.test.steps import execute
from sisyphus.test.checks import check_retcode_zero, check_retcode_nonzero, create_check_reference_output

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
        if "should_fail/" in name:
            checks = [check_retcode_nonzero]
        if check_output:
            checks.append(create_check_reference_output(name+".ref"))
        # Sisyphus supports multiple steps like "compile" and "run".
        # Here we need only one.
        # Check return code and output against reference file.
        t.add_step(stepname, generic_step(stepcmd), checks=checks)
        return t
    return create_test

def find_java_files(dir):
    matches = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.java'):
                matches.append(os.path.join(root, filename))
    return matches

lex_test = generic_test("lex", "lextest")
parse_test = generic_test("parse", "parsetest", check_output=False)
ast_test = generic_test("ast", "print-ast")
semantic_test = generic_test("semantic", "check", check_output=False)

lex_testfiles = [p for p in find_java_files("lexer/")]
test.suite.make("lex", tests=map(lex_test, lex_testfiles))

parse_testfiles = [p for p in glob("parser/*.java")]
test.suite.make("ast", tests=map(ast_test, parse_testfiles))

parse_testfiles.extend(p for p in glob("parser/should_fail/*.java"))
test.suite.make("parse", tests=map(parse_test, parse_testfiles))

semantic_testfiles = [p for p in find_java_files("semantic/")]
test.suite.make("semantic", tests=map(semantic_test, semantic_testfiles))
