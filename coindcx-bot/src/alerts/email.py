from typing import List, Optional

from loguru import logger

from src.config import settings


class EmailAlert:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_pass = settings.smtp_pass
        self.alert_email = settings.alert_email

    async def send_email(
        self,
        subject: str,
        body: str,
        recipients: Optional[List[str]] = None,
    ) -> bool:
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            logger.warning("Email not configured")
            return False

        if recipients is None:
            recipients = [self.alert_email] if self.alert_email else []

        if not recipients:
            logger.warning("No email recipients configured")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText

            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(recipients)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def send_trade_alert(self, trade: dict):
        html = f"""
        <h2>Trade {trade.get('status', 'unknown').upper()}</h2>
        <table>
            <tr><td>Symbol:</td><td>{trade.get('symbol', 'N/A')}</td></tr>
            <tr><td>Direction:</td><td>{trade.get('side', '').upper()}</td></tr>
            <tr><td>Entry:</td><td>${trade.get('entry_price', 0):.4f}</td></tr>
            <tr><td>Stop Loss:</td><td>${trade.get('stop_loss', 0):.4f}</td></tr>
            <tr><td>Take Profit:</td><td>${trade.get('take_profit_1', 0):.4f}</td></tr>
            <tr><td>Confidence:</td><td>{trade.get('confidence_score', 0):.1f}%</td></tr>
        </table>
        <p>{trade.get('reason_entry', 'N/A')}</p>
        """
        await self.send_email(f"Trade Alert - {trade.get('symbol', 'N/A')}", html)
