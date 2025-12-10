import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_SENDER, EMAIL_RECEIVER, HTML_TEMPLATE):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = ", ".join(EMAIL_RECEIVER)
        msg['Subject'] = "Basic Input Data - File Upload Status"
        # Attach the HTML content
        msg.attach(MIMEText(HTML_TEMPLATE, 'html'))

        # Connect to the SMTP server using FQDN
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls() # Secure the connection
            server.ehlo()
            # Authenticate using different username
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            # Send the email
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
