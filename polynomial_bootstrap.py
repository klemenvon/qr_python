from functools import lru_cache
from pprint import pprint

class GaloisField:
    def __init__(self, prime_modulus=0x11D, field_size=256):
        """Initialize Galois Field GF(2^8)"""
        self.prime_modulus = prime_modulus
        self.field_size = field_size
        self.exp = [0] * field_size  # exp table
        self.log = [0] * field_size  # log table
        
        # Generate exp and log tables
        x = 1
        for i in range(field_size):
            self.exp[i] = x
            if i < field_size - 1:  # log[0] is undefined
                self.log[x] = i
            x = self._multiply_no_lookup(x, 2)
            if x >= field_size:
                x ^= prime_modulus
    
    def _multiply_no_lookup(self, x, y):
        """Multiply two numbers in the field without using lookup tables"""
        result = 0
        while y:
            if y & 1:
                result ^= x
            y >>= 1
            x <<= 1
            if x >= self.field_size:
                x ^= self.prime_modulus
        return result
    
    def multiply(self, x, y):
        """Multiply two numbers in the field using lookup tables"""
        if x == 0 or y == 0:
            return 0
        return self.exp[(self.log[x] + self.log[y]) % (self.field_size - 1)]

class GeneratorPolynomialCalculator:
    def __init__(self):
        self.gf = GaloisField()
    
    def multiply_polynomials(self, poly1, poly2):
        """Multiply two polynomials in the Galois Field"""
        result = [0] * (len(poly1) + len(poly2) - 1)
        for i in range(len(poly1)):
            for j in range(len(poly2)):
                idx = i + j
                term = self.gf.multiply(poly1[i], poly2[j])
                result[idx] ^= term
        return result
    
    @lru_cache(maxsize=128)
    def generate_generator_polynomial(self, num_error_bytes):
        """
        Recursively generate the generator polynomial for given number of error correction bytes
        Using @lru_cache to store and reuse results
        """
        if num_error_bytes == 1:
            # Base case: g(x) = (x + α^0)
            return [1, self.gf.exp[0]]
        
        # Recursive case: g(x) = g_{n-1}(x) * (x + α^{n-1})
        prev_poly = self.generate_generator_polynomial(num_error_bytes - 1)
        multiplicand = [1, self.gf.exp[num_error_bytes - 1]]  # (x + α^{n-1})
        
        return self.multiply_polynomials(prev_poly, multiplicand)

    def generate_all_polynomials(self, max_bytes=68):
        """Generate all generator polynomials needed for QR codes"""
        return {i: self.generate_generator_polynomial(i) for i in range(1, max_bytes + 1)}


# Example usage and testing
def test_generator_polynomials():
    calc = GeneratorPolynomialCalculator()
    
    # Generate polynomials for EC lengths 7 and 8
    poly_7 = calc.generate_generator_polynomial(7)
    poly_8 = calc.generate_generator_polynomial(8)
    
    # The polynomial for length 8 should build upon length 7
    # This demonstrates the caching benefit
    print(f"Length 7 polynomial coefficients: {poly_7}")
    print(f"Length 8 polynomial coefficients: {poly_8}")
    
    # We can also see the cache info
    print(f"\nCache info: {calc.generate_generator_polynomial.cache_info()}")

required_poly = [7,10,13,15,16,17,18,20,22,24,26,28,30]

if __name__ == "__main__":
    calc = GeneratorPolynomialCalculator()
    polynomials = calc.generate_all_polynomials()
    polynomials = {k: v for k, v in polynomials.items() if k in required_poly}
    pprint(polynomials)