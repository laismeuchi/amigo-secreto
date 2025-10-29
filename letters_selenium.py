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

from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# ---- Logging Setup ----
LOG_DIR = r"C:\logs\letters_selenium"
os.makedirs(LOG_DIR, exist_ok=True)
logfile = os.path.join(LOG_DIR, "letters_selenium.log")

logger = logging.getLogger("letters_selenium")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    # File handler (rotates daily, keeps 7 days)
    file_handler = TimedRotatingFileHandler(
        logfile, when="midnight", backupCount=7, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)

logger.info("Script started")

# ---- Configurations ----
WHATSAPP_WEB_URL = 'https://web.whatsapp.com'
CHROME_USER_DATA_DIR = r"C:\Users\laism\ChromeWhatsAppSession"

load_dotenv()
SHEET_URL = os.getenv("SHEET_URL")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# ---- Functions ----

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

        logger.info(f"{index}/{len(df_letter)} => Sending message to {to_phone}...")

        try:
            whatsapp_url = generate_link(to_phone, message)
            driver.get(whatsapp_url)
            sleep(5)
            msg_box = WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )

            sleep(5)
            msg_box.send_keys(" ")  # triggers focus
            msg_box.send_keys(Keys.ENTER)
            logger.info(f"Message sent to {to_phone}\n")

            set_letter_sent(letter_number)
            sleep(5)

        except Exception as e:
            logger.info(f"Failed to send message to {to_phone}: {e}\n")


def get_letters():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

    logger.info("Opening sheet...")
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet("Respostas")

    logger.info("Getting letters to send...")
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df[df['Data Envio'].isna() | (df['Data Envio'].astype(str).str.strip() == '')]

    return df


def set_letter_sent(target_id):
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet("Respostas")
    data = worksheet.get_all_values()
    header = data[0]
    rows = data[1:]

    id_col = header.index("Numero Carta")
    sent_col = header.index("Data Envio")

    for i, row in enumerate(rows, start=2):
        if row[id_col] == target_id:
            worksheet.update_cell(i, sent_col + 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logger.info(f"Updated 'Data Envio' for ID {target_id} at row {i}")
            break
    else:
        logger.info(f"ID {target_id} not found.")


# ---- Main Script ----
if __name__ == '__main__':
    df_letters = get_letters()

    if len(df_letters) > 0:
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(options=options)
        driver.get(WHATSAPP_WEB_URL)

        WebDriverWait(driver, 85).until(
            EC.presence_of_element_located((By.ID, "pane-side"))
        )
        logger.info("WhatsApp Web fully loaded...")

        send_messages(driver, df_letters)
        logger.info("All messages sent!")
        driver.quit()
    else:
        logger.info("There are no messages to be sent...")

logger.info("Script finished")
