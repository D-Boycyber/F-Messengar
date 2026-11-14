from flask import Flask, render_template, request

app = Flask(__name__)

def caesar_encrypt(text, shift):
    encrypted = ""
    for char in text:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            encrypted += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            encrypted += char
    return encrypted

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        try:
            shift = int(request.form.get('shift', 3))
        except ValueError:
            shift = 3
        
        if not message:
            return render_template('index.html', error="Please enter a message to encrypt.")
        
        # Encrypt the message directly
        encrypted_msg = caesar_encrypt(message, shift)
        
        return render_template('index.html', encrypted=encrypted_msg, shift=shift)
        
    return render_template('index.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_page():
    if request.method == 'POST':
        ciphertext = request.form.get('ciphertext', '').strip()
        try:
            shift = int(request.form.get('shift', 3))
        except ValueError:
            shift = 3
            
        if not ciphertext:
            return render_template('view.html', error="Please enter an encrypted message.")
            
        decrypted_msg = caesar_decrypt(ciphertext, shift)
        return render_template('view.html', decrypted=decrypted_msg)
        
    return render_template('view.html')

if __name__ == '__main__':
    app.run(debug=True)
