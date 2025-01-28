# DO NOT STEAL FREE CODE FROM DEVS AND PUT YOUR NAME ON IT! I WILL GET YOU TRUST ME I AM BETTER THAN YOU! AMD IF I GET ,  I WILL F*** YOUR HOLE LIFE!
# Copyright Volkan Kücükbudak

import hashlib
import time
import random
from tqdm import tqdm

# Konfiguration
DIFFICULTY = 10  # Anzahl der führenden Nullen im Hex-Hash (z. B. 10 = 0000000000...)
LOTTERY_DURATION = 60  # Sekunden, wie lange die Lotterie läuft
WALLET_ADDRESS = "<DeineBitcoinAdresse>"  # Hier deine Bitcoin-Adresse eintragen

# Bitcoin-spezifische Konstanten (für eine rudimentäre Blockstruktur)
BLOCK_TEMPLATE = {
    "version": 1,
    "previous_block_hash": "0" * 64,  # Dummy-Wert
    "merkle_root": "",  # Kann später erweitert werden
    "timestamp": int(time.time()),
    "difficulty": DIFFICULTY,
    "nonce": 0,
}

# Funktion zur Generierung eines rudimentären Blocks
def generate_block(nonce):
    block = BLOCK_TEMPLATE.copy()
    block["nonce"] = nonce
    block["timestamp"] = int(time.time())
    return block

# Funktion zur Berechnung des Hashes eines Blocks
def hash_block(block):
    block_string = (
        f"{block['version']}{block['previous_block_hash']}{block['merkle_root']}{block['timestamp']}{block['nonce']}"
    )
    return hashlib.sha256(block_string.encode()).hexdigest()

# Überprüfung, ob der Hash die Bedingungen erfüllt
def is_winner(block_hash):
    return block_hash.startswith("0" * DIFFICULTY)

# Mining-Funktion für den Nutzer
def mine_block():
    print(f"\n🚀 Bitcoin Mining gestartet! Schwierigkeit: {DIFFICULTY}")
    print(f"Wallet-Adresse: {WALLET_ADDRESS}")
    print(f"Dauer: {LOTTERY_DURATION} Sekunden\n")

    start_time = time.time()
    nonce = 0
    winner = None

    with tqdm(total=LOTTERY_DURATION, desc="Mining-Fortschritt", unit="s") as pbar:
        while time.time() - start_time < LOTTERY_DURATION:
            block = generate_block(nonce)
            block_hash = hash_block(block)

            if is_winner(block_hash):
                winner = {
                    "block": block,
                    "hash": block_hash,
                    "found_at": time.time() - start_time
                }
                break

            nonce += 1
            pbar.update(min(1, LOTTERY_DURATION - (time.time() - start_time)))

    if winner:
        print(f"\n🎉 GEWINNER! Block gefunden!")
        print(f"🔑 Hash: {winner['hash']}")
        print(f"📜 Block: {winner['block']}")
        print(f"⏱️ Zeit: {winner['found_at']:.2f} Sekunden")
        print(f"Die Belohnung wird an die Wallet-Adresse {WALLET_ADDRESS} geschickt (simuliert).")
    else:
        print("\n❌ Kein Gewinner in dieser Runde. Erhöhe die Laufzeit oder verringere die Difficulty!")

if __name__ == "__main__":
    print("Starte Mining...")
    mine_block()
