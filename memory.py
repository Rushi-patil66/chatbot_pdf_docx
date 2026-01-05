class MemoryManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id):
        self.sessions[session_id] = {
            "document": "",
            "history": []
        }

    def store_document(self, session_id, content):
        self.sessions[session_id]["document"] = content

    def add_chat(self, session_id, role, message):
        self.sessions[session_id]["history"].append(
            f"{role}: {message}"
        )

    def get_full_context(self, session_id):
        session = self.sessions[session_id]
        chat_history = "\n".join(session["history"])

        return f"""
Document Content:
{session['document']}

Conversation History:
{chat_history}
"""
