import argparse
from mnemonic import Mnemonic
from colorama import Fore, Style, init
import bip32utils

def ask_for_words():
    words = []
    for i in range(1, 13):
        word = input(f"Enter word {i} (or press Enter to bruteforce this word): ").strip()
        words.append(word if word else None)
    return words

def load_wordlist():
    mnemo = Mnemonic("english")
    return mnemo.wordlist

def is_valid_mnemonic(mnemonic):
    mnemo = Mnemonic("english")
    return mnemo.check(mnemonic)

def derive_address(mnemonic):
    seed = Mnemonic.to_seed(mnemonic)
    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)
    return bip32_child_key_obj.Address()

def recover_mnemonic(derived_address, words, wordlist):
    init(autoreset=True)
    missing_indices = [i for i, word in enumerate(words) if word is None]
    total_combinations = len(wordlist) ** len(missing_indices)
    checked_combinations = 0

    def recursive_brute_force(index=0):
        nonlocal checked_combinations
        if index == len(missing_indices):
            checked_combinations += 1
            mnemonic = ' '.join(words)
            print(Fore.YELLOW + f"Trying mnemonic: {mnemonic} ({checked_combinations}/{total_combinations})")
            if is_valid_mnemonic(mnemonic):
                generated_address = derive_address(mnemonic)
                if generated_address == derived_address:
                    print(Fore.GREEN + f"Valid mnemonic found: {mnemonic}")
                    print(Fore.GREEN + f"Derived address: {generated_address}")
                    return True
            return False
        for word in wordlist:
            words[missing_indices[index]] = word
            if recursive_brute_force(index + 1):
                return True
        return False

    if not recursive_brute_force():
        print(Fore.RED + "No valid mnemonic found.")

def main():
    parser = argparse.ArgumentParser(description="Recover mnemonic words with brute-forcing missing words.")
    parser.add_argument("derived_address", type=str, help="The derived address to be used.")

    args = parser.parse_args()

    words = ask_for_words()
    wordlist = load_wordlist()

    recover_mnemonic(args.derived_address, words, wordlist)

if __name__ == '__main__':
    main()
