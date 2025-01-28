# Bitcoin Lottery Miner
### your chance 1: 45.000.000.000.000.000.000.000 (difficulty on 28.01.2025) for 6,25 BTC

Welcome to the **Bitcoin Lottery Miner**, a unique simulation and mining tool for both fun and educational purposes! This project offers a fresh take on "lottery mining," where the challenge is to find a valid Bitcoin block with a specific difficulty target, much like the real Bitcoin mining process.

## 🚀 Features

- **Custom Block Generation**: Generates rudimentary Bitcoin blocks in Python, including fields like `version`, `previous_block_hash`, `merkle_root`, `timestamp`, and `nonce`.
- **Difficulty-Based Mining**: Simulates the Proof-of-Work process with customizable difficulty.
- **Progress Visualization**: Includes a progress bar for real-time mining feedback.
- **Standalone Mining**: No external miners required; everything runs directly in Python.
- **Fun and Learning**: Perfect for understanding the mechanics of Bitcoin mining and experimenting with block creation.

## 🌟 What Makes This Project Unique?

Unlike other "lottery miners" that rely on external mining tools or pools, this project:

1. **Runs Entirely in Python**: No need for external mining software like `bfgminer`. The script itself handles the entire mining logic.
2. **Standalone Blocks**: Generates and hashes blocks directly in code, simulating the real-world mining process.
3. **Interactive Simulation**: Focuses on learning and having fun while exploring mining concepts.
4. **Simple Yet Expandable**: Provides a solid foundation for further experimentation, like adding real blockchain network interaction or enhancing block structure.

## 📋 Requirements

- Python 3.6 or higher
- [tqdm](https://pypi.org/project/tqdm/) (for the progress bar)

Install `tqdm` via pip:
```bash
pip install tqdm
```

## 🛠️ How to Use

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd bitcoin-lottery-miner
   ```
2. Open the script and update the `WALLET_ADDRESS` variable with your Bitcoin wallet address:
   ```python
   WALLET_ADDRESS = "<YourBitcoinAddress>"
   ```
3. Run the script:
   ```bash
   python lottery_miner.py
   ```
4. Choose your difficulty and watch the magic happen! If a valid block is found, the script simulates sending the reward to your wallet address.

## ⚙️ Configuration

You can customize the following parameters in the script:

- **DIFFICULTY**: Number of leading zeros required in the block hash.
- **LOTTERY_DURATION**: Time (in seconds) the mining process runs.
- **WALLET_ADDRESS**: Your Bitcoin wallet address (used for simulation).

## 🔍 Example Output

```text
🚀 Bitcoin Mining started! Difficulty: 10
Wallet Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Duration: 60 seconds

Mining-Progress:  50%|█████████         | 30/60 [00:30<00:30,  1.00s/s]

🎉 WINNER! Block found!
🔑 Hash: 00000000001d3a2b...
📜 Block: {'version': 1, 'previous_block_hash': '000000...', 'merkle_root': '', 'timestamp': 1674873294, 'nonce': 938475}
⏱️ Time: 35.12 seconds
The reward is sent to the wallet address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (simulated).
```

## 🤔 How It Works

1. **Block Creation**: The script generates a simple block template and increments the `nonce` value to attempt different hashes.
2. **Hash Calculation**: Each block's data is hashed using SHA-256.
3. **Proof of Work**: The hash is checked against the difficulty (number of leading zeros).
4. **Reward Simulation**: If a valid hash is found, the block is considered mined, and a reward is simulated.

## 🧠 Learning Focus

This project simplifies the mining process and focuses on:
- Understanding how Bitcoin blocks are created and validated.
- Experimenting with Proof-of-Work concepts.
- Exploring the role of difficulty and randomness in mining.

## 🚧 Future Enhancements

- Add realistic Merkle tree implementation for transactions.
- Integrate with a Bitcoin node to submit mined blocks.
- Visualize mining statistics (e.g., hash rate, attempts).
- Support for multi-threaded mining.

## 🤝 Contributions

Feel free to fork this repository, submit pull requests, or suggest improvements. Let’s make this project even more fun and educational!

## 📜 License

This project is licensed under the GPL3 License. See the LICENSE file for details.

---

Have fun exploring the world of Bitcoin mining! 🚀


