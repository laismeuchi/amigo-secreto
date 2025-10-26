import random
import pandas as pd
import logging
from datetime import datetime
import pytz
from urllib.parse import quote

from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


# Configurations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WHATSAPP_WEB_URL = 'https://web.whatsapp.com'
CHROME_USER_DATA_DIR = r"C:\Users\laism\ChromeWhatsAppSession"

def read_xlsx_file(file_path):
    return pd.read_excel(file_path)

def generate_link(contact, message):
    message_encoded = quote(message)
    return f"https://web.whatsapp.com/send?phone={contact}&text={message_encoded}"


def assign_secret_friends(participants):
    logging.info("Iniciando o Sorteio...")
    while True:
        drawn = participants[:]
        random.shuffle(drawn)
        if all(participants[i]['Telefone'] != drawn[i]['Telefone'] for i in range(len(participants))):
            return drawn
        logging.info("Tivemos pessoas tirando ela mesma.. refazendo o sorteio")


def send_messages(driver, df_result):
    for index in df_result.index:
        participant_name = df_result['Participante'][index]
        participant_phone = "+55" + str(df_result['Telefone'][index])
        friend_name = df_result['Amigo Secreto'][index]
        friend_city = df_result['Amigo Secreto Cidade'][index]

        message = f"""Olá *{participant_name}*!
Chegou o resultado do sorteio de *Amigo Secreto Minha Flor 2025!* 💐🌷🪻🪴
Seu amigo(a) secreto é
.
.
.
.
.
.
.
.
.
.
*{friend_name}* 
que mora em *{friend_city}*
"""

        logging.info(f"{index}/{len(df_result)} => Sending message to {participant_phone}...")

        try:
            whatsapp_url = generate_link(participant_phone, message)
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
            logging.info(f"Message sent to {participant_phone}\n")
            sleep(5)

        except Exception as e:
            logging.info(f"Failed to send message to {participant_phone}: {e}\n")


if __name__ == '__main__':
    logging.info("Iniciando script...")
    df_participants = read_xlsx_file('bases/Amigo Secreto do Viveiro_2025.xlsx')
    execution_time = datetime.now(pytz.timezone('America/Cuiaba')).strftime("%Y%m%d%H%M%S")

    # Configure drive for Selenium
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
    options.add_argument("--start-maximized")


    logging.info("Iniciando sorteio...")
    participants = df_participants.to_dict('records')
    drawn = assign_secret_friends(participants)
    logging.info("Sorteio realizado...")

    df_drawn = pd.DataFrame({
        'Participante': [p['Participante'] for p in participants],
        'Telefone': [p['Telefone'] for p in participants],
        'Cidade': [p['Cidade'] for p in participants],
        'Amigo Secreto': [d['Participante'] for d in drawn],
        'Amigo Secreto Telefone': [d['Telefone'] for d in drawn],
        'Amigo Secreto Cidade': [d['Cidade'] for d in drawn],
    })

    # output_file = f'bases/Amigo Secreto do Viveiro - Resultado_{execution_time}.xlsx'
    output_file = 'bases\Amigo Secreto do Viveiro - Resultado_20251026171350.xlsx'
    #df_drawn.to_excel(output_file, index=False)

    df_results = read_xlsx_file(output_file)

    logging.info("Enviando mensagens...")


    if len(df_results) > 0:

        # Initialize dirver for webdriver
        driver = webdriver.Chrome(options=options)
        driver.get(WHATSAPP_WEB_URL)

        # Wait for WhatsApp Web to load
        WebDriverWait(driver, 85).until(
            EC.presence_of_element_located((By.ID, "pane-side"))
        )
        logging.info("WhatsApp Web fully loaded.")

        # Send messages
        send_messages(driver, df_results)

        logging.info("All messages sent!")
        driver.quit()

    else:
        logging.info("There are no messages to be sent.")

    logging.info("Mensagens enviadas.")