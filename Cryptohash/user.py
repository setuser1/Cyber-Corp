import random

def main():
    # Shared values (agreed ahead of time)
    prime = 397  # Insecurely small, just for demo
    base = random.randint(2, prime - 2)

    # Your private key and public key
    privkey = random.randint(500, 1000)
    pubkey = pow(base, privkey, prime)
    print(pubkey)
    other_pubkey = int(input("Enter their Pubkey: "))

    # Compute the shared secret
    shared_secret = pow(other_pubkey, privkey, prime)*1878426628

    return shared_secret

mixkey = main()
print(mixkey)
# working
