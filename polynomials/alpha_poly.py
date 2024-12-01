from alpha import Alpha
from polynomials.poly import Poly
from global_settings import Global


class AlphaPoly(Poly):
    M = Global.M
    T = Global.T

    coefficients = None
    alphas = None

    def __init__(self, coefficients):
        from galois import Galois
        self.gallois = Galois()
        self.coefficients = coefficients
        self.alphas = [Alpha(x) for x in self.coefficients]

    def __str__(self):
        poly = self.alphas
        if len(poly) == 0:
            return "None"

        return f"[{', '.join([str(alpha) for alpha in self.alphas])}]"

    def __repr__(self):
        return f"AlphaPoly({self.coefficients})"

    def __setitem__(self, key, value):
        self.coefficients[key] = value
        self.alphas[key] = Alpha(value)

    def get_trimmed(self):
        coefficients_copy = self.coefficients[:]
        while len(coefficients_copy) > 1 and coefficients_copy[0] is None:
            coefficients_copy.pop(0)
        return AlphaPoly(coefficients_copy)

    def get_filled(self, desired_no_of_bits):
        filled_coefficients = ([None] * (desired_no_of_bits - len(self.coefficients))) + self.coefficients
        return AlphaPoly(filled_coefficients)

    def __add__(self, other):
        max_len = max(len(self.alphas), len(other.alphas))
        poly1 = self.get_filled(max_len).alphas
        poly2 = other.get_filled(max_len).alphas

        alpha_poly = [x + y for (x, y) in zip(poly1, poly2)]
        alpha_poly_coefficients = list(map(lambda x: x.power, alpha_poly))

        return AlphaPoly(alpha_poly_coefficients)

    def division_with_remainder(self, p1, p2):
        poly1 = p1.get_trimmed().coefficients
        poly2 = p2.get_trimmed().coefficients

        if not any(poly2):
            raise ValueError("Divisor cannot be zero polynomial")

        remainder = poly1[:]
        result = []

        iteration = 0
        max_len = len(poly1) - len(poly2)

        while iteration <= max_len:
            # if remainder[iteration] is None:
            #     result.append(0)
            # else:
            #     result.append((remainder[iteration]) - poly2[0])

            if remainder[iteration] is None or poly2[0] is None:
                result.append(None)
                iteration += 1
                continue
            else:
                result.append(remainder[iteration] - poly2[0])

            # Create sub poly
            sub_poly = []
            if result[iteration] is None:
                pass
            elif result[iteration] == 0:
                sub_poly = poly2
            else:
                for i in poly2:
                    if i is None:
                        sub_poly.append(None)
                    elif i == 0:
                        sub_poly.append(result[iteration])
                    else:
                        alfa1 = result[iteration]
                        alfa2 = i

                        value = self.gallois.alpha_powers[alfa1] * self.gallois.alpha_powers[alfa2]
                        sub_poly.append(self.gallois.poly_2_alpha_power(value))

            # Reminder - sub_poly
            for i in range(0, len(sub_poly)):
                if remainder[iteration + i] is None:
                    remainder[iteration + i] = sub_poly[i]
                elif remainder[iteration + i] == sub_poly[i]:
                    remainder[iteration + i] = None
                else:
                    alfa1 = remainder[i + iteration]
                    alfa2 = sub_poly[i]
                    # print(f"Alfa1: {alfa1} | Alfa2: {alfa2}")

                    value = self.gallois.alpha_powers[alfa1] if alfa2 is None else self.gallois.alpha_powers[alfa1] + \
                                                                                   self.gallois.alpha_powers[alfa2]
                    remainder[iteration + i] = self.gallois.poly_2_alpha_power(value)
            # print(iteration)
            # print(f"{poly1} : {poly2} = {result}")
            # print(f"{sub_poly}")
            # print(remainder)
            iteration += 1
        result = [(x + (2 ** self.M - 1)) if (x is not None and x < 0) else x for x in result]

        return AlphaPoly(result), AlphaPoly(remainder)

    def __truediv__(self, other):
        result, _ = self.division_with_remainder(self, other)
        return result

    def __mod__(self, other):
        _, remainder = self.division_with_remainder(self, other)
        return remainder.get_trimmed()

    def __mul__(self, other):
        poly1 = self.coefficients
        poly2 = other.coefficients

        result = [None] * (len(poly1) + len(poly2) - 1)

        for i in range(len(poly1)):
            if poly1[i] is None:
                continue
            for j in range(len(poly2)):
                if poly2[j] is None:
                    continue
                result[i + j] = \
                (AlphaPoly([result[i + j]]) + AlphaPoly([((poly1[i] + poly2[j]) % (2 ** self.M - 1))])).coefficients[0]

        return AlphaPoly(result)

    def get_cyclic_shifted(self, no_of_positions, direction="left"):
        n = len(self.coefficients)
        shifted_coefficients = self.coefficients[:]

        no_of_positions = no_of_positions % n

        if direction == "left":
            shifted_coefficients = shifted_coefficients[no_of_positions:] + shifted_coefficients[:no_of_positions]
        elif direction == "right":
            shifted_coefficients = shifted_coefficients[-no_of_positions:] + shifted_coefficients[:-no_of_positions]
        else:
            raise ValueError("Direction must be 'left' or 'right'")

        return AlphaPoly(shifted_coefficients)

    def get_shifted(self, no_of_positions):
        copy = AlphaPoly(self.coefficients)
        copy *= AlphaPoly([0] + [None] * no_of_positions)

        return copy
