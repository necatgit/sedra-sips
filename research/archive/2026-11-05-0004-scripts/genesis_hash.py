"""Recompute Kaspa-family genesis hashes from their fields, following rusty-kaspa v1.0.1
consensus/core/src/hashing/{header,tx,mod}.rs and crypto/merkle/src/lib.rs.
Pure stdlib (hashlib.blake2b keyed). No network, no node."""
import hashlib, struct

def H(key):
    return hashlib.blake2b(digest_size=32, key=key)

def le16(x): return struct.pack('<H', x)
def le32(x): return struct.pack('<I', x)
def le64(x): return struct.pack('<Q', x)
def var_bytes(b): return le64(len(b)) + b

EMPTY_MUHASH = bytes([0x54, 0x4e, 0xb3, 0x14, 0x2c, 0x0, 0xf, 0xa, 0xd2, 0xc7, 0x6a, 0xc4, 0x1f, 0x42, 0x22, 0xab,
                      0xba, 0xba, 0xbe, 0xd8, 0x30, 0xee, 0xaf, 0xee, 0x4b, 0x6d, 0xc5, 0x6b, 0x52, 0xd5, 0xca, 0xc0])
COINBASE_SUBNET = bytes([1] + [0] * 19)
ZERO = bytes(32)

def coinbase_tx_hash(payload):
    h = H(b"TransactionHash")
    h.update(le16(0) + le64(0))          # version 0, 0 inputs
    h.update(le64(0))                    # 0 outputs
    h.update(le64(0) + COINBASE_SUBNET + le64(0) + var_bytes(payload))  # locktime, subnet, gas, payload
    return h.digest()

def header_hash(merkle, ts, bits, nonce, daa, utxo=EMPTY_MUHASH):
    h = H(b"BlockHash")
    h.update(le16(0) + le64(0))          # version 0, 0 parent levels
    h.update(merkle + ZERO + utxo)       # hash_merkle_root, accepted_id_merkle_root, utxo_commitment
    h.update(le64(ts) + le32(bits) + le64(nonce) + le64(daa) + le64(0))  # ts, bits, nonce, daa, blue_score
    h.update(var_bytes(b""))             # blue_work 0 -> empty big-endian bytes
    h.update(ZERO)                       # pruning_point
    return h.digest()

def payload(tail):
    return le64(0) + bytes([0x00, 0xE1, 0xF5, 0x05, 0, 0, 0, 0]) + bytes([0, 0, 0x01, 0x00]) + tail

cases = {
    # kaspad v0.12.15 domain/dagconfig/genesis.go devnet (control case for this script)
    "kaspa-devnet (control)": (payload(b"kaspa-devnet"), 0x11e9db49828, 525264379, 0x48e5e, 0,
                               "b313870a32c704bdf1214a3b270cc475d942c2092d379bc8700ab043319ef846",
                               "58abf20321d70716162b6bf8d9f589ca33ae6e32b3b19abb7fa65d1141a3f94d"),
    # sedrad v2.0.0 domain/dagconfig/genesis.go mainnet
    "sedra-mainnet": (payload(b"sedra-mainnet"), 0x14d2bd72185, 525264379, 0x1a14e, 0,
                      "7c380ae690f9eaa64f300451d5e466371113c38b96ed96fe3f1e934869355ffa",
                      "0a654355c1d58bd4abd9bdcc2e52f1bd565864e8a16ce0377b48ecc64db54b27"),
}

for name, (pl, ts, bits, nonce, daa, exp_hash, exp_merkle) in cases.items():
    m = coinbase_tx_hash(pl)
    hh = header_hash(m, ts, bits, nonce, daa)
    print(f"{name}: merkle={m.hex()} match={m.hex()==exp_merkle} | hash={hh.hex()} match={hh.hex()==exp_hash}")
