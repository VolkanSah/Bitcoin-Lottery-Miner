# Bitcoin Lottery Miner (Educational Simulator)
# Copyright (C) 2025 Volkan Kücükbudak
# Licensed under the GNU General Public License v3.0 (GPLv3)

import hashlib
import struct
import time
from tqdm import tqdm

# ================= CONFIGURATION =================
DIFFICULTY = (
    6  # Leading hex zeros (5 = easy/seconds, 6 = medium/~30s, 7 = hard/minutes)
)
LOTTERY_DURATION = 60  # Duration of the mining round in seconds
WALLET_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Your Bitcoin address
BLOCK_REWARD = 3.125  # Current BTC reward after the 2024 halving
# =================================================


def double_sha256(data: bytes) -> bytes:
  """Performs standard Bitcoin Double-SHA256 hashing."""
  return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def build_merkle_root(wallet_address: str) -> bytes:
  """Creates a Coinbase transaction (including your wallet) and combines it

  with dummy transactions to calculate a realistic 32-byte Merkle Root.
  """
  # 1. Coinbase Transaction (mints new Bitcoin to your wallet)
  coinbase_tx = f"Coinbase: {BLOCK_REWARD} BTC -> {wallet_address}".encode(
      "utf-8"
  )
  tx1_hash = double_sha256(coinbase_tx)

  # 2. Dummy Transactions to simulate a block
  tx2_hash = double_sha256(b"Alice sends 0.5 BTC to Bob")
  tx3_hash = double_sha256(b"Charlie sends 1.2 BTC to Dave")
  tx4_hash = double_sha256(b"Eve sends 0.1 BTC to Mallory")

  # Build Merkle Tree (Pairwise hashing)
  branch1 = double_sha256(tx1_hash + tx2_hash)
  branch2 = double_sha256(tx3_hash + tx4_hash)
  merkle_root = double_sha256(branch1 + branch2)

  return merkle_root


def calculate_odds(hashrate: float, difficulty: int):
  """Calculates and prints the mathematical odds of winning."""
  expected_hashes = 16**difficulty
  expected_seconds = expected_hashes / hashrate if hashrate > 0 else 0

  # Real Bitcoin difficulty approx. requires ~19 leading hex zeros
  btc_real_hashes = 16**19
  btc_years = (
      (btc_real_hashes / hashrate) / (60 * 60 * 24 * 365) if hashrate > 0 else 0
  )

  print(f"📊 --- LOTTERY ODDS (at ~{hashrate:,.0f} H/s) ---")
  print(
      f"🎯 Target (Difficulty {difficulty}): 1 in {expected_hashes:,} hashes"
      f" (~{expected_seconds:.1f} sec on average)"
  )
  print(
      "🌍 Real BTC Network (~Diff 19): 1 in ~75 sextillion hashes"
      f" (~{btc_years:,.0f} years with this Python script!)\n"
  )


def mine_block():
  print(f"\n🚀 Bitcoin Lottery Miner started! (Difficulty: {DIFFICULTY})")
  print(
      f"💳 Wallet Address : {WALLET_ADDRESS} (baked into Coinbase TX & Merkle"
      " Root)"
  )
  print(f"⏱️  Max Duration   : {LOTTERY_DURATION} seconds\n")

  # Prepare static block header fields (first 76 bytes of the 80-byte Bitcoin header)
  version = 1
  prev_block_hash = bytes.fromhex("00" * 32)  # 32 bytes dummy previous block
  merkle_root = build_merkle_root(WALLET_ADDRESS)  # 32 bytes Merkle Root
  timestamp = int(time.time())
  bits = DIFFICULTY  # Simplified difficulty target representation

  # Pack the static 76 bytes in Little-Endian format (<I32s32sII)
  static_header = struct.pack(
      "<I32s32sII", version, prev_block_hash, merkle_root, timestamp, bits
  )
  target_prefix = "0" * DIFFICULTY

  # Quick 0.5s benchmark to calculate odds before starting the main bar
  bench_start = time.time()
  bench_hashes = 0
  while time.time() - bench_start < 0.5:
    double_sha256(static_header + struct.pack("<I", bench_hashes))
    bench_hashes += 1
  estimated_hashrate = bench_hashes / (time.time() - bench_start)
  calculate_odds(estimated_hashrate, DIFFICULTY)

  # Start actual mining
  start_time = time.time()
  nonce = 0
  winner = None
  batch_size = 25000  # Only update UI every 25k hashes for maximum performance

  with tqdm(
      total=LOTTERY_DURATION,
      desc="⛏️  Mining",
      unit="s",
      bar_format=(
          "{l_bar}{bar}| {n_fmt}/{total_fmt}s [{elapsed}<{remaining},"
          " {postfix}]"
      ),
  ) as pbar:
    while True:
      # Pack the 4-byte nonce (Total header = 76 + 4 = 80 bytes!)
      header = static_header + struct.pack("<I", nonce)

      # Double-SHA256 and reverse bytes (Bitcoin uses Little-Endian internally, Big-Endian for display)
      block_hash = double_sha256(header)[::-1].hex()

      if block_hash.startswith(target_prefix):
        winner = {
            "nonce": nonce,
            "hash": block_hash,
            "merkle_root": merkle_root.hex(),
            "timestamp": timestamp,
            "found_at": time.time() - start_time,
        }
        break

      nonce += 1

      # Check time and update progress bar in batches
      if nonce % batch_size == 0:
        elapsed = time.time() - start_time
        if elapsed >= LOTTERY_DURATION:
          pbar.n = LOTTERY_DURATION
          pbar.refresh()
          break

        pbar.n = int(elapsed)
        current_hashrate = nonce / elapsed if elapsed > 0 else 0
        pbar.set_postfix_str(
            f"{current_hashrate:,.0f} H/s | Nonce: {nonce:,}"
        )
        pbar.refresh()

      # Prevent 32-bit unsigned integer overflow for nonce (max 4,294,967,295)
      if nonce > 0xFFFFFFFF:
        timestamp = int(time.time())
        static_header = struct.pack(
            "<I32s32sII", version, prev_block_hash, merkle_root, timestamp, bits
        )
        nonce = 0

  # Result output
  total_time = time.time() - start_time
  avg_hashrate = nonce / total_time if total_time > 0 else 0

  if winner:
    print(f"\n\n🎉 WINNER! Valid Block found!")
    print(f"🔑 Block Hash  : {winner['hash']}")
    print(f"🌳 Merkle Root : {winner['merkle_root']}")
    print(f"🎲 Winning Nonce: {winner['nonce']:,}")
    print(
        f"⚡ Avg Hashrate: {avg_hashrate:,.0f} H/s ({nonce:,} total hashes)"
    )
    print(f"⏱️  Time taken  : {winner['found_at']:.2f} seconds")
    print(
        f"💰 Reward      : {BLOCK_REWARD} BTC sent to {WALLET_ADDRESS}"
        " (simulated)!"
    )
  else:
    print(
        f"\n\n❌ No block found in {LOTTERY_DURATION}s ({nonce:,} hashes"
        f" tried at ~{avg_hashrate:,.0f} H/s)."
    )
    print(
        "💡 Tip: Run again to try your luck, increase LOTTERY_DURATION, or"
        " lower DIFFICULTY to 5!"
    )


if __name__ == "__main__":
  mine_block()
