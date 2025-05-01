import algo

options = str(input("Encrypt or Decrypt? (e/d): "))
match options:
    case "decrypt":
        print("Decrypting...")
        # Decrypt the message using the shared key
        recieve = str(input("Enter the message to decrypt: "))
        decrypted_message = algo.decrypt_message(recieve)
        print("Decrypted message:", decrypted_message)
    case "encrypt":
        print("Encrypting...")
        # Encrypt the message using the shared key
        message = str(input("Enter the message to encrypt: "))
        encrypted_message = algo.encrypt_message(message)
        print("Encrypted message:", encrypted_message)
    case _:
        print("Invalid option. Please choose 'e' or 'd'.")
        exit(1)
