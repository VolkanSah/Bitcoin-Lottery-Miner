# Bitcoin Lottery Miner

A small Python toy that mines a fake Bitcoin block on your CPU. Pure fun, built for learning how proof-of-work actually works.

**No real coins, no network, no pool. Nothing gets sent anywhere.** If you "win", you get a hash on your screen and a warm fuzzy feeling.

## What it does

- Builds a real 80-byte Bitcoin block header (version, prev hash, Merkle root, timestamp, bits, nonce)
- Puts a Coinbase TX with your wallet address plus a few dummy TXs into a Merkle tree
- Hashes with double SHA-256, same as Bitcoin
- Checks `hash < target` like a real miner, with a proper compact `bits` field
- Uses all your CPU cores
- Re-verifies every block it finds from scratch
- Shows your odds before it starts, so you know what you're getting into

## Quick start

```bash
git clone https://github.com/VolkanSah/Bitcoin-Lottery-Miner
cd Bitcoin-Lottery-Miner
pip install tqdm
python lottery_miner.py
```

Needs Python 3.9+ (and `tqdm` for the progress bar, that's it).

## Options

```bash
python lottery_miner.py -d 6 -t 120 -j 4 -w <your-address>
```

| Flag | What it does | Default |
|------|--------------|---------|
| `-d`, `--difficulty` | Leading hex zeros the hash needs | `6` |
| `-t`, `--time` | Max seconds to mine | `60` |
| `-j`, `--workers` | CPU processes | all cores |
| `-w`, `--wallet` | Address baked into the Coinbase TX | example address |

Rough feeling for difficulty (depends on your CPU):

- `5` is done in a second or so
- `6` takes around half a minute
- `7` takes minutes, so give it more time with `-t`

Each extra zero makes it 16x harder.

## Example run

```text
🚀 Bitcoin Lottery Miner started! (Difficulty: 5)
💳 Wallet : 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (baked into Coinbase TX & Merkle Root)
⏱️  Duration: 30s | 🧵 Workers: 2

📊 --- LOTTERY ODDS (~2,798,944 H/s total) ---
🎯 Difficulty 5: 1 in 1,048,576 hashes (~0.4s avg)
🌍 Real BTC network (~Diff 19): ~856,010,131 years with this script!

🎉 WINNER! Valid Block found (verified)!
🔑 Block Hash   : 00000be0e85204a88f76df41d34dca1d4b9b8253831aed2ed19d6b51be5a7ddd
🎲 Winning Nonce: 153,301
```

Your numbers will differ, it's a lottery after all.

## How it works

1. Build the 76 static header bytes (everything except the nonce).
2. Hash the first 64 of those once and keep the state (the "midstate"). Every nonce only needs the rest, which is a trick real miners use too.
3. Each worker gets its own slice of the 32-bit nonce space and tries them one by one.
4. Hash is double SHA-256, read as a little-endian number, compared against the target.
5. First worker to find one stops the others. The block gets verified again from zero.

## Is this real mining? 

Nope, and it can't win real Bitcoin even if you get lucky. The block you find is only valid by *our* rules:

- It doesn't point to the real chain tip
- The target is way easier than the real network's
- The Coinbase TX is just a string, not a properly serialized transaction

The real network needs more than 10^23 hashes per block on average. This script does a few hundred thousand per second. Do the math, or let the script do it for you, it prints it on start.

For real Regtest fun (your own local node where mining is instant), that's a good next step: grab a template with `getblocktemplate`, build the block, `submitblock`. Not in here yet.

## Safety note

You only ever need a **public** address. Never put a private key or seed phrase into any script you found on the internet. Not here, not anywhere.

## Ideas 

- Real serialized Coinbase TX and address validation
- Save found blocks as JSON
- Regtest mode with a local `bitcoind`
- Tests against the genesis block

PRs and ideas welcome. Break it, improve it, make it faster.

## License

AGPL3, see [LICENSE](LICENSE).

Made by [Volkan Kücükbudak](https://github.com/volkansah)
