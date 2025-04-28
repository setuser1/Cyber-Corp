import random

def main():
# Large prime number for modulus
    constant = 395  # Example prime number, should be much larger in real scenarios
    pubkey = random.randint(500, 1000)
    print(pubkey)
    privkey1 = random.randint(500, 1000)
    privkey2 = random.randint(500, 1000)

# Both participants compute their key messages using the public key and their private keys

    keymsg1 = pubkey*privkey1*constant
    keymsg2 = pubkey*privkey2*constant

# Now they exchange and compute the secret
    complete1 = keymsg2*privkey1*constant  # Participant 1 computes complete secret
    complete2 = keymsg1*privkey2*constant  # Participant 2 computes complete secret

    secret = complete1
# If both computed secrets are the same, the key exchange is successful
    return secret if complete1 == complete2 else None