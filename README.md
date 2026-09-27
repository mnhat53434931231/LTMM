# E-Wallet Crypto Demo

## Chạy
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

## Luồng mật mã
Transaction -> SHA-256 -> RSA-PSS signature -> lưu DB -> Public Key verify.

Có chức năng DEMO tamper amount: sửa amount trong DB rồi verify để thấy INVALID.

> Đây là đồ án giả lập. Password đang hash SHA-256 để minh họa; hệ thống thực tế nên dùng Argon2id/bcrypt và bảo vệ private key bằng cơ chế quản lý khóa an toàn.
