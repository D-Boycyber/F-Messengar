from flask import Flask, render_template, request, redirect, url_for
import uuid

app = Flask(__name__)

# Temporary in-memory database to store secrets
secrets_db = {}

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
        message = request.form.get('message', '')
        shift_val = request.form.get('shift', 3)
        shift = int(shift_val) if shift_val else 3
        
        if not message:
            return render_template('index.html', error="Please enter a message to encrypt.")
        
        # Encrypt the message
        encrypted_msg = caesar_encrypt(message, shift)
        
        # Generate a unique secure token ID
        secret_id = str(uuid.uuid4())[:8]
        
        # Save it to our database
        secrets_db[secret_id] = encrypted_msg
        
        return render_template('index.html', encrypted=encrypted_msg, secret_id=secret_id, shift=shift)
        
    return render_template('index.html')

@app.route('/view/<secret_id>', methods=['GET', 'POST'])
def view_secret(secret_id):
    if secret_id not in secrets_db:
        return render_template('view.html', error="This secret message has already been viewed and destroyed, or it never existed!")
    
    if request.method == 'POST':
        shift_val = request.form.get('shift', 3)
        shift = int(shift_val) if shift_val else 3
        encrypted_msg = secrets_db[secret_id]
        
        # THE ONE-TIME TRICK: Delete it immediately upon decryption attempt
        del secrets_db[secret_id]
        
        decrypted_msg = caesar_decrypt(encrypted_msg, shift)
        return render_template('view.html', decrypted=decrypted_msg)
        
    return render_template('view.html', secret_id=secret_id)

if __name__ == '__main__':
    app.run(debug=True)
