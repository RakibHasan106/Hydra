from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio,sys,os,json,string,random

#PreLogin Authorization
async def saved_info_login(session_details):
    client = TelegramClient (
        session_details["session_name"],
        session_details["api_id"],
        session_details["api_hash"]
    )
    try:
        await client.connect()
        
        me = await client.get_me()
        username = me.username
        print(username)
                
        if username == None : 
            username = me.first_name + " " + me.last_name
        
        new_session = {
            "user_name" : username,
            "session_name" : session_details["session_name"],
            "api_id" : session_details["api_id"],
            "api_hash" : session_details["api_hash"]
        }
                
        current_session_json = os.path.join("./session","current_session.json")
                
        with open(current_session_json, 'w') as f:
            json.dump(new_session,f,indent=2)
    
    except Exception as e:
        print(e)
        await client.disconnect()
        return False
    
    if not client.is_user_authorized():
        await client.disconnect()
        return False
    else:
        await client.disconnect()
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
    
    # try:
    #         client.send_code_request(phone_number)
    # except Exception as E:
    #         client.disconnect()
    #         print("exception occured during sending code request to phone number"+e)
    #         return None

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
    sessions_file_path = os.path.join(os.getcwd(),"session","saved_sessions.json")
    saved_sessions = None
    print(sessions_file_path)

    if(os.path.isfile(sessions_file_path)): #checks if session file exists or not
        print("file exists")
        with open(sessions_file_path,"r") as f:
            try:
                saved_sessions = json.load(f)
                saved_sessions = saved_sessions["sessions"]
            except:
                return None
            # if telegram_login.saved_info_login(current_session) == True:
            #     stacked_widget.setCurrentIndex(2)
    
    
    return saved_sessions

def current_session_loader():
    current_session_path = os.path.join("./session","current_session.json")

    current_session = None
    if(os.path.isfile(current_session_path)):
        try:
            with open(current_session_path, "r") as f:
                current_session = json.load(f)
        
        except Exception as e: 
            print(e)
            return None

    return current_session