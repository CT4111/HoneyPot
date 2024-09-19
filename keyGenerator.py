import paramiko

# Generate RSA key
key = paramiko.RSAKey.generate(2048)

# Save private key
private_key_file = 'private.key'
with open(private_key_file, 'w') as private_key:
    key.write_private_key(private_key)

# Save public key
public_key_file = 'public.key'
with open(public_key_file, 'w') as public_key:
    public_key.write(f"{key.get_name()} {key.get_base64()}")