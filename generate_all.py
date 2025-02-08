# Create or re-create all qr codes inside test_images/all/ directory
from qrgen import QRGenerator

def generate_qr(version, ec_level, data):
    qr = QRGenerator(
        data=data,
        version=version,
        ec_level=ec_level,
        module_size=10,
        padding=4,
    )
    qr.add_required_elements()
    qr.place_data()
    qr.apply_best_mask()
    qr.add_metadata()
    qr.save(f'test_images/all/{version}_{ec_level}.png')

# Generate all QR codes
for v in range(2, 41):
    for ec in 'LMQH':
        generate_qr(v, ec, 'Hello World!')
        print(f'Generated QR code for version {v} and error correction level {ec}')
