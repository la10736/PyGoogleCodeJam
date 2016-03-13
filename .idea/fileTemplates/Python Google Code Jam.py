import os
import unittest
import sys
import time
from io import StringIO


# Set NR to  "A", "B" or "C"
NR = "A"


# Here your Code
# --------------


# noinspection PyPep8Naming
class Test(unittest.TestCase):
    def test_base(self):
        self.assertTrue(False)

    def test_parse_test_case(self):
        INPUT = """
        Cut and paste here one
        test case from webpage
        """
        si = StringIO(INPUT.strip())
        data = parse_test_case(si)
        self.fail("Write your asserts about data")

    def test_exec_example(self):
        INPUT = """
        Cut and paste here web INPUT example
        """
        OUTPUT = """
        Cut and paste here web OUTPUT example
        """
        si = StringIO(INPUT.strip())
        so = StringIO()
        for pos, case in enumerate(get_test_cases(si)):
            dump_case_result(case, so, pos + 1)
        self.assertEqual(so.getvalue().strip(), OUTPUT.strip())

    def test_solution(self):
        f_in_name = file_name("in")
        f_out_name = file_name("out")
        if not all(map(os.path.isfile, [f_in_name, f_out_name])):
            self.skipTest("Both small in and out should be present")
        f_in = open(f_in_name)
        f_out = StringIO()
        do(f_in, f_out)
        with open(f_out_name) as fixture:
            self.assertEqual(f_out.getvalue(), fixture.read())


def parse_test_case(f_in):
    raise NotImplementedError()


def do_single(case):
    raise NotImplementedError()


def get_test_cases(f_in):
    tests = int(f_in.readline())
    return [parse_test_case(f_in) for _ in range(tests)]


# noinspection PyUnusedLocal
def none_log(text):
    pass


def do(f_in, f_out, log=none_log):
    test_cases = get_test_cases(f_in)
    l = len(test_cases)
    log("=" * 20 + " START " + "=" * 20)
    start = time.time()
    for pos, case in enumerate(test_cases):
        pos += 1
        log("#" * 10 + "{}/{}".format(pos, l))
        s = time.time()
        dump_case_result(case, f_out, pos)
        log("Elapsed time: " + str(time.time() - s))
    log("Total Elapsed time: " + str(time.time() - start))
    log("=" * 20 + "  END  " + "=" * 20)


def dump_case_result(case, f_out, pos):
    f_out.write("Case #{}: ".format(pos) + str(do_single(case)) + "\n")


FILE_TEMPLATE = "{}-{}-practice.{}"


def file_name(direction, dimension="small", nr=NR):
    if direction not in ["in", "out"]:
        raise ValueError()
    return FILE_TEMPLATE.format(nr, dimension, direction)


def usage():
    print("""{} <input_file> [output_file]
or
{} small|large [-]
    """.format(sys.argv[0]))


def default_files(dimension, use_stdout):
    f_in_name = file_name("in", dimension)
    f_out_name = file_name("out", dimension)
    fin = open(f_in_name)
    if use_stdout:
        return fin, sys.stdout
    return fin, open(f_out_name, "w")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    if sys.argv[1] in ["small", "large"]:
        stdout_option = len(sys.argv) > 2 and sys.argv[2] == "-"
        src, dst = default_files(sys.argv[1], stdout_option)
    else:
        src, dst = open(sys.argv[1]), sys.stdout
        try:
            dst = open(sys.argv[2], "w")
        except IndexError:
            pass
    do(src, dst, print)
