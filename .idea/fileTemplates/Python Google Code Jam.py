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
    start = time.time()
    test_cases = [parse_test_case(f_in) for _ in range(tests)]
    l = len(test_cases)
    for pos, case in enumerate(test_cases):
        pos += 1
        print("#"*10 + "{}/{}".format(pos, l))
        s = time.time()
        f_out.write("Case #{}: ".format(pos) + str(do_single(case)) + "\n")
        print("Elapsed time: " + str(time.time()-s))
    print("Total Elapsed time: " + str(time.time()-start))
    print("=" * 20 + "  END  " + "=" * 20)


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
