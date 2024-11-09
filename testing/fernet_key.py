from cryptography.fernet import Fernet

# Generate a new Fernet key
key = Fernet.generate_key()

# Save the key to a file
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Fernet key generated and stored in 'secret.key'.")
