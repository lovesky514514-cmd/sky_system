class AppState:
    def __init__(self):
        self.current_username = None
        self.current_user = None

    def login(self, username, user_data):
        self.current_username = username
        self.current_user = user_data

    def logout(self):
        self.current_username = None
        self.current_user = None


app_state = AppState()