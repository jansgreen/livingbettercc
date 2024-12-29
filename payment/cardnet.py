import requests
from django.conf import settings
# Ejemplo de función para procesar pagos
def process_payment(card_number, exp_date, cvv, amount):
    api_url = "https://api.cardnet.com/v1/payments"  # URL real de CardNet
    api_key = settings.SECRET_KEY_CARDNET  # Obtén esto de CardNet

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "card_number": card_number,
        "exp_date": exp_date,
        "cvv": cvv,
        "amount": amount
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}
