from app.conversation.user_profile import UserProfile

class ConversationManager:
    #Manages a single convo with a user
    #Stores conversation history
    #Maintains current UserProfile
    #Pass messages to parser
    #Decides whether to ask another question or proceed to recommend destinations

    def __init__(self):
        self.profile = UserProfile()
        self.messages: list[dict[str,str]] = []

    def add_user_messages(self, message: str) -> None:
        self.messages.append(
            {
                "role": "user",
                "content": self.messages
            }
        )
    
    def add_assistant_message(self, message:str) -> None:
        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )
    
    def get_profile(self) -> UserProfile:
        return self.profile
    
    def get_messages(self) -> list[dict[str,str]]:
        return self.messages
    
    def reset(self) -> None:
        #Starts a fresh convo
        self.profile = UserProfile()
        self.messages.clear()

        