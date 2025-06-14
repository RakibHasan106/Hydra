from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio,sys,os,json,string,random

#PreLogin Authorization
def saved_info_login(session_details):
    client = TelegramClient (
        session_details["session_name"],
        session_details["api_id"],
        session_details["api_hash"]
    )
    try:
        client.connect()
    except Exception as e:
        print(e)
        client.disconnect()
        return False
    
    if not client.is_user_authorized():
        client.disconnect()
        return False
    else:
        client.disconnect()
        return True


def send_code(api_id,api_hash,phone_number):
    
    session_path = os.path.join("./session","saved_session.session")
    if(not os.path.isdir('./session')):
        os.mkdir('./session')

    client = TelegramClient(session_path,api_id,api_hash)
    
    try:
        client.connect()
    except Exception as e:
        print("exception occured during connecting: ")
        print(e)
        # client.disconnect()
        return None

    if not client.is_user_authorized():
        try:
            client.send_code_request(phone_number)
        except Exception as E:
            client.disconnect()
            print("exception occured during sending code request to phone number"+e)
            return None

    return client

def login(client,entered_code):
    try:
        client.sign_in(code=entered_code)
    except Exception as e:
        print("error occurred during final login")
        client.disconnect()
        print(e)
        return None
    return client

def get_client(session_details):
    client = TelegramClient (
        session_details["session_name"],
        session_details["api_id"],
        session_details["api_hash"]
    )
    try:
        client.connect()
    except Exception as e:
        client.disconnect()
        client = None
    
    return client

def session_loader():
    session_file_path = os.path.join(os.getcwd(),"session","LastSavedSession.json")
    current_session = None
    print(session_file_path)

    if(os.path.isfile(session_file_path)): #checks if session file exists or not
        print("file exists")
        with open(session_file_path,"r") as f:
            try:
                current_session = json.load(f)
            except:
                return None
            # if telegram_login.saved_info_login(current_session) == True:
            #     stacked_widget.setCurrentIndex(2)
    
    return current_session