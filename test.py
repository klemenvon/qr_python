from argparse import ArgumentParser
from qrgen import QRGenerator, ByteEncoder

parser = ArgumentParser()
parser.add_argument('-v', '--version', type=int, default=1, help='QR Code version')
parser.add_argument('-m', '--module_size', type=int, default=5, help='Module size')
parser.add_argument('-s', '--save', type=str, help='Filename to save QR Code')
parser.add_argument('--show-mask', action='store_true', help='Show only data area.')
parser.add_argument('--mask', type=int, help='Mask pattern to apply')
args = parser.parse_args()

data = 'Hello World! This is just here for padding. Hi.'
data = " ".join([data for _ in range(100)])
encoder = ByteEncoder(data)
encoded_data = encoder.encode(qr_version=args.version)
print(encoded_data)

qr = QRGenerator(
    data=[encoded_data],
    version=args.version,
    module_size=args.module_size,
    padding=0,
)
qr.add_required_elements()
qr.place_data()
# qr.fill_white()
if args.mask is not None:
    print(f'Applying mask pattern {args.mask}')
    qr.apply_mask(args.mask)
else:
    qr.apply_best_mask()

if args.show_mask:
    if args.save:
        qr.save_mask(args.save)
    else:
        qr.show_mask()
else:
    if args.save:
        qr.save(args.save)
    else:
        qr.show()