import base64, hashlib #import thư viện base64 (từ binary thành text), hash là hàm băm của thư viện có 
from pathlib import Path #sử dụng để xử lý đường dẫn file 
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
#thư viện mã hóa rsa -> tạo public và private key , hash -> dùng SHA-256 trong hash signature, pading dùng RSA-PSS và serialization tạo file 
def canonical_transaction_data(sender, receiver, amount, timestamp, tx_id):
    return f'{sender}|{receiver}|{amount:.2f}|{timestamp}|{tx_id}'
#tạo chuỗi tượng trưng cho giao dịch

def sha256_hex(data): return hashlib.sha256(data.encode()).hexdigest()

def generate_key_pair(private_path: Path, public_path: Path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    public_path.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

def load_private_key(path): return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
def load_public_key(path): return serialization.load_pem_public_key(Path(path).read_bytes())

def sign_data(data, private_key):
    sig = private_key.sign(data.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return base64.b64encode(sig).decode()

def verify_signature(data, signature_b64, public_key):
    try:
        public_key.verify(base64.b64decode(signature_b64), data.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return True
    except Exception: return False
