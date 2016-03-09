import operator
import sys
import unittest
from io import StringIO
from itertools import permutations

import time


class VectorPair(object):
    def __init__(self, v1, v2):
        if len(v1) != len(v2):
            raise ValueError()
        self.v1 = v1[:]
        self.v2 = v2[:]

    def scalar(self):
        return self._product(self.v1, self.v2)

    def better_permutation(self):
        v1, v2 = self.v1, self.v2
        l = len(self.v1)
        for orig in range(l):
            for swap in range(orig + 1, l):
                if self._swap_value(orig, swap) < self._orig_value(orig, swap):
                    old = v2[orig]
                    v2[orig] = v2[swap]
                    v2[swap] = old
                    return VectorPair(v1, v2)
        return self

    def _swap_value(self, orig, swap):
        return self.v1[orig] * self.v2[swap] + self.v1[swap] * self.v2[orig]

    def _orig_value(self, orig, swap):
        return self.v1[orig] * self.v2[orig] + self.v1[swap] * self.v2[swap]

    def best_permutation(self):
        v1, v2 = self.v1, self.v2
        v1.sort()
        v2.sort(reverse=True)
        return VectorPair(v1, v2)

    @classmethod
    def _product(cls, v1, v2):
        return sum(a * b for a, b in zip(v1, v2))


class Test(unittest.TestCase):
    def test_base(self):
        self.assertEqual(0, VectorPair([1, 0, 0], [0, 1, 1]).scalar())
        self.assertEqual(0, VectorPair([1, 0, 0], [0, 0, 1]).scalar())
        self.assertEqual(1, VectorPair([1, 0, 0], [1, 0, 1]).scalar())
        self.assertEqual(4, VectorPair([1, 1, 1], [1, 2, 1]).scalar())

    def test_single_swap(self):
        v = VectorPair([10, 1], [10, 1])
        w = v.better_permutation()
        self.assertEqual(w.scalar(), 20)
        w = w.better_permutation()
        self.assertEqual(w.scalar(), 20)

    def test_double_swap(self):
        v = VectorPair([100, 10, 1], [100, 10, 1])
        previous = v.scalar()
        w = v.better_permutation()
        self.assertLess(w.scalar(), previous)
        previous = w.scalar()
        w = w.better_permutation()
        self.assertLess(w.scalar(), previous)
        previous = w.scalar()
        w = w.better_permutation()
        self.assertLess(w.scalar(), previous)
        previous = w.scalar()
        self.assertEqual(300, previous)
        self.assertEqual(previous, w.better_permutation().scalar())

    def test_best(self):
        v = VectorPair([100, 10, 1], [100, 10, 1])
        self.assertEqual(300, v.best_permutation().scalar())
        v = VectorPair([10, 100, 1], [100, 10, 1])
        self.assertEqual(300, v.best_permutation().scalar())
        v = VectorPair([10, 1, 100], [100, 10, 1])
        self.assertEqual(300, v.best_permutation().scalar())
        v = VectorPair([10, 1, 100], [100, 10, 1])
        self.assertEqual(300, v.best_permutation().scalar())

    def test_integration(self):
        v1 = [1, 4, 6, 1000]
        v2 = [0, 32, -6, -2345]
        vp = VectorPair(v1, v2)
        value = vp.best_permutation().scalar()
        for v in permutations(v2):
            self.assertEqual(value, VectorPair(v1, list(v)).best_permutation().scalar())

    def test_parse_test_case(self):
        sio = StringIO("""3
1 3 -5
-2 4 1""")
        vp = parse_test_case(sio)
        self.assertEqual([1, 3, -5], vp.v1)
        self.assertEqual([-2, 4, 1], vp.v2)


def parse_test_case(f_in):
    l = len(f_in.readline().strip())
    v1 = [int(v) for v in f_in.readline().strip().split(" ")]
    v2 = [int(v) for v in f_in.readline().strip().split(" ")]
    return VectorPair(v1, v2)


def do_single(case):
    return case.best_permutation().scalar()


def do(f_in, f_out):
    print("=" * 20 + " START " + "=" * 20)
    start = time.time()
    tests = int(f_in.readline())
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
