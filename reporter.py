import html
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def _rec_group_html(papers: list[dict], label: str, color: str) -> str:
    if not papers:
        return ""
    items = "".join(
        f"""<div style="margin-bottom:10px;padding:10px;background:#f9f9f9;border-left:3px solid {color};">
          <p style="margin:0 0 2px 0;font-size:14px;font-weight:bold;">{p['stars']} {html.escape(p['title'])}</p>
          <p style="margin:0 0 2px 0;color:#666;font-size:11px;">{html.escape(p['venue'])} &middot; {p['year']}</p>
          <p style="margin:0;font-size:12px;color:#444;">{html.escape(p.get('reason', ''))}</p>
        </div>"""
        for p in papers
    )
    return f'<p style="margin:12px 0 4px;font-weight:bold;color:{color};">{label}</p>{items}'


def build_email_html(
    new_papers: list[dict],
    trend_text: str,
    db_stats: dict,
    week_label: str,
) -> str:
    must_read  = [p for p in new_papers if p.get("tier") == "强烈推荐"]
    worth_read = [p for p in new_papers if p.get("tier") == "值得一读"]

    if must_read or worth_read:
        rec_html = (
            '<h3 style="color:#0057a8;">&#128218; 本周推荐</h3>'
            + _rec_group_html(must_read,  "强烈推荐", "#c0392b")
            + _rec_group_html(worth_read, "值得一读", "#2980b9")
            + '<hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">'
        )
    else:
        rec_html = ""

    if new_papers:
        paper_rows = "".join(
            f"""<div style="margin-bottom:20px;padding:12px;border-left:3px solid #0057a8;">
              <p style="margin:0 0 4px 0;font-size:15px;font-weight:bold;">{p['stars']} {p['title']}</p>
              <p style="margin:0 0 4px 0;color:#666;font-size:12px;">
                {p['venue']} &middot; {p['year']} &middot; Citations: {p['citation_count']} &middot;
                <a href="https://doi.org/{p['doi']}">{p['doi']}</a>
              </p>
              <p style="margin:0;font-size:13px;">{p['contribution']}</p>
            </div>"""
            for p in new_papers
        )
    else:
        paper_rows = "<p>No new papers found this week.</p>"

    trend_html = trend_text.replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;color:#222;padding:20px;">
  <h2 style="color:#0057a8;">[SC Research Weekly] {week_label}</h2>

  {rec_html}

  <h3>New Papers This Week ({len(new_papers)})</h3>
  {paper_rows}

  <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

  <h3>Research Trend Analysis</h3>
  <p style="font-size:13px;line-height:1.8;">{trend_html}</p>

  <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

  <p style="font-size:11px;color:#999;">
    Database: {db_stats['total']} papers tracked &middot;
    Coverage: TPEL, TIE, ECCE, APEC &middot;
    Since: {db_stats['since']}
  </p>
</body>
</html>"""


def send_email(
    html: str,
    subject: str,
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: list[str],
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
    logger.info("Email sent to %s", recipients)
