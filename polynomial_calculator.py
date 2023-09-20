import re


def standard(pairs):
    standard_dic = {}
    for pair in pairs:
        if pair[0] not in standard_dic:
            standard_dic[pair[0]] = pair[1]
        else:
            standard_dic[pair[0]] += pair[1]
    pairs = [(key, value) for key, value in standard_dic.items()]
    sorted(pairs, reverse=True)
    return pairs


def string(pairs, variable):
    exp= ""
    for pair in pairs:
        # positive coefficient
        if pair[1] > 0:
            # powers greater than 1
            if pair[0] > 1:
                exp += "+" + str(pair[1]) + "*" + variable + "**" + str(pair[0])
            # power 1
            if pair[0] == 1:
                exp += "+" + str(pair[1]) + "*" + variable

        # negative coefficient
        elif pair[1] < 0:
            # powers greater than 1
            if pair[0] > 1:
                exp += str(pair[1]) + "*" + variable + "**" + str(pair[0])
            # power 1
            if pair[0] == 1:
                exp += str(pair[1]) + "*" + variable

        # power 0
        if pair[0] == 0:
            if pair[1] > 0:
                exp += "+" + str(pair[1])
            if pair[1] < 0:
                exp += str(pair[1])
            if pair[1] == 0:
                continue
    if exp == "":
        return "0"

    return exp


class Polynomial:
    quotient = [(0, 0)]

    def __init__(self, exp, variable):
        self.exp = exp
        self.variable = variable
        self.pairs = self.pairs(self.coefficients(), self.powers(), self.constant())

    def powers(self):
        """This function returns all the powers in the given expression."""
        pat_power = r"(?<=\*{2})[0-9]+(?=[\+|\-]*)|[a-z][^\*{2}]"
        powers = re.findall(pat_power, self.exp)
        if self.exp[-1] == self.variable:
            powers.append("1")

        for i in range(len(powers)):
            if powers[i][-1] == "+" or powers[i][-1] == "-":
                idx = powers.index(powers[i])
                powers[idx] = "1"
            powers[i] = int(powers[i])

        return powers

    def coefficients(self):
        """This function returns all the coefficients in the given expression."""
        pattern = r"[\+|\-][0-9]+(?=\*)"
        coeffs = re.findall(pattern, self.exp)

        for i in range(len(coeffs)):
            coeffs[i] = int(coeffs[i])

        return coeffs

    def constant(self):
        """This function returns the sum of the constants in the given expression."""
        zero_power = r"[+-][0-9]*\d+(?:\.\d+)?(?=[-+\s]|$)"
        zero_powers = re.findall(zero_power, self.exp)

        for i in range(len(zero_powers)):
            if zero_powers[i][-1] == "+" or zero_powers[i][-1] == "-":
                zero_powers[i] = zero_powers[i][:-1]

        for i in range(len(zero_powers)):
            zero_powers[i] = int(zero_powers[i])

        constant = sum(zero_powers)

        return constant

    def pairs(self, coeffs, powers, constant):
        pairs_dic = {}
        i = 0
        while i < len(coeffs):
            if powers[i] not in pairs_dic:
                pairs_dic[powers[i]] = coeffs[i]
                i += 1
            else:
                pairs_dic[powers[i]] += coeffs[i]
                i += 1

        pairs_dic[0] = constant
        pairs = [(key, value) for key, value in pairs_dic.items()]

        return sorted(pairs, reverse=True)

    def __str__(self):
        return self.exp

    def __add__(self, other):
        sum_pair = []
        f = lambda x, y: x if x <= y else y
        length = f(len(self.pairs), len(other.pairs))
        i = 0
        j = 0

        while i < length and j < length:
            if self.pairs[i][0] == other.pairs[j][0]:
                sum_pair.append((self.pairs[i][0], self.pairs[i][1] + other.pairs[j][1]))
                i += 1
                j += 1

            elif self.pairs[i][0] > other.pairs[j][0]:
                sum_pair.append((self.pairs[i][0], self.pairs[i][1]))
                i += 1

            elif self.pairs[i][0] < other.pairs[j][0]:
                sum_pair.append((other.pairs[j][0], other.pairs[j][1]))
                j += 1

        for i in range(i, len(self.pairs)):
            sum_pair.append((self.pairs[i][0], self.pairs[i][1]))

        for j in range(j, len(other.pairs)):
            sum_pair.append((other.pairs[j][0], other.pairs[j][1]))

        return Polynomial(string(sorted(standard(sum_pair), reverse=True), self.variable), self.variable)

    def __sub__(self, other):
        sub_pair = []

        for i in range(len(other.pairs)):
            sub_pair.append((other.pairs[i][0], -1 * other.pairs[i][1]))

        exp = Polynomial(string(sub_pair, self.variable), self.variable)
        sub = self + exp
        return sub

    def __mul__(self, other):
        mul_pairs = []

        for pair1 in self.pairs:
            for pair2 in other.pairs:
                mul_pairs.append((pair1[0] + pair2[0], pair1[1]*pair2[1]))

        return Polynomial(string(sorted(standard(mul_pairs), reverse=True), self.variable), self.variable)

    def __divmod__(self, other):
        global dividend
        quotient = Polynomial("0", self.variable)
        dividend = Polynomial(self.exp, self.variable)
        divisor = Polynomial(string([other.pairs[0]], self.variable), self.variable)

        if len(dividend.pairs) == 0:
            return Polynomial(string(Polynomial.quotient, self.variable), self.variable), dividend

        if dividend.pairs[0][0] < divisor.pairs[0][0]:
            return Polynomial(string(Polynomial.quotient, self.variable), self.variable), dividend

        quotient += Polynomial(string([(dividend.pairs[0][0] - divisor.pairs[0][0], dividend.pairs[0][1] //
                                        divisor.pairs[0][1])], self.variable), self.variable)

        dividend -= Polynomial(string([quotient.pairs[0]], self.variable), self.variable) * other
        Polynomial.quotient += quotient.pairs
        dividend.pairs.remove(dividend.pairs[0])
        divmod(dividend, other)

        return Polynomial(string(Polynomial.quotient, self.variable), self.variable), dividend

    def derivative(self):
        d = []
        for pair in self.pairs:
            if pair[0] > 0:
                d.append((pair[0] - 1, pair[0]*pair[1]))

        return Polynomial(string(sorted(d, reverse=True), self.variable), self.variable)


inp = input().split()
variable = inp[0]
operand = inp[1]
if len(inp) > 2:
    for item in inp[2:]:
        operand += " " + item

if operand != "first order derivative":
    if operand != "second order derivative":
        exp1 = input()
        exp1 = Polynomial(exp1, variable)
        exp2 = input()
        exp2 = Polynomial(exp2, variable)

    if operand == "add":
        result = exp1 + exp2
        print(result)

    if operand == "subtract":
        result = exp1 - exp2
        print(result)

    if operand == "multiply":
        result = exp1 * exp2
        print(result)

    if operand == "division":
        result = divmod(exp1, exp2)
        print(result[0], result[1])

if operand == "first order derivative":
    exp = input()
    exp = Polynomial(exp, variable)
    print(exp.derivative())

elif operand == "second order derivative":
    exp = input()
    exp = Polynomial(exp, variable)
    exp = exp.derivative()
    exp = exp.derivative()
    print(exp)

