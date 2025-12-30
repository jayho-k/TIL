import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.tasks.user_tasks import send_welcome_email
from app.models.user_email import UserEmail
from app.core.database import async_session_factory, Base, engine as global_engine
from sqlalchemy import select
# Note: we import Container but users code uses Container() instantiation, so we patch the class in user_tasks module

# Fixture to initialize DB tables
@pytest.fixture(scope="module")
def init_db():
    async def _init():
        async with global_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_init())
    yield

async def verify_db_state(email):
    # Use global factory for verification to avoid wiring complexity in test helper
    async with async_session_factory() as session:
        result = await session.execute(select(UserEmail).where(UserEmail.user_name == email))
        return result.scalar_one_or_none()

def test_send_welcome_email_success(init_db):
    # Patch sleep
    async def fast_sleep(delay):
        return
        
    with patch("asyncio.sleep", side_effect=fast_sleep) as mock_sleep:
        # Run task
        # It uses real DB settings from config.yaml via Container() instantiation
        result = send_welcome_email.apply(args=["success@example.com"]).get()
        
        # Verify result
        assert "Email sent" in result
        
        # Verify sleep
        mock_sleep.assert_called_with(10)
        
        # Verify DB
        user_email = asyncio.run(verify_db_state("success@example.com"))
        assert user_email is not None
        assert user_email.success_or_fail == "success"

class FakeSessionContext:
    def __init__(self, raise_error=False):
        self.raise_error = raise_error
        
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass
    
    def add(self, obj):
        if self.raise_error:
            raise Exception("DB Error")
            
    async def commit(self):
        pass
        
    async def rollback(self):
        pass

def test_send_welcome_email_failure_retry():
    # Sync test for failure path
    
    async def fast_sleep(delay):
        return

    with patch("asyncio.sleep", side_effect=fast_sleep):
        # Override the session factory by mocking Container class in user_tasks
        
        # Logic for Fake Session that fails once, then works
        class ConditionalFailSession:
            def __init__(self):
                self.call_count = 0
            
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
            
            def add(self, obj):
                self.call_count += 1
                if getattr(obj, "success_or_fail", "") == "success":
                    raise ConnectionError("Simulated DB Connection Error")
                # Allow "failed: ..." to succeed
                
            async def commit(self):
                pass
            async def rollback(self):
                pass

        fake_session = ConditionalFailSession()
        
        # Mock: InfraContainer.db_session_factory() -> fake_session callback
        # We Mock 'app.tasks.user_tasks.InfraContainer' class
        
        with patch("app.tasks.user_tasks.InfraContainer") as MockInfraContainer:
             # InfraContainer.db_session_factory() returns factory
             
             simple_factory = lambda: fake_session
                 
             MockInfraContainer.db_session_factory.return_value = simple_factory
             
             # Expect the task to raise the exception after logging
             # Pass retries=3 to simulate it being the last retry (max_retries=3)
             with pytest.raises(Exception):
                send_welcome_email.apply(args=["fail@example.com"], retries=3).get()
            
             # Verify that we tried to write failure log
             assert fake_session.call_count >= 2
