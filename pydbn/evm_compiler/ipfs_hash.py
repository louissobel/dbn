import hashlib

MAX_SINGLE_CHUNK_SIZE = 262144


def get_hash_of_ipfs_node(filedata):
    """
    returns the SHA2-256 hash of what a single-node file
    in IPFS would be for the given data

    This involves hand-serializing two protobufs:

    NodeData:
     - uint64 1: NodeType (hardcoded to 2)
     - bytes  2: Data
     - uint64 3: FileLength

    Node:
     - bytes 1: Data

    We hand serialize rather than use protobuf proper because
      - a) I don't feel like taking on a dependency in the lambda
      - b) I guess that's ^ really it...
    """

    if not isinstance(filedata, bytes):
    	raise TypeError("data must be bytes, got %r" % type(filedata))

    if len(filedata) >= MAX_SINGLE_CHUNK_SIZE:
        raise ValueError("file too big to fit in a single CID0 ipfs block: %d" % len(data))

    node_data_pieces = [
        b'\x08',  # tag 1<<3
        b'\x02',  # type: file

        b'\x12',  # tag 2<<3 | length-encoded
        _varint128(len(filedata)),
        filedata,

        b'\x18',  # tag 3
        _varint128(len(filedata)),
    ]

    node_data = b''.join(node_data_pieces)

    node_pieces = [
        b'\x0A',  # tag 1<<3 | length-encoded
        _varint128(len(node_data)),
        node_data,
    ]
    node = b''.join(node_pieces)

    return hashlib.sha256(node).hexdigest()


def _varint128(i):
    """
    How protobuf encodes uint64s and lengths of bytes
    """
    out = []

    while i > 0:
        least = i & 0x7F
        i = i >> 7

        if i > 0:
            least |= 0b10000000
        out.append(least.to_bytes(1, byteorder='big'))

    return b''.join(out)
