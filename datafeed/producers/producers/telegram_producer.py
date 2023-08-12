import configparser
import json
import asyncio
from datetime import date, datetime
import time
import re
import pandas as pd
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)
from kafka import KafkaProducer

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id, api_hash = config['Telegram']['api_id'], str(config['Telegram']['api_hash'])
phone, username = config['Telegram']['phone'], config['Telegram']['username']

regex_pattern = r'(\w+)\s+(Long|Short)\s+Liquidation:\s+\$(\d+(?:\.\d+)?K?)\s+at\s+\$(\d+\.\d+)'

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

producer = KafkaProducer(bootstrap_servers='broker:29092')
topic = 'alt_liquidations'
@client.on(events.NewMessage(chats="nanceliqtape"))
async def newMessageListener(event):
    msg = event.message.message
    try: matches = re.search(regex_pattern, msg)
    except: pass
    if matches:
        liquidation_amount_str = matches.group(3)
        if liquidation_amount_str.endswith('K'):
            liquidation_amount = float(liquidation_amount_str[:-1]) * 1000
        else:
            liquidation_amount = float(liquidation_amount_str)
    msg = {
        'ticker' : matches.group(1),
        'amount' : liquidation_amount,
        'price': float(matches.group(4)),
        'side': matches.group(2),
        'timestamp': int(time.mktime(datetime.now().timetuple()) * 1000)
    }
    producer.send(topic, value=json.dumps(msg).encode('utf-8'))


with client:
    client.run_until_disconnected()
    producer.close()