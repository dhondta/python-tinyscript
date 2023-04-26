# -*- coding: UTF-8 -*-
"""Utility function for sending notifications (either local or by email).

"""
from .common import lazy_load_module
from .data.types import is_domain, is_email, is_file, is_port
from ..preimports import os

for _m in ["email", "mimetypes", "plyer", "smtplib"]:
    lazy_load_module(_m)


__all__ = __features__ = ["notify", "send_mail"]


SECURITY = {25: "unencrypted", 465: "ssl", 587: "starttls"}
SERVERS = {
    'aol.com':        ("smtp.aol.com", 465),
    'gmail.com':      ("smtp.gmail.com", 587),
    'gmx.com':        ("smtp.gmx.com", 465),
    'hotmail.com':    ("smtp.live.com", 465),
    'hubspot.com':    ("smtp.hubspot.com", 587),
    'mail.com':       ("smtp.mail.com", 465),
    'microsoft.com':  ("smtp.office365.com", 587),
    'outlook.com':    ("smtp.office365.com", 587),
    'pepipost.com':   ("smtp.pepipost.com", 587),
    'protonmail.com': ("smtp.protonmail.com", 465),
    'yahoo.com':      ("smtp.mail.yahoo.com", 587),
    'zoho.com':       ("smtp.zoho.com", 465),
}


def notify(title="", message="", app="", icon="", timeout=5, ticker=""):
    """ Shortcut to plyer.notification.notify, not considering the 'toast' option, and fail-safe.
    
    :param title:   title of the notification
    :param message: message of the notification
    :param app:     name of the app launching this notification
    :param icon:    name or path of the icon to be displayed along with the message
    :param timeout: time to display the message for
    :param ticker:  text to display on status bar as the notification arrives
    """
    try:
        plyer.notification.notify(title, message, app, icon, timeout, ticker)
    except NotImplementedError:
        pass


def send_mail(from_mail, to_mail, subject, body, *attachments, **kwargs):
    """ Send an email to a single receiver.
    
    :param from_mail:   sender's email address
    :param to_mail:     recipient's email address
    :param subject:     email subject
    :param body:        message body (HTML format)
    :param attachments: list of paths to files to be attached
    :param kwargs:      other email parameters (i.e. server, security, auth)
    """
    import email.mime
    ctype = kwargs.get('content_type', "plain")
    srv = kwargs.get('server')
    auth = kwargs.get('auth')
    auth_user, auth_pswd = (None, None) if auth is None else auth if len(auth) == 2 else (from_mail, auth)
    domain = (auth_user or from_mail).split("@")[-1]
    # parameters validation
    if not is_email(from_mail):
        raise ValueError("Bad sender email address")
    if not is_email(to_mail):
        raise ValueError("Bad recipient email address")
    if srv is None and domain in SERVERS.keys():
        try:
            host, port = SERVERS[domain]
        except KeyError:
            raise ValueError("Cannot find SMTP settings for %s" % domain)
    else:
        host, port = srv if isinstance(srv, tuple) and len(srv) == 2 else (srv, 25)
    if host is None or not is_domain(host) or not is_port(port):
        raise ValueError("Bad email server host or port")
    for path in attachments:
        if not is_file(path):
            raise ValueError("Attachment '%s' does not exist" % path)
    sec = kwargs.get('security', SECURITY.get(port, "unencrypted"))
    # create the email
    msg = email.mime.multipart.MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = from_mail, to_mail, subject
    msg.attach(email.mime.text.MIMEText(body, ctype))
    for path in attachments:
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split("/", 1)
        cls = globals().get("MIME" + maintype.capitalize())
        with open(path, 'rb') as f:
            if cls:
                submsg = cls(f.read(), _subtype=subtype)
            else:
                submsg = email.mime.base.MIMEBase(maintype, subtype)
                submsg.set_payload(f.read())
                encoders.encode_base64(submsg)
        submsg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
        msg.attach(submsg)
    # send the email
    session = getattr(smtplib, "SMTP_SSL" if sec == "ssl" else "SMTP")(host, port)
    if sec == "starttls":
        session.starttls()
    if auth:
        session.login(auth_user, auth_pswd)
    session.sendmail(from_mail, to_mail, msg.as_string())
    session.quit()

