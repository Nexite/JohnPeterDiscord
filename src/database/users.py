class User:
    def __init__(self, discord_id: int, clear_username: str = None):
        self.discord_id = discord_id
        self.clear_username = clear_username
