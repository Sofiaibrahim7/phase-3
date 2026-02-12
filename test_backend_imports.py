import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_backend_imports():
    """Test that all backend modules can be imported without errors."""
    try:
        from backend.database import User, Task, Category, Conversation, Message, create_db_and_tables
        print("[OK] Database models imported successfully")

        from backend.mcp_tools import router as mcp_router
        print("[OK] MCP tools router imported successfully")

        from backend.chat_endpoint import router as chat_router
        print("[OK] Chat endpoint router imported successfully")

        from backend.agent import OpenAIAgent
        print("[OK] Agent imported successfully")

        from backend.main import app
        print("[OK] Main app imported successfully")

        print("\nAll backend modules imported successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Error importing backend modules: {e}")
        return False

if __name__ == "__main__":
    test_backend_imports()