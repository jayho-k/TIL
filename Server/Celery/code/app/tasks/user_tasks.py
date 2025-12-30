import asyncio
import logging
from celery import shared_task
from app.models.user_email import UserEmail
from app.container import InfraContainer 

logger = logging.getLogger(__name__)

__all__ = ["send_welcome_email"]


async def _send_welcome_email_logic(email: str, session_factory):
    """비동기 이메일 발송 로직"""
    await asyncio.sleep(10)  # 시뮬레이션
    
    async with session_factory() as session:
        try:
            user_email = UserEmail(user_name=email, success_or_fail="success")
            session.add(user_email)
            await session.commit()
            return f"Email sent to {email}"
        except Exception as e:
            await session.rollback()
            raise


async def _log_failure(email: str, error_msg: str, session_factory):
    """실패 로그를 DB에 저장"""
    async with session_factory() as session:
        try:
            user_email = UserEmail(
                user_name=email, 
                success_or_fail=f"failed: {error_msg}"
            )
            session.add(user_email)
            await session.commit()
            logger.info(f"Logged failure for {email} to database")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to log failure for {email}: {e}")


async def _task_main_logic(self, email: str, session_factory):
    """전체 태스크 로직을 하나의 비동기 함수로 통합"""
    try:
        result = await _send_welcome_email_logic(email, session_factory)
        logger.info(f"Successfully sent welcome email to {email}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}", exc_info=True)
        
        # 마지막 재시도인지 확인
        is_last_retry = self.request.retries >= self.max_retries - 1
        
        if is_last_retry:
            logger.error(f"Max retries exceeded for {email}. Logging failure to DB.")
            await _log_failure(email, str(e), session_factory)
        
        raise  # autoretry_for가 재시도 처리


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(ConnectionError, TimeoutError, OSError),  # 구체적인 예외만
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    name="send_welcome_email"
)
def send_welcome_email(self, email: str):
    """Celery 태스크: 환영 이메일 발송"""
    
    # DI 컨테이너에서 세션 팩토리 가져오기
    session_factory = InfraContainer.db_session_factory()
    # 비동기 로직 실행
    try:
        return asyncio.run(_task_main_logic(self, email, session_factory))
    except Exception as e:
        # 최종 로깅 (필요시)
        logger.error(f"Task failed for {email}: {e}")
        raise