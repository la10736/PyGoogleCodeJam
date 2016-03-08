import math
import unittest
from io import StringIO

import sys
from operator import attrgetter

class Obj(object):
    def __init__(self, x, y, z, vx, vy, vz):
        self.x, self.y, self.z, self.vx, self.vy, self.vz = x, y, z, vx, vy, vz

    def center(self, t=0.0):
        return self.x + t * self.vx, self.y + t * self.vy, self.z + t * self.vz

    @property
    def velocity(self):
        return self.vx, self.vy, self.vz

    @property
    def data(self):
        return self.x, self.y, self.z, self.vx, self.vy, self.vz


def mean(values):
    return sum(values) / len(values)


class M(Obj):
    def __init__(self, *objs):
        args = [mean([getattr(o, a) for o in objs]) for a in ("x", "y", "z", "vx", "vy", "vz")]
        super(M, self).__init__(*args)
        self.objs = objs


def parse_obj_line(line):
    return Obj(*map(int, line.split(" ", 5)))


def norm_quad(x, y, z):
    return x ** 2 + y ** 2 + z ** 2


def distance(x, y, z):
    return math.sqrt(norm_quad(x, y, z))


def min_time(o):
    x, y, z = o.center()
    vx, vy, vz = o.velocity
    nq = norm_quad(vx, vy, vz)
    if nq == 0:
        return 0
    return -(x * vx + y * vy + z * vz) / norm_quad(vx, vy, vz)


def parse_m(sio):
    n = int(sio.readline())
    return M(*[parse_obj_line(sio.readline()) for _ in range(n)])


class Test(unittest.TestCase):
    def test_obj(self):
        o = Obj(2, 3, 0, 3, 1, -2)
        self.assertEqual((2, 3, 0), o.center())
        self.assertEqual((8, 5, -4), o.center(2))

    def test_distance(self):
        self.assertEqual(1, distance(1, 0, 0))
        self.assertEqual(1, distance(0, 1, 0))
        self.assertEqual(1, distance(0, 0, 1))

        self.assertAlmostEqual(math.sqrt(3), distance(1, 1, 1))

    def test_min_time_trivial(self):
        o = Obj(1, 0, 0, 0, 1, 0)
        self.assertEqual(0, min_time(o))
        o = Obj(0, 0, 1, 0, 1, 0)
        self.assertEqual(0, min_time(o))
        o = Obj(0, 1, 0, 0, 0, 1)
        self.assertEqual(0, min_time(o))

        o = Obj(1, 1, -1, -1, -1, 1)
        self.assertEqual(1, min_time(o))

    def test_min_time_edge_case(self):
        o = Obj(1, 1, -1, 0, 0, 0)
        self.assertEqual(0, min_time(o))


    def test_m(self):
        m = M(Obj(1, 0, 0, 0, 1, 0), Obj(0, 0, 1, 0, 1, 0), Obj(0, 1, 0, 0, 0, 1))
        self.assertEqual((1 / 3, 1 / 3, 1 / 3), m.center())
        self.assertEqual((0, 2 / 3, 1 / 3), m.velocity)

    def test_parse_obj(self):
        o = parse_obj_line("-5 0 0 1 0 0")
        self.assertEqual((-5, 0, 0, 1, 0, 0), o.data)

    def test_parse_m(self):
        sio = StringIO("""3
-5 0 0 1 0 0
-7 0 0 1 0 0
-6 3 0 1 0 0
""")
        m = parse_m(sio)
        self.assertEqual((-5, 0, 0, 1, 0, 0), m.objs[0].data)
        self.assertEqual((-7, 0, 0, 1, 0, 0), m.objs[1].data)
        self.assertEqual((-6, 3, 0, 1, 0, 0), m.objs[2].data)


def usage():
    print("""{} <input_file> [output_file]""".format(sys.argv[0]))


def do_single(m):
    t = max(min_time(m), 0)
    return "{} {}".format(distance(*m.center(t)), t)


def do(src, dest):
    tests = int(src.readline())
    test_cases = [parse_m(src) for _ in range(tests)]
    for pos, m in enumerate(test_cases):
        dest.write("Case #{}: ".format(pos + 1) + do_single(m) + "\n")


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
