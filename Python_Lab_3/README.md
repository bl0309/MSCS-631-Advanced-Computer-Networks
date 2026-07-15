# Python Lab 3: SMTP Mail Client

## Run

Start a local SMTP testing server first. Recommended options include `smtp4dev`, `MailHog`, or `FakeSMTP`. Configure it to listen on `localhost` port `1025`, or update the environment variables below to match the tool's settings.

```bash
export SMTP_SERVER=localhost
export SMTP_PORT=1025
export SMTP_SENDER=student@example.com
export SMTP_RECIPIENT=receiver@example.com
python3 SMTPMailClient.py
```

Optional variables:

```bash
export SMTP_SUBJECT='Python Lab 3 SMTP Test'
export SMTP_BODY='This message was sent by my Python SMTP socket client.'
```

## Files

- `SMTPMailClient.py`: completed socket-based SMTP client.
- `experience.txt`: two-paragraph reflection for the lab submission.
- `mailhog-received-email.png`: screenshot showing the received email in MailHog.
- `smtp-client-terminal-output.png`: screenshot showing the Python client SMTP command exchange.
- `mailhog-docker-server-log.png`: screenshot showing the MailHog Docker server logs.
- `mailhog-api-event-stream.png`: screenshot showing MailHog event details for the received message.
- `mailhog-source-view.png`: screenshot showing the raw/source view of the received email.

## Expected Result

The client connects to the local SMTP testing server, receives the `220` greeting, sends `HELO`, `MAIL FROM`, `RCPT TO`, `DATA`, the email contents, and finally `QUIT`. The terminal output prints each SMTP reply so the protocol exchange is visible.
