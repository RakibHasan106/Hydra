from PyQt5.QtCore import QObject, pyqtSignal
import asyncio,time,os,json
from telethon.sync import TelegramClient


class login_worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(object)

    def __init__(self,api_id,api_hash,phone):
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone

        self.entered_code = None
        self.is_code_entered = False

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.login())
        loop.close()
        
        self.finished.emit()

    async def login(self):
        session_path = os.path.join("./session","tempSession.session")
        client = TelegramClient(
            session_path,
            self.api_id,
            self.api_hash
        )

        try:
            await client.connect()

            if not await client.is_user_authorized():
                await client.send_code_request(self.phone)
                print("no error after sending code request")

                while not self.is_code_entered:
                    time.sleep(0.2)

                await client.sign_in(code=self.entered_code)

                print("no error after signing in")

                me = await client.get_me()
                username = me.username
                print(username)
                
                if username == None : 
                    username = me.first_name + " " + me.last_name
                
                await client.disconnect()

                new_session_path = os.path.join("./session",f"{username}.session")
                os.rename(session_path, new_session_path)

                json_path = os.path.join("./session","saved_sessions.json")

                try:
                    with open(json_path,'r') as f:
                        data = json.load(f)

                except (FileNotFoundError, json.JSONDecodeError):
                    data = {"sessions": []}

                new_session = {
                    "user_name" : username,
                    "session_name" : new_session_path,
                    "api_id" : self.api_id,
                    "api_hash" : self.api_hash
                }

                data["sessions"].append(new_session)
        
                    
                with open(json_path, "w") as f:
                    json.dump(data, f, indent=2)

                
                current_session_json = os.path.join("./session","current_session.json")
                
                with open(current_session_json, 'w') as f:
                    json.dump(new_session,f,indent=2)

        
        except Exception as E:
            self.error.emit(E)
            print("error from the loginThread: "+str(E))

    def enter_code(self,code):
        self.entered_code = code
        self.is_code_entered = True
    
