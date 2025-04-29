import random

def main():
    # Use a large prime and a base (primitive root mod p)
    prime = 395  # Example large prime
    base = random.randint(1,15)        # Base (generator)

    privkey1 = random.randint(1000, 2000)
    privkey2 = random.randint(1000, 2000)

    pubkey = pow(base, privkey1, prime) * random.randint(1,15)

    # Exchange public keys and compute shared secret
    complete1 = pow(pubkey, privkey1, prime)
    complete2 = pow(pubkey, privkey2, prime)

    return complete1 if complete1 == complete2 else None
mixkey = main()
print(mixkey)

# working exchange
