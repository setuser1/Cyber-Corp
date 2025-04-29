import random

def main():
    constant = 395  # Example prime number, should be much larger in real scenarios
    pubkey = random.randint(500, 1000)
    privkey = random.randint(500, 1000)

    keymsg1 = pubkey*privkey1*constant # send this to other participent
    print(keymsg1)

    othermsg = int(input("Enter key msg from other participent: ")
    complete = othermsg*privkey*constant

    secret = complete
# If both computed secrets are the same, the key exchange is successful
    return secret

mixkey = main()
print(f'Heres your key: {mixkey}')
