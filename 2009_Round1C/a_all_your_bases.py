import unittest
import sys

def get_base(code):
    return max(2, len(set(code)))


def sub_solve(base, code, code_map):
    if not code:
        return 0
    c = code[0]
    if c not in code_map:
        code_map[c] = min([x for x in range(base) if x not in code_map.values()])
    return code_map[c] * base ** (len(code) - 1) + sub_solve(base, code[1:], code_map)


def solve(code):
    base = get_base(code)
    code_map = {code[0]: 1}
    val = base ** (len(code) - 1)
    return val + sub_solve(base, code[1:], code_map)

def read_file(path):
    tests = []
    with open(path) as f:
        l = int(f.readline())
        return [l.strip() for l in f.readlines()]

class Test(unittest.TestCase):

    def test_get_base(self):
        self.assertEqual(2, get_base("a"))
        self.assertEqual(2, get_base("1"))
        self.assertEqual(2, get_base("7"))
        self.assertEqual(2, get_base("ab"))
        self.assertEqual(2, get_base("10"))
        self.assertEqual(2, get_base("77"))
        self.assertEqual(5, get_base("123as"))
        self.assertEqual(4, get_base("cats"))

    def test_solve(self):
        self.assertEqual(1, solve("a"))
        self.assertEqual(2, solve("ab"))

    def test_ex_0(self):
        self.assertEqual(4, solve("100"))

    def test_ex_1(self):
        self.assertEqual(201, solve("11001001"))

    def test_ex_2(self):
        self.assertEqual(75, solve("cats"))


if __name__ == "__main__":
    source = sys.argv[1]
    dest = sys.stdout
    if len(sys.argv)>2:
        dest = open(sys.argv[2], "w")
    test = read_file(source)
    for num, code in enumerate(test):
        dest.write("Case #%d: %d\n" % (num+1, solve(code)))