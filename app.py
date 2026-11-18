from flask import Flask, render_template, request, redirect, url_for, session
import uuid

app = Flask(__name__)
app.secret_key = 'super-secret-admin-key-change-this'

# Storage: { secret_id: { 'ciphertext': str, 'shift': int, 'passcode': str, 'expired': bool } }
db = {}

ADMIN_SETTINGS = {
    'passcode': 'admin123'
}

def caesar_encrypt(text, shift):
    encrypted = ""
    for char in text:
        if char.isalpha():
            ascii_offset = ord('a') if char.islower() else ord('A')
            encrypted += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        elif char.isdigit():
            encrypted += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            encrypted += char
    return encrypted

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

@app.route('/', methods=['GET', 'POST'])
def index():
    encrypted_msg = None
    secret_id = None
    shift = 3
    error = None
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        custom_passcode = request.form.get('passcode', '').strip() # Allows letters, symbols, numbers
        try:
            shift = int(request.form.get('shift', 3))
        except ValueError:
            shift = 3
        
        if not message:
            error = "Please enter a message to encrypt."
        else:
            encrypted_msg = caesar_encrypt(message, shift)
            secret_id = str(uuid.uuid4())[:8]
            
            db[secret_id] = {
                'ciphertext': encrypted_msg,
                'shift': shift,
                'passcode': custom_passcode,
                'expired': False
            }
            
    return render_template('index.html', encrypted=encrypted_msg, secret_id=secret_id, shift=shift, error=error)

@app.route('/decrypt/<secret_id>', methods=['GET', 'POST'])
def view_secret(secret_id):
    if secret_id not in db or db[secret_id]['expired']:
        return render_template('view.html', error="This message has already expired, been destroyed, or was revoked by the admin.")
    
    item = db[secret_id]
    error = None
    decrypted_msg = None
    
    if request.method == 'POST':
        entered_passcode = request.form.get('passcode', '').strip()
        entered_ciphertext = request.form.get('ciphertext', '').strip()
        
        # Verify passcode (if set)
        if item['passcode'] and entered_passcode != item['passcode']:
            error = "Incorrect passcode! Access denied."
        # Verify that the pasted ciphertext matches the stored link's ciphertext
        elif entered_ciphertext != item['ciphertext']:
            error = "Incorrect ciphertext pasted! Please paste the exact encrypted message."
        else:
            decrypted_msg = caesar_decrypt(item['ciphertext'], item['shift'])
            item['expired'] = True  # Self-destruct immediately upon successful decrypt
            
    return render_template('view.html', secret_id=secret_id, decrypted=decrypted_msg, error=error, has_passcode=bool(item['passcode']))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        p = request.form.get('admin_pass', '')
        if p == ADMIN_SETTINGS['passcode']:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid Admin Passcode")
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_pass':
            new_p = request.form.get('new_admin_pass', '').strip()
            if new_p:
                ADMIN_SETTINGS['passcode'] = new_p
        elif action == 'delete':
            s_id = request.form.get('secret_id')
            if s_id in db:
                del db[s_id]
                
    return render_template('admin_dashboard.html', db=db, admin_pass=ADMIN_SETTINGS['passcode'])

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
