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
# data = " ".join([data for _ in range(100)])
encoder = ByteEncoder(data)
encoded_data = encoder.encode(qr_version=args.version)
capacity = get_codeword_capacity(args.version, args.ec_level) * 8
if len(encoded_data) > capacity:
    raise ValueError(f'Data too long for version {args.version} with error correction level {args.ec_level}')
encoded_data.pad_to_length(capacity)

# Encode the data with Reed-Solomon error correction
qr_ec = QRErrorCorrection(version=args.version, ec_level=args.ec_level)
data_blocks, ec_blocks = qr_ec.encode_data(encoded_data.buffer)
data_final = interleave_blocks(data_blocks)
ec_final = interleave_blocks(ec_blocks)
data_stream = BitStream.from_int8_array(data_final)
ec_stream = BitStream.from_int8_array(ec_final)


qr = QRGenerator(
    data=[data_stream, ec_stream],
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