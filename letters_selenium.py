from urllib.parse import quote
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

import gspread
import pandas as pd
from datetime import datetime

import logging

import os
from dotenv import load_dotenv

# Configurations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WHATSAPP_WEB_URL = 'https://web.whatsapp.com'
CHROME_USER_DATA_DIR = r"C:\Users\laism\ChromeWhatsAppSession"

load_dotenv()
SHEET_URL = os.getenv("SHEET_URL")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")


def generate_link(contact, message):
    message_encoded = quote(message)
    return f"https://web.whatsapp.com/send?phone={contact}&text={message_encoded}"


def send_messages(driver, df_letter):
    for index in df_letter.index:
        to_phone = '+55' + df_letter['Telefone'][index]
        to_name = df_letter['Nome'][index]
        letter = df_letter['Mensagem'][index]
        letter_number = df_letter['Numero Carta'][index]

        message = f"""Olá *{to_name}*!
Chegou uma cartinha anônima do *Amigo Secreto Minha Flor!* 💐🌷🪻🪴
        \nVeja o texto abaixo 💌: 
        \n{letter}"""

        logging.info(f"{index}/{len(df_letter)} => Sending message to {to_phone}...")

        try:
            whatsapp_url = generate_link(to_phone, message)
            driver.get(whatsapp_url)
            sleep(5)
            # Wait until the message box is available
            msg_box = WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )

            # Just in case the pre-filled text doesn't trigger the button
            sleep(5)
            msg_box.send_keys(" ")  # triggers focus
            msg_box.send_keys(Keys.ENTER)
            logging.info(f"Message sent to {to_phone}\n")

            set_letter_sent(letter_number)
            sleep(5)

        except Exception as e:
            logging.info(f"Failed to send message to {to_phone}: {e}\n")


def get_letters():
    # Authenticate
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    logging.info(f"Opening sheet..")
    # Open the Google Sheet by name or URL
    sh = gc.open_by_url(SHEET_URL)

    # Select a worksheet
    worksheet = sh.worksheet("Respostas")

    logging.info(f"Getting letters to send...")

    # Get all data as a list of lists
    data = worksheet.get_all_values()

    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Filter only registries that are not sent yet
    df = df[df['Data Envio'].isna() | (df['Data Envio'].astype(str).str.strip() == '')]

    return df


def set_letter_sent(target_id):
    # Authenticate
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    # Open the Google Sheet by name or URL
    sh = gc.open_by_url(SHEET_URL)

    # Select a worksheet
    worksheet = sh.worksheet("Respostas")

    # Get all data as a list of lists
    data = worksheet.get_all_values()

    # Extract header and rows
    header = data[0]
    rows = data[1:]

    # Find the indexes of the columns we care about
    id_col = header.index("Numero Carta")
    sent_col = header.index("Data Envio")

    for i, row in enumerate(rows, start=2):  # start=2 because first row is header
        if row[id_col] == target_id:
            # Found the matching row — update 'Sent' column
            worksheet.update_cell(i, sent_col + 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logging.info(f"Updated 'Data Envio' for ID {target_id} at row {i}")
            break
    else:
        logging.info(f"ID {target_id} not found.")


if __name__ == '__main__':

    # Configure drive for Selenium
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
    options.add_argument("--start-maximized")

    # Get letters to be sent
    df_letters = get_letters()

    if len(df_letters) > 0:

        # Initialize dirver for webdriver
        driver = webdriver.Chrome(options=options)
        driver.get(WHATSAPP_WEB_URL)

        # Wait for WhatsApp Web to load
        WebDriverWait(driver, 85).until(
            EC.presence_of_element_located((By.ID, "pane-side"))
        )
        logging.info("WhatsApp Web fully loaded.")

        # Send messages
        send_messages(driver, df_letters)

        logging.info("All messages sent!")
        driver.quit()

    else:
        logging.info("There are no messages to be sent.")
