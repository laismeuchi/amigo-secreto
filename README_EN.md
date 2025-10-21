# Secret Santa

Project for a Secret Santa draw and sending the results via WhatsApp.

## Request

My mother has a nursery where she sells different types of plants, from flowers to fruit trees.

Over the years she has acquired customers in several cities in the region and sales are made to these customers via WhatsApp and then, once a month, my father goes to these cities to make deliveries to customers.

There is also a WhatsApp group in which participating customers can monitor the products available, in addition to exchanging experiences about growing and caring for their plants.

Over time, clients began to get to know each other through the group and interact a lot, which led her to the idea of creating a secret friend this year among clients who want to participate.
The idea is to draw among customers and then during deliveries, gifts would be sent to participants.

So she asked me for a way to do this draw among customers in the various cities and send each participant the result via WhatsApp.
It should be something very simple as most customers only know how to use WhatsApp.

## Solution

### Secret Santa Draw

The draw is carried out based on the spreadsheet filled out with the Participant's Name, Telephone and City.

![Screenshot 2024-10-30 174740](https://github.com/user-attachments/assets/00ee603f-fc46-48d7-b18e-4aa036e0b56a)


The sheet is read into a [Pandas](https://pandas.pydata.org/) _dataframe_. A copy of this _dataframe_ is made and the _suffle_ function of the [_random_](https://docs.python.org/3/library/random.html) library is applied to shuffle the list of participants.
Validation is also carried out to see if any participant drew it themselves and if this is the case, a new draw is carried out until there are no such cases.

``` python
def assign_secret_friends(participants):
    logging.info("Iniciando o Sorteio...")
    while True:
        drawn = participants[:]
        random.shuffle(drawn)
        if all(participants[i]['Telefone'] != drawn[i]['Telefone'] for i in range(len(participants))):
            return drawn
        logging.info("Tivemos pessoas tirando ela mesma.. refazendo o sorteio")
```

This was an example of a draw result:

![Screenshot 2024-10-30 190342](https://github.com/user-attachments/assets/dcd4b311-4aba-4848-bb8b-fcaf00071290)


As the number of participants is small, this solution meets the needs, but in cases of many participants this would be a part of the code that needs to be adjusted for better performance.

### Messaging (pywhatkit)

Thinking about simplicity, I decided to use WhatsApp's [Click to Chat](https://faq.whatsapp.com/5913398998672934/?helpref=uf_share) option, where you can send a message to a number directly from the browser.
It was then that I found the library [pywhatkit](https://pypi.org/project/pywhatkit/) that encapsulates the whole part of opening the browser and using *Click to Chat* and closing the tab.

The _sendwhatmsg_instantly_ function sends the message instantly to the indicated phone number. The _wait_time_ parameter specifies the time in seconds that the message will be sent after opening the browser and the _tab_close=True_ closes the tab after sending the message.”

``` python
def send_messages(df_drawn):
    for index in df_drawn.index:
        participant_name = df_drawn['Participante'][index]
        participant_phone = "+55" + str(df_drawn['Telefone'][index])
        friend_name = df_drawn['Amigo Secreto'][index]
        friend_city = df_drawn['Amigo Secreto Cidade'][index]

        message = f"""Olá *{participant_name}*!
        Chegou o resultado do sorteio de *Amigo Secreto 2025* 💐🌷🌿
        Seu amigo(a) secreto é
        .
        .
        .
        .
        .
        *{friend_name}* que mora em *{friend_city}*
        """
        logging.info(f"Enviando mensagem para {participant_phone}")
        pywhatkit.sendwhatmsg_instantly(participant_phone, message, wait_time=15, tab_close=True)
```

## New Version — Anonymous Letters

This year, I decided to make the experience more interactive by adding a new feature that allows participants to send anonymous messages to each other.
Because the users are not familiar with technology, I focused again on simplicity:
- Google Forms was used to collect the messages — no login required, easy to use, and responses are automatically stored in Google Sheets.
- The script reads new letters from the sheet using [gspread](https://pypi.org/project/gspread/).
- Each message is sent through WhatsApp Web using [Selenium](https://www.selenium.dev/).
- After sending, the message is marked as delivered in the sheet.

The process is scheduled to run every 15 minutes, checking for new messages to send.

``` python
def send_messages(driver, df_letter):
    for index in df_letter.index:
        to_phone = '+55' + df_letter['Telefone'][index]
        to_name = df_letter['Nome'][index]
        letter = df_letter['Mensagem'][index]
        message = f"""Olá *{to_name}*!
Chegou uma cartinha anônima do *Amigo Secreto 2025!* 💐🌷🪻🪴
Veja o texto abaixo 💌:
{letter}"""
        whatsapp_url = generate_link(to_phone, message)
        driver.get(whatsapp_url)
        sleep(5)
        msg_box = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        msg_box.send_keys(" ")
        msg_box.send_keys(Keys.ENTER)

```

This approach gives more control and reliability than pywhatkit, while keeping the process simple and automated.

<!-- ### Demo

Here is a video demonstrating how the draw is carried out and messages are sent: 

[![Demo](https://img.youtube.com/vi/SRuPT3GjgVg/0.jpg)](https://www.youtube.com/watch?v=SRuPT3GjgVg) -->


## *_Disclaimer_*

WhatsApp has a series of restrictions on sending messages on a large scale, especially using personal accounts. Be aware of these rules!
