import unittest
import sys


class Test(unittest.TestCase):
    def test_base(self):
        self.assertTrue(False)


def parse_test_case(f_in):
    raise NotImplementedError()


def do_single(case):
    raise NotImplementedError()


def do(f_in, f_out):
    tests = int(f_in.readline())
    test_cases = [parse_test_case(f_in) for _ in range(tests)]
    for pos, case in enumerate(test_cases):
        f_out.write("Case #{}: ".format(pos + 1) + str(do_single(case)) + "\n")


def usage():
    print("""{} <input_file> [output_file]""".format(sys.argv[0]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    src = open(sys.argv[1])
    dest = sys.stdout
    try:
        dest = open(sys.argv[2], "w")
    except IndexError:
        pass
    do(src, dest)


if __name__ == '__main__':
    unittest.main()
