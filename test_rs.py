from reedsolo import RSCodec
from typing import List, Tuple, Dict
import sys

from qrgen.polynomial_gen import GeneratorPolynomialCalculator
from qrgen.reedsolomon import ReedSolomonEncoder

class ReedSolomonTester:
    def __init__(self):
        self.gpc = GeneratorPolynomialCalculator()
        
    def encode_message(self, message: bytes, num_ecc: int) -> List[int]:
        """
        Encode a message using your implementation.
        """
        # Convert bytes to list of integers
        data = list(message)
    
        # Create encoder and encode the data
        encoder = ReedSolomonEncoder(self.gpc)
        return encoder.encode_block(data, num_ecc)

    @staticmethod
    def reference_encode(message: bytes, num_ecc: int) -> List[int]:
        """Use the reedsolo library as reference implementation"""
        rsc = RSCodec(num_ecc)
        encoded = rsc.encode(message)
        # Extract just the ECC portion (last num_ecc bytes)
        return list(encoded[-num_ecc:])

    @staticmethod
    def compare_results(yours: List[int], reference: List[int]) -> Tuple[bool, str, List[Dict]]:
        """Compare two lists of ECC bytes and return detailed differences"""
        if len(yours) != len(reference):
            return False, f"Length mismatch: yours={len(yours)}, reference={len(reference)}", []
        
        differences = []
        for i, (y, r) in enumerate(zip(yours, reference)):
            if y != r:
                differences.append({
                    'position': i,
                    'yours': hex(y),
                    'reference': hex(r),
                    'xor_diff': hex(y ^ r)  # Shows which bits are different
                })
        
        return len(differences) == 0, \
               f"Found {len(differences)} differences" if differences else "Perfect match", \
               differences

def generate_test_messages() -> List[Tuple[str, bytes]]:
    """Generate a variety of test messages"""
    return [
        ("Simple ASCII", b"Hello, World!"),
        ("Numbers", b"12345"),
        ("Binary", bytes([x % 256 for x in range(20)])),
        ("QR Alphanumeric", b"HELLO WORLD 123456789"),
        ("URL", b"https://example.com/path?param=value"),
        ("Long message", b"This is a longer message that will require more error correction bytes" * 2),
        ("Special chars", bytes([0xFF, 0x00, 0xAA, 0x55, 0x12, 0x34, 0x56, 0x78])),
        # Add more test cases as needed
    ]

def run_tests():
    tester = ReedSolomonTester()
    test_messages = generate_test_messages()
    
    # Test with ECC lengths from 1 to 30
    ecc_lengths = range(1, 31)
    
    for desc, message in test_messages:
        print(f"\nTesting message: {desc}")
        print(f"Message bytes: {message[:30]}{'...' if len(message) > 30 else ''}")
        print(f"Message length: {len(message)} bytes")
        
        for num_ecc in ecc_lengths:
            print(f"\nTesting with {num_ecc} ECC bytes:")
            
            # Get results from both implementations
            try:
                your_ecc = tester.encode_message(message, num_ecc)
                ref_ecc = tester.reference_encode(message, num_ecc)
                
                # Compare results
                match, reason, differences = tester.compare_results(your_ecc, ref_ecc)
                
                if match:
                    print(f"✓ Match achieved for {num_ecc} ECC bytes")
                else:
                    print(f"✗ Mismatch for {num_ecc} ECC bytes")
                    print(f"Reason: {reason}")
                    print("\nDetailed differences:")
                    for diff in differences:
                        print(f"Position {diff['position']}:")
                        print(f"  Your value:      {diff['yours']}")
                        print(f"  Reference value: {diff['reference']}")
                        print(f"  XOR difference:  {diff['xor_diff']}")
                    
                    # Print the full arrays for comparison when there's a mismatch
                    print("\nFull ECC arrays:")
                    print("Yours:     ", [hex(x) for x in your_ecc])
                    print("Reference: ", [hex(x) for x in ref_ecc])
                    
            except Exception as e:
                print(f"Error during encoding: {str(e)}")
                print(f"Stack trace: {sys.exc_info()}")

if __name__ == "__main__":
    run_tests()
