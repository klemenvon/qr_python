from argparse import ArgumentParser
from qrgen import QRGenerator

parser = ArgumentParser()
parser.add_argument('-v', '--version', type=int, default=1, help='QR Code version')
parser.add_argument('-m', '--module_size', type=int, default=5, help='Module size')
parser.add_argument('-s', '--save', type=str, help='Filename to save QR Code')
parser.add_argument('--show_mask', action='store_true', help='Show only data area.')
args = parser.parse_args()

qr = QRGenerator(
    data='Hello World!',
    version=args.version,
    module_size=args.module_size,
    padding=0,
)
qr.add_required_elements()

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