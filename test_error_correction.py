from qrgen.reedsolomon import QRErrorCorrection, get_codeword_capacity
from qrgen import ByteEncoder, BitStream, interleave_blocks


def test_error_correction():
    # Create a version 1-Q QR code error correction encoder
    qr_ec = QRErrorCorrection(version=7, ec_level='H')
    
    # Sample data (13 bytes for version 1-Q)
    # test_data = [64, 116, 102, 116, 102, 102, 102, 102, 102, 102, 102, 102, 102]
    test_string = 'Hello World! This is just here for padding. Hi.'
    encoder = ByteEncoder(test_string)
    test_data = encoder.encode(qr_version=7)
    capacity = get_codeword_capacity(7, 'H')
    test_data.pad_to_length(capacity*8)
    
    # Encode the data
    data_blocks, ec_blocks = qr_ec.encode_data(test_data.buffer)
    data_final = interleave_blocks(data_blocks)
    ec_final = interleave_blocks(ec_blocks)
    data_stream = BitStream.from_int8_array(data_final)
    ec_stream = BitStream.from_int8_array(ec_final)
    
    print("Data blocks:", data_stream)
    print("EC blocks:", ec_stream)


if __name__ == "__main__":
    test_error_correction()
    # print(get_codeword_capacity(7, 'H'))