from argparse import ArgumentParser
# TODO: Move this into QR generator so we don't need all these imports
from qrgen import QRGenerator, ByteEncoder, interleave_blocks, get_codeword_capacity, QRErrorCorrection, BitStream

parser = ArgumentParser()
parser.add_argument('-v', '--version', type=int, default=1, help='QR Code version')
parser.add_argument('-e', '--ec_level', type=str, default='Q', help='Error correction level')
parser.add_argument('-m', '--module_size', type=int, default=5, help='Module size')
parser.add_argument('-s', '--save', type=str, help='Filename to save QR Code')
parser.add_argument('--show-mask', action='store_true', help='Show only data area.')
parser.add_argument('--mask', type=int, help='Mask pattern to apply')
args = parser.parse_args()

data = 'Hello World! This is just here for padding. Hi.'
# data = 'Hello World!'
# data = 'https://youtu.be/dQw4w9WgXcQ'
# data = " ".join([data for _ in range(5)])


qr = QRGenerator(
    data=data,
    version=args.version,
    ec_level=args.ec_level,
    module_size=args.module_size,
    padding=4,
)
qr.add_required_elements()
qr.place_data()
# qr.fill_white()
if args.mask is not None:
    print(f'Applying mask pattern {args.mask}')
    qr.apply_mask(args.mask)
    qr.mask_pattern = args.mask
    qr.add_metadata()
else:
    qr.apply_best_mask()
    qr.add_metadata()

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