import hashlib, secrets
from datetime import datetime
from config import KEYS_DIR
from crypto import *
from database import fetch_one, fetch_all, get_connection

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()
def get_user(username): return fetch_one('SELECT * FROM users WHERE username=?',(username.strip(),))

def register(username,password):
    username=username.strip()
    if not username or not password: return False,'Username/password không được rỗng.'
    if get_user(username): return False,'Username đã tồn tại.'
    safe=''.join(c if c.isalnum() or c in '_-' else '_' for c in username)
    priv=KEYS_DIR/f'{safe}_private.pem'; pub=KEYS_DIR/f'{safe}_public.pem'; generate_key_pair(priv,pub)
    with get_connection() as c:
        cur=c.execute('INSERT INTO users(username,password_hash,public_key_path,private_key_path,created_at) VALUES(?,?,?,?,?)',(username,hash_password(password),str(pub),str(priv),datetime.now().isoformat(timespec='seconds')))
        c.execute('INSERT INTO wallets(user_id,balance) VALUES(?,0)',(cur.lastrowid,))
    return True,'Đăng ký thành công.'

def login(username,password): return fetch_one('SELECT * FROM users WHERE username=? AND password_hash=?',(username.strip(),hash_password(password)))
def get_balance(username):
    r=fetch_one('SELECT w.balance FROM wallets w JOIN users u ON u.id=w.user_id WHERE u.username=?',(username,)); return float(r['balance']) if r else None

def deposit(username,amount):
    if amount<=0:return False,'Số tiền phải > 0.'
    u=get_user(username)
    if not u:return False,'Không tìm thấy user.'
    with get_connection() as c:c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(amount,u['id']))
    return True,f'Nạp {amount:,.2f} VNĐ thành công.'

def transfer(sender_username,receiver_username,amount):
    if amount<=0:return False,'Số tiền phải > 0.',None
    if sender_username==receiver_username:return False,'Không thể chuyển cho chính mình.',None
    s,r=get_user(sender_username),get_user(receiver_username)
    if not s or not r:return False,'Sender/receiver không tồn tại.',None
    if get_balance(sender_username)<amount:return False,'Số dư không đủ.',None
    tx_id='TX-'+datetime.now().strftime('%Y%m%d%H%M%S')+'-'+secrets.token_hex(3); ts=datetime.now().isoformat(timespec='seconds')
    data=canonical_transaction_data(sender_username,receiver_username,amount,ts,tx_id); h=sha256_hex(data)
    sig=sign_data(data,load_private_key(s['private_key_path']))
    with get_connection() as c:
        c.execute('UPDATE wallets SET balance=balance-? WHERE user_id=?',(amount,s['id'])); c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(amount,r['id']))
        c.execute('INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?)',(tx_id,s['id'],r['id'],amount,ts,h,sig,'SIGNED'))
    return True,f'Giao dịch {tx_id} thành công.',tx_id

def list_transactions(username):
    u=get_user(username)
    if not u:return []
    return fetch_all('''SELECT t.*,su.username sender_username,ru.username receiver_username FROM transactions t JOIN users su ON su.id=t.sender_id JOIN users ru ON ru.id=t.receiver_id WHERE t.sender_id=? OR t.receiver_id=? ORDER BY t.timestamp DESC''',(u['id'],u['id']))

def verify_transaction(tx_id):
    tx = fetch_one('''SELECT t.*, su.username sender_username, ru.username receiver_username, su.public_key_path 
                      FROM transactions t 
                      JOIN users su ON su.id=t.sender_id 
                      JOIN users ru ON ru.id=t.receiver_id 
                      WHERE t.id=?''', (tx_id,))
    if not tx:
        return False, 'Không tìm thấy giao dịch.', None

    data = canonical_transaction_data(tx['sender_username'], tx['receiver_username'], tx['amount'], tx['timestamp'], tx['id'])
    h = sha256_hex(data)
    hash_ok = (h == tx['transaction_hash'])
    sig_ok = verify_signature(data, tx['signature'], load_public_key(tx['public_key_path']))
    valid = hash_ok and sig_ok

    if not valid and tx['status'] != 'TAMPERED':
        # Tìm lại số tiền gốc ban đầu bằng cách đối chiếu với transaction_hash đã lưu
        orig_amount = None
        for test_cents in range(1, 100000000): # Hỗ trợ tới 1.000.000 VNĐ (bước nhảy 0.01)
            amt = test_cents / 100.0
            test_data = canonical_transaction_data(tx['sender_username'], tx['receiver_username'], amt, tx['timestamp'], tx['id'])
            if sha256_hex(test_data) == tx['transaction_hash']:
                orig_amount = amt
                break
        
        # Nếu số tiền lớn hơn phạm vi brute-force, fallback lấy tx['amount']
        rollback_amount = orig_amount if orig_amount is not None else float(tx['amount'])

        with get_connection() as c:
            # 1. Hoàn lại số dư ví về trạng thái cũ
            c.execute('UPDATE wallets SET balance = balance + ? WHERE user_id = ?', (rollback_amount, tx['sender_id']))
            c.execute('UPDATE wallets SET balance = balance - ? WHERE user_id = ?', (rollback_amount, tx['receiver_id']))
            
            # 2. Khôi phục amount về tiền như cũ và cập nhật trạng thái TAMPERED
            c.execute('UPDATE transactions SET amount = ?, status = ? WHERE id = ?', (rollback_amount, 'TAMPERED', tx_id))

    msg = 'VALID: dữ liệu và chữ ký hợp lệ.' if valid else 'INVALID: giao dịch đã bị thay đổi hoặc chữ ký không hợp lệ.'
    details = {
        'stored_hash': tx['transaction_hash'],
        'recalculated_hash': h,
        'hash_ok': hash_ok,
        'signature_ok': sig_ok
    }
    return valid, msg, details

def tamper_transaction(tx_id,new_amount):
    with get_connection() as c:return c.execute('UPDATE transactions SET amount=? WHERE id=?',(new_amount,tx_id)).rowcount>0
