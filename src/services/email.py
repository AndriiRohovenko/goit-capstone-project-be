from pathlib import Path

from jinja2 import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.conf.config import config

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "email_verification.html"


def send_verification_email(email: str, access_token: str, user_info):
    fullname = f"{user_info.name} {user_info.surname}"
    frontend_base = config.FRONTEND_URL.rstrip("/")
    verification_link = f"{frontend_base}/verify-email?token={access_token}"
    html = Template(TEMPLATE_PATH.read_text(encoding="utf-8")).render(
        fullname=fullname,
        verification_link=verification_link,
    )

    message = Mail(
        from_email=config.SENDGRID_FROM,
        to_emails=str(email),
        subject="Verify your email",
        html_content=html,
    )
    print(
        f"[email] sending verification to={email} from={config.SENDGRID_FROM}",
        flush=True,
    )
    try:
        response = SendGridAPIClient(config.SENDGRID_API_KEY).send(message)
        print(
            f"[email] sent ok to={email} status={response.status_code}",
            flush=True,
        )
    except Exception as e:
        print(f"[email] failed to send to={email}: {type(e).__name__}: {e}", flush=True)
