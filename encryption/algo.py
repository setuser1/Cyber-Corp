import random
from typing import List, Union

# Your exact original character list
characters: List[str] = [
    # Uppercase letters
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',

    # Lowercase letters
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',

    # Digits
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',

    # Basic specials
    '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
    ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',
]

def encode(text: str, mixkey: Union[str, int]) -> str:
    """
    Shuffle-encode `text` using your exact `mixkey` with an isolated RNG.
    """
    rng = random.Random(mixkey)        # seed RNG directly with mixkey
    shuffled = characters[:]           # copy your exact list
    rng.shuffle(shuffled)              # shuffle in isolation

    # build forward map and apply
    enc_map = { orig: sub for orig, sub in zip(characters, shuffled) }
    return ''.join(enc_map.get(c, c) for c in text)

def decode(encrypted_text: str, mixkey: Union[str, int]) -> str:
    """
    Reverse the shuffle using the same `mixkey`.
    """
    rng = random.Random(mixkey)
    shuffled = characters[:]
    rng.shuffle(shuffled)

    # build reverse map and apply
    dec_map = { sub: orig for orig, sub in zip(characters, shuffled) }
    return ''.join(dec_map.get(c, c) for c in encrypted_text)
