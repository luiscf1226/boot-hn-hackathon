#!/usr/bin/env python3
"""
Simple test script to verify the agent integration works.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db, create_tables
from app.services.agent import Agent
from app.models.user import User


async def test_agent_integration():
    """Test the agent integration."""
    print("🧪 Testing Agent Integration...")
    
    try:
        # Initialize database
        print("📦 Creating database tables...")
        create_tables()
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Create agent instance
            print("🤖 Creating agent instance...")
            agent = Agent(db)
            
            # Test without API calls (just structure)
            print("📋 Testing session management...")
            
            # Test session creation
            session = agent.start_new_session("Test Session")
            print(f"✅ Created session: {session.id}")
            
            # Test getting user sessions
            sessions = agent.get_user_sessions()
            print(f"✅ Found {len(sessions)} sessions")
            
            # Test getting current model
            model = agent.ai_service.get_current_model()
            print(f"✅ Current model: {model}")
            
            print("🎉 Basic agent integration test passed!")
            print("\nℹ️  To test AI calls, make sure you have:")
            print("   1. Set GEMINI_API_KEY in your .env file")
            print("   2. Run /setup command to configure your model")
            print("   3. Install google-generativeai: pip install google-generativeai")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent_integration())