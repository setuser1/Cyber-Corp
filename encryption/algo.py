import random

characters = [
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

import random

characters = [
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

def encode(text, mixkey):
    random.seed(mixkey)
    shuffled_characters = characters.copy()
    random.shuffle(shuffled_characters)
    
    # Create a mapping dictionary for encoding
    encode_map = {original: shuffled for original, shuffled in zip(characters, shuffled_characters)}
    
    encrypted_text = []
    for char in text:
        # XOR step
        xor_char = chr(ord(char) ^ mixkey)
        encrypted_text.append(encode_map.get(xor_char, xor_char))  # Use the map, or leave unsupported characters unchanged
    
    return ''.join(encrypted_text)

def decode(encrypted_text, mixkey):
    random.seed(mixkey)
    shuffled_characters = characters.copy()
    random.shuffle(shuffled_characters)
    
    # Create a mapping dictionary for decoding
    decode_map = {shuffled: original for original, shuffled in zip(characters, shuffled_characters)}
    
    decrypted_text = []
    for char in encrypted_text:
        # Reverse XOR step
        decoded_char = decode_map.get(char, char)  # Use the map, or leave unsupported characters unchanged
        original_char = chr(ord(decoded_char) ^ mixkey)
        decrypted_text.append(original_char)
    
    return ''.join(decrypted_text)
    
    decrypted_text = []
    for char in encrypted_text:
        decrypted_text.append(decode_map.get(char, char))  # Use the map, or leave unsupported characters unchanged
    
    return ''.join(decrypted_text)
