from flask import Flask, render_template, request

app = Flask(__name__)


# Caesar cipher logic for both encrypting and decrypting
def caesar_cipher(text, shift, mode):
  result = ""
  if mode == "decrypt":
    shift = -shift

  for char in text:
    if char.islower():
      new_char = chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
      result += new_char
    elif char.isupper():
      new_char = chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
      result += new_char
    else:
      result += char
  return result


@app.route("/", methods=["GET", "POST"])
def home():
  encrypted_message = ""
  shift_used = 3
  if request.method == "POST":
    message = request.form.get("message", "")
    shift_used = int(request.form.get("shift", 3))
    # Encrypt the message
    encrypted_message = caesar_cipher(message, shift_used, "encrypt")

  return render_template(
      "index.html",
      encrypted_message=encrypted_message,
      shift_used=shift_used,
  )


@app.route("/decrypt", methods=["GET", "POST"])
def decrypt_page():
  decrypted_message = ""
  error_msg = ""
  if request.method == "POST":
    ciphertext = request.form.get("ciphertext", "")
    shift = int(request.form.get("shift", 3))
    try:
      # Decrypt the message using the ciphertext and shift key
      decrypted_message = caesar_cipher(ciphertext, shift, "decrypt")
    except Exception:
      error_msg = "Invalid decryption attempt."

  return render_template(
      "view.html", decrypted_message=decrypted_message, error=error_msg
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)