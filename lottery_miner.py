# Bitcoin Lottery Miner (Educational Simulator)
# Copyright (C) 2025 Volkan Kücükbudak
# Licensed under the GNU General Public License v3.0 (GPLv3)
"""Educational Bitcoin-style miner.

Optimizations compared to the naive version:
  * SHA-256 midstate: the first 64 header bytes never change, so they are
    hashed once and the state is copied for every nonce (like real miners).
  * Real target comparison (hash < target) instead of hex string checks.
  * Correct compact "bits" field in the header, decoded back to the target.
  * Multiprocessing: the nonce space is split across all CPU cores.
  * Time/UI checks only once per batch, never per hash.
  * Generic Merkle tree (odd levels duplicate the last hash, like Bitcoin).
  * Every found block is re-verified from scratch.
"""

import argparse
import hashlib
import multiprocessing as mp
import queue
import struct
import time

from tqdm import tqdm

# ================= DEFAULTS (override via CLI) =================
DIFFICULTY = 6  # Leading hex zeros: 5 = seconds, 6 = ~30s, 7 = minutes
LOTTERY_DURATION = 60  # Seconds the mining round runs
WALLET_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
BLOCK_REWARD = 3.125  # BTC per block after the 2024 halving
# ===============================================================

BATCH = 20_000  # Hashes per worker between stop/progress checks
MAX_NONCE = 0xFFFFFFFF
_PACK_NONCE = struct.Struct("<I").pack


# ------------------------- Bitcoin primitives -------------------------
def double_sha256(data: bytes) -> bytes:
    """Standard Bitcoin hash: SHA256(SHA256(data))."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def merkle_root(tx_hashes: list[bytes]) -> bytes:
    """Builds a Merkle root from transaction hashes (any number >= 1)."""
    level = tx_hashes
    while len(level) > 1:
        if len(level) % 2:  # Bitcoin duplicates the last hash on odd levels
            level = level + [level[-1]]
        level = [
            double_sha256(level[i] + level[i + 1])
            for i in range(0, len(level), 2)
        ]
    return level[0]


def build_merkle_root(wallet_address: str) -> bytes:
    """Coinbase TX (reward -> your wallet) + dummy TXs -> Merkle root.

    Note: the TXs are plain strings, not real serialized transactions.
    """
    txs = [
        f"Coinbase: {BLOCK_REWARD} BTC -> {wallet_address}",
        "Alice sends 0.5 BTC to Bob",
        "Charlie sends 1.2 BTC to Dave",
        "Eve sends 0.1 BTC to Mallory",
    ]
    return merkle_root([double_sha256(t.encode()) for t in txs])


def target_to_bits(target: int) -> int:
    """Encodes a 256-bit target into Bitcoin's compact 'bits' format."""
    size = (target.bit_length() + 7) // 8
    if size <= 3:
        compact = target << (8 * (3 - size))
    else:
        compact = target >> (8 * (size - 3))
    if compact & 0x00800000:  # sign bit must stay clear
        compact >>= 8
        size += 1
    return (size << 24) | compact


def bits_to_target(bits: int) -> int:
    """Decodes compact 'bits' back to the full target."""
    size, compact = bits >> 24, bits & 0x007FFFFF
    if size <= 3:
        return compact >> (8 * (3 - size))
    return compact << (8 * (size - 3))


def difficulty_to_bits(difficulty: int) -> int:
    """N leading hex zeros == hash < 2^(256 - 4N)."""
    return target_to_bits(1 << (256 - 4 * difficulty))


def verify_block(static_header: bytes, nonce: int, bits: int) -> str:
    """Recomputes the hash from scratch. Raises if it is not a valid block."""
    digest = double_sha256(static_header + _PACK_NONCE(nonce))
    if int.from_bytes(digest, "little") >= bits_to_target(bits):
        raise ValueError("Block verification failed!")
    return digest[::-1].hex()  # display order is big-endian


# ----------------------------- Mining core -----------------------------
def worker(static_header, target, start, end, stop, counter, results):
    """Searches nonces in [start, end). Runs in its own process."""
    # Midstate: first 64 bytes are constant -> hash them only once.
    midstate = hashlib.sha256(static_header[:64])
    tail = static_header[64:]  # remaining 12 header bytes (before the nonce)
    sha256 = hashlib.sha256
    from_bytes = int.from_bytes

    for batch_start in range(start, end, BATCH):
        if stop.is_set():
            return
        batch_end = min(batch_start + BATCH, end)
        for nonce in range(batch_start, batch_end):
            h = midstate.copy()
            h.update(tail + _PACK_NONCE(nonce))
            digest = sha256(h.digest()).digest()
            if from_bytes(digest, "little") < target:
                with counter.get_lock():
                    counter.value += nonce - batch_start + 1
                results.put(nonce)
                stop.set()
                return
        with counter.get_lock():
            counter.value += batch_end - batch_start


def benchmark(static_header: bytes, seconds: float = 0.3) -> float:
    """Single-core hashrate estimate (H/s) using the same midstate trick."""
    midstate = hashlib.sha256(static_header[:64])
    tail = static_header[64:]
    sha256 = hashlib.sha256
    n, t0 = 0, time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        h = midstate.copy()
        h.update(tail + _PACK_NONCE(n))
        sha256(h.digest()).digest()
        n += 1
    return n / (time.perf_counter() - t0)


def print_odds(hashrate: float, difficulty: int) -> None:
    expected = 16**difficulty
    secs = expected / hashrate if hashrate > 0 else float("inf")
    btc_hashes = 16**19  # real network needs roughly ~19 leading hex zeros
    years = btc_hashes / hashrate / (3600 * 24 * 365) if hashrate else 0
    print(f"📊 --- LOTTERY ODDS (~{hashrate:,.0f} H/s total) ---")
    print(f"🎯 Difficulty {difficulty}: 1 in {expected:,} hashes (~{secs:.1f}s avg)")
    print(f"🌍 Real BTC network (~Diff 19): ~{years:,.0f} years with this script!\n")


def mine_block(difficulty: int, duration: int, wallet: str, workers: int) -> None:
    print(f"\n🚀 Bitcoin Lottery Miner started! (Difficulty: {difficulty})")
    print(f"💳 Wallet : {wallet} (baked into Coinbase TX & Merkle Root)")
    print(f"⏱️  Duration: {duration}s | 🧵 Workers: {workers}\n")

    version = 1
    prev_block_hash = bytes(32)
    root = build_merkle_root(wallet)
    timestamp = int(time.time())
    bits = difficulty_to_bits(difficulty)
    target = bits_to_target(bits)

    # 76 bytes; the 4-byte nonce makes the 80-byte Bitcoin header.
    static_header = struct.pack("<I32s32sII", version, prev_block_hash, root, timestamp, bits)

    print_odds(benchmark(static_header) * workers, difficulty)

    stop = mp.Event()
    counter = mp.Value("Q", 0)
    results = mp.Queue()
    chunk = (MAX_NONCE + 1) // workers
    procs = [
        mp.Process(
            target=worker,
            args=(static_header, target, i * chunk, (i + 1) * chunk, stop, counter, results),
            daemon=True,
        )
        for i in range(workers)
    ]

    start = time.perf_counter()
    for p in procs:
        p.start()

    with tqdm(
        total=duration,
        desc="⛏️  Mining",
        unit="s",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}s [{elapsed}<{remaining}, {postfix}]",
    ) as pbar:
        while not stop.is_set() and time.perf_counter() - start < duration:
            time.sleep(0.2)
            elapsed = time.perf_counter() - start
            pbar.n = min(int(elapsed), duration)
            pbar.set_postfix_str(f"{counter.value / elapsed:,.0f} H/s | {counter.value:,} hashes")
            pbar.refresh()

    stop.set()
    elapsed = time.perf_counter() - start
    for p in procs:
        p.join(timeout=2)
        if p.is_alive():
            p.terminate()

    try:
        nonce = results.get(timeout=1)
    except queue.Empty:
        nonce = None

    total = counter.value
    rate = total / elapsed if elapsed > 0 else 0

    if nonce is None:
        print(f"\n\n❌ No block found in {duration}s ({total:,} hashes at ~{rate:,.0f} H/s).")
        print("💡 Tip: run again, raise the duration or lower the difficulty.")
        return

    block_hash = verify_block(static_header, nonce, bits)  # raises if invalid
    print("\n\n🎉 WINNER! Valid Block found (verified)!")
    print(f"🔑 Block Hash   : {block_hash}")
    print(f"🌳 Merkle Root  : {root.hex()}")
    print(f"🧮 Bits         : {bits:#010x}")
    print(f"🎲 Winning Nonce: {nonce:,}")
    print(f"⚡ Avg Hashrate : {rate:,.0f} H/s ({total:,} hashes)")
    print(f"⏱️  Time taken   : {elapsed:.2f} seconds")
    print(f"💰 Reward       : {BLOCK_REWARD} BTC sent to {wallet} (simulated)!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bitcoin Lottery Miner (educational)")
    parser.add_argument("-d", "--difficulty", type=int, default=DIFFICULTY)
    parser.add_argument("-t", "--time", type=int, default=LOTTERY_DURATION, help="seconds")
    parser.add_argument("-w", "--wallet", default=WALLET_ADDRESS)
    parser.add_argument("-j", "--workers", type=int, default=mp.cpu_count())
    args = parser.parse_args()
    if not 1 <= args.difficulty <= 63:
        parser.error("difficulty must be between 1 and 63")
    mine_block(args.difficulty, args.time, args.wallet, max(1, args.workers))


if __name__ == "__main__":
    main()
