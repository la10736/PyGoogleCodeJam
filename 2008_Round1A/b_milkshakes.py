import unittest
import sys
import time

import itertools


class MilkshakeShop(object):
    def __init__(self, flavors_numbers):
        self._flavors = [str(i) for i in range(1, flavors_numbers + 1)]

    @property
    def flavors(self):
        return self._flavors[:]

    def trivial_planning(self, *customers):
        candidates = itertools.product([False, True], repeat=len(self._flavors))
        candidates = sorted(candidates, key=sum)
        for c in candidates:
            if all(map(lambda customer: customer.satisfied(c), customers)):
                return [Flavor(f, malted) for f, malted in zip(self._flavors, c)]
        return None

    def best_planning(self, *customers):
        return self.trivial_planning(*customers)


class Flavor(object):
    def __init__(self, name, malted):
        self._name = str(name)
        self._malted = malted

    @property
    def name(self):
        return self._name

    @property
    def is_malted(self):
        return self._malted

    def __str__(self):
        return self._name + ("m" if self.is_malted else "")

    @classmethod
    def list_code(cls, flavors):
        return "|".join([str(f) for f in flavors])


class Customer(object):
    def __init__(self, *flavors):
        if not len(flavors):
            raise ValueError()
        self._flavors = list(flavors)
        self._maletd_flavors_code = {f.name for f in self._flavors if f.is_malted}
        self._unmaletd_flavors_code = {f.name for f in self._flavors if not f.is_malted}

    def satisfied(self, malted_list):
        for pos, is_malted in enumerate(malted_list):
            code = str(pos + 1)
            l = self._maletd_flavors_code if is_malted else self._unmaletd_flavors_code
            if code in l:
                return True
        return False

    def __str__(self):
        return Flavor.list_code(self._flavors)


class Test(unittest.TestCase):
    def test_base(self):
        shop = MilkshakeShop(4)
        self.assertEqual(["1", "2", "3", "4"], shop.flavors)

    def test_customer(self):
        with self.assertRaises(ValueError):
            Customer()
        customer = Customer(Flavor(1, False), Flavor(2, True), Flavor(5, False))
        self.assertEqual("1|2m|5", str(customer))

    def test_trivial(self):
        shop = MilkshakeShop(2)
        customer = Customer(Flavor(1, False), Flavor(2, True))
        result = shop.best_planning(customer)
        self.assertEqual("1|2", Flavor.list_code(result))

    def test_no_issue(self):
        shop = MilkshakeShop(5)
        c0 = Customer(Flavor(1, True))
        c1 = Customer(Flavor(1, False), Flavor(2, False))
        c2 = Customer(Flavor(5, False))
        result = shop.best_planning(c0, c1, c2)
        self.assertEqual("1m|2|3|4|5", Flavor.list_code(result))

    def test_impossible(self):
        shop = MilkshakeShop(1)
        c0 = Customer(Flavor(1, False))
        c1 = Customer(Flavor(1, True))
        self.assertIsNone(shop.best_planning(c0, c1))


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
        print("#" * 10 + "{}/{}".format(pos, l))
        s = time.time()
        f_out.write("Case #{}: ".format(pos) + str(do_single(case)) + "\n")
        print("Elapsed time: " + str(time.time() - s))
    print("Total Elapsed time: " + str(time.time() - start))
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
