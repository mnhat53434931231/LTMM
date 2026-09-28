
from database import init_db
from services import *

def menu(user):
    while True:
        print(f'\n===== E-WALLET | {user} =====\n1. Xem số dư\n2. Nạp tiền\n3. Chuyển tiền\n4. Lịch sử\n5. Verify giao dịch\n6. [DEMO] Tamper amount\n0. Đăng xuất')
        ch=input('Chọn: ').strip()
        if ch=='1': print(f'Số dư: {get_balance(user):,.2f} VNĐ')
        elif ch=='2':
            try: ok,msg=deposit(user,float(input('Số tiền: '))); print(('✓ ' if ok else '✗ ')+msg)
            except ValueError: print('Số tiền không hợp lệ.')
        elif ch=='3':
            try:
                ok,msg,tx=transfer(user,input('Người nhận: ').strip(),float(input('Số tiền: '))); print(('✓ ' if ok else '✗ ')+msg); tx and print('Transaction ID:',tx)
            except ValueError: print('Số tiền không hợp lệ.')
        elif ch=='4':
            rows=list_transactions(user); print('\n'.join(f"{x['id']} | {x['sender_username']} -> {x['receiver_username']} | {x['amount']:,.2f} | {x['timestamp']}" for x in rows) or 'Chưa có giao dịch.')
        elif ch=='5':
            ok,msg,d=verify_transaction(input('Transaction ID: ').strip()); print(('✓ ' if ok else '✗ ')+msg); d and print(d)
        elif ch=='6':
            try:
                tx=input('Transaction ID: ').strip(); amount=float(input('Amount mới: ')); print('⚠ Đã tamper.' if tamper_transaction(tx,amount) else 'Không tìm thấy giao dịch.')
            except ValueError: print('Số tiền không hợp lệ.')
        elif ch=='0': break

def cli_main():
    init_db()
    while True:
        print('\n=== E-WALLET CRYPTO ===\n1. Đăng ký\n2. Đăng nhập\n0. Thoát')
        ch=input('Chọn: ').strip()
        if ch=='1':
            ok,msg=register(input('Username: '),input('Password: ')); print(('✓ ' if ok else '✗ ')+msg)
        elif ch=='2':
            u=input('Username: '); p=input('Password: '); row=login(u,p); print('✓ Đăng nhập.' if row else '✗ Sai thông tin.'); row and menu(row['username'])
        elif ch=='0': break

def main():
    import sys
    init_db()
    if '--cli' in sys.argv:
        cli_main()
    else:
        from frontend import run_app
        run_app()

if __name__=='__main__': main()

