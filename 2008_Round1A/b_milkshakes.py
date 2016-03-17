import operator
import os
import unittest
import sys
import time
from io import StringIO
import itertools


# Set nr to  A, B or C
NR = "B"


class Solution(object):
    def __init__(self):
        self._flavors = set()
        self._cost = 0

    def add(self, flavor):
        if flavor in self._flavors:
            return
        if flavor.opposite() in self._flavors:
            raise ValueError("Invalid Solution")
        self._flavors.add(flavor)
        self._cost += int(flavor.is_malted)

    def has(self, flavor):
        return flavor in self._flavors

    def compatible(self, flavor):
        return flavor.opposite() not in self._flavors

    @property
    def cost(self):
        return self._cost

    def copy(self):
        s = Solution()
        s._flavors = self._flavors.copy()
        s._cost = self._cost
        return s


class FlavorPlanner(object):
    def __init__(self, shop, *customers):
        self._shop = shop
        ":type: MilkshakeShop"
        self._customers = customers

    def plan(self):
        raise NotImplementedError()


class TrivialFlavorPlanner(FlavorPlanner):
    def plan(self):
        flavors = self._shop.flavors
        candidates = itertools.product([False, True], repeat=len(flavors))
        candidates = sorted(candidates, key=sum)
        for c in candidates:
            if all(map(lambda customer: customer.satisfied(c), self._customers)):
                return [Flavor(f, malted) for f, malted in zip(flavors, c)]
        return None


class SmartFlavorPlanner(FlavorPlanner):
    def __init__(self, shop, *customers):
        super().__init__(shop, *customers)

    def plan(self):
        solution = Solution()
        self._customers = sorted(self._customers, key=operator.attrgetter("n_flavors"))
        for f in self._unmalted_no_conflict_flavors():
            solution.add(f)
        first = 0
        for pos, customer in enumerate(self._customers):
            if customer.n_flavors > 1:
                first = pos
                break
            try:
                solution.add(customer.flavors[0])
            except ValueError:
                return None
        try:
            solution = self._sub_planning(solution, first)
            return self._to_list(solution)
        except ValueError:
            return None

    def _sub_planning(self, solution, pos):
        pos = self._skip_first_satisfied_customers(solution, pos)
        if not self._customers[pos:]:
            return solution
        customer = self._customers[pos]
        solutions = []
        for flavor in customer.flavors:
            if not solution.compatible(flavor):
                continue
            new_solution = solution.copy()
            new_solution.add(flavor)
            try:
                solutions.append(self._sub_planning(new_solution, pos + 1))
            except ValueError:
                pass
        if not solutions:
            raise ValueError("Invalid solution")
        return min(solutions, key=operator.attrgetter("cost"))

    def _skip_first_satisfied_customers(self, solution, start):
        for pos, customer in enumerate(self._customers[start:]):
            if not customer.valid_solution(solution):
                return start + pos
        return len(self._customers)

    def _unmalted_no_conflict_flavors(self):
        unmalted = set()
        malted = set()
        for c in self._customers:
            unmalted.update(map(lambda code: Flavor(code, False), c.unmalted))
            malted.update(map(lambda code: Flavor(code, True), c.malted))
        return {f for f in unmalted if f.opposite() not in malted}

    def _to_list(self, solution):
        result = []
        for f in [Flavor(f, False) for f in self._shop.flavors]:
            result.append(f if not solution.has(f.opposite()) else f.opposite())
        return result


class MilkshakeShop(object):
    def __init__(self, flavors_numbers):
        self._flavors = [str(i) for i in range(1, flavors_numbers + 1)]

    @property
    def flavors(self):
        return self._flavors[:]

    def _unmalted_no_conflict_flavors(self, *customers):
        unmalted = set()
        malted = set()
        for c in customers:
            unmalted.update(map(lambda code:Flavor(code, False), c.unmalted))
            malted.update(map(lambda code:Flavor(code, True), c.malted))
        return {f for f in unmalted if f.opposite() not in malted}

    def _solution_to_list(self, solution):
        result = []
        for f in [Flavor(f, False) for f in self._flavors]:
            result.append(f if not solution.has(f.opposite()) else f.opposite())
        return result


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

    def opposite(self):
        return Flavor(self.name, not self.is_malted)

    def __str__(self):
        return self._name + ("m" if self.is_malted else "")

    def __eq__(self, other):
        return self.name == other.name and self.is_malted == other.is_malted

    def __hash__(self):
        return (1 + int(self.is_malted)) * hash(self._name)

    @classmethod
    def list_code(cls, flavors):
        return "|".join([str(f) for f in flavors])


class Customer(object):
    def __init__(self, *flavors):
        if not len(flavors):
            raise ValueError()
        self._flavors = list(flavors)
        self._malted_flavors_code = {f.name for f in self._flavors if f.is_malted}
        self._unmalted_flavors_code = {f.name for f in self._flavors if not f.is_malted}

    def satisfied(self, malted_list):
        for pos, is_malted in enumerate(malted_list):
            code = str(pos + 1)
            l = self._malted_flavors_code if is_malted else self._unmalted_flavors_code
            if code in l:
                return True
        return False

    def valid_solution(self, solution):
        return any((solution.has(f) for f in self._flavors))

    @property
    def n_flavors(self):
        return len(self._flavors)

    @property
    def flavors(self):
        return self._flavors[:]

    @property
    def malted(self):
        return self._malted_flavors_code.copy()

    @property
    def unmalted(self):
        return self._unmalted_flavors_code.copy()

    def __str__(self):
        return Flavor.list_code(self._flavors)


# noinspection PyPep8Naming
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
        result = SmartFlavorPlanner(shop, customer).plan()
        self.assertEqual("1|2", Flavor.list_code(result))

    def test_trivial_smart_planning(self):
        shop = MilkshakeShop(2)
        customer = Customer(Flavor(1, False), Flavor(2, True))
        result = SmartFlavorPlanner(shop, customer).plan()
        self.assertEqual("1|2", Flavor.list_code(result))

    def test_no_issue(self):
        shop = MilkshakeShop(5)
        c0 = Customer(Flavor(1, True))
        c1 = Customer(Flavor(1, False), Flavor(2, False))
        c2 = Customer(Flavor(5, False))
        result = SmartFlavorPlanner(shop, c0, c1, c2).plan()
        self.assertEqual("1m|2|3|4|5", Flavor.list_code(result))

    def test_no_issue_smart_planning(self):
        shop = MilkshakeShop(5)
        c0 = Customer(Flavor(1, True))
        c1 = Customer(Flavor(1, False), Flavor(2, False))
        c2 = Customer(Flavor(5, False))
        result = SmartFlavorPlanner(shop, c0, c1, c2).plan()
        self.assertEqual("1m|2|3|4|5", Flavor.list_code(result))

    def test_invalid_solution(self):
        s = Solution()
        s.add(Flavor(1, True))
        with self.assertRaises(ValueError):
            s.add(Flavor(1, False))

    def test_solution_cost(self):
        s = Solution()
        self.assertEqual(0, s.cost)
        s.add(Flavor(1, True))
        self.assertEqual(1, s.cost)
        s.add(Flavor(2, True))
        self.assertEqual(2, s.cost)
        s.add(Flavor(3, False))
        s.add(Flavor(4, False))
        s.add(Flavor(7, True))
        self.assertEqual(3, s.cost)
        s.add(Flavor(7, True))
        self.assertEqual(3, s.cost)

    def test_impossible(self):
        shop = MilkshakeShop(1)
        c0 = Customer(Flavor(1, False))
        c1 = Customer(Flavor(1, True))
        self.assertIsNone(SmartFlavorPlanner(shop, c0, c1).plan())

    def test_parse_test_case(self):
        INPUT = """
5
3
1 1 1
2 1 0 2 0
1 5 0
        """
        si = StringIO(INPUT.strip())
        shop, customers = parse_test_case(si)
        self.assertEqual(5, len(shop.flavors))
        self.assertEqual(3, len(customers))
        self.assertEqual("1m-1|2-5", "-".join(map(str, customers)))

    def test_exec_example(self):
        INPUT = """
2
5
3
1 1 1
2 1 0 2 0
1 5 0
1
2
1 1 0
1 1 1
        """
        OUTPUT = """
Case #1: 1 0 0 0 0
Case #2: IMPOSSIBLE
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


def parse_customer(line):
    elements = line.split(" ")
    choices = int(elements[0])
    flavors = []
    for i in range(0, 2 * choices, 2):
        flavors.append(Flavor(int(elements[i + 1]), int(elements[i + 2])))
    return Customer(*flavors)


def parse_test_case(f_in):
    shop = MilkshakeShop(int(f_in.readline().strip()))
    n_customers = int(f_in.readline().strip())
    customers = [parse_customer(f_in.readline()) for _ in range(n_customers)]
    return shop, customers


def do_single(case):
    shop, customers = case
    planning = SmartFlavorPlanner(shop, *customers).plan()
    if planning is None:
        return "IMPOSSIBLE"
    return " ".join([str(int(f.is_malted)) for f in planning])


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
