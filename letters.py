import gspread
import pandas as pd

import logging

from datetime import datetime
import pywhatkit

import os
from dotenv import load_dotenv

# Configurations
load_dotenv()
SHEET_URL = os.getenv("SHEET_URL")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")


def send_messages(df_letter):
    for index in df_letter.index:
        to_phone = '+55' + df_letter['Telefone'][index]
        to_name = df_letter['Nome'][index]
        letter = df_letter['Mensagem'][index]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"""Olá *{to_name}*!
Chegou uma cartinha anônima do *Amigo Secreto Minha Flor!* 💐🌷🪻🪴
Veja o texto abaixo 💌: 
{letter}
"""
        logging.info(f"Enviando mensagem para {to_phone}")
        pywhatkit.sendwhatmsg_instantly(to_phone, message, wait_time=20, tab_close=True)

        # Update a single cell
        worksheet.update_cell(index + 2, 6, now)


if __name__ == '__main__':
    # Authenticate
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    # Open the Google Sheet by name or URL
    sh = gc.open("Cartas Amigo Secreto")

    # Select a worksheet
    worksheet = sh.worksheet("Form Responses 1")

    # Get all data as a list of lists
    data = worksheet.get_all_values()

    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Filter only registries that are not sent yet
    df = df[df['Data Envio'].isna() | (df['Data Envio'].astype(str).str.strip() == '')]
    print(df.head)

    send_messages(df)
