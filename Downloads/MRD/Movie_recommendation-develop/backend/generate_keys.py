"""
Generate secure keys for the application
"""
import secrets

def generate_keys():
    """Generate secure random keys"""
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    
    print("=" * 60)
    print("Generated Secure Keys")
    print("=" * 60)
    print(f"\nSECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret_key}")
    print("\n" + "=" * 60)
    print("\nCopy these values to your .env file!")
    print("=" * 60)
    
    return secret_key, jwt_secret_key

if __name__ == '__main__':
    generate_keys()

