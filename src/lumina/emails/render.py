import html2text
from jinja2 import Environment, PackageLoader

from lumina.emails.send import EmailBody

env = Environment(loader=PackageLoader("lumina.emails", "templates"))


def render_email(template_filename: str, **context) -> EmailBody:
    template = env.get_template(template_filename)
    html = template.render(**context)
    return EmailBody(plaintext=html2text.html2text(html).strip(), html=html)
