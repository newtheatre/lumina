from lumina.emails.render import render_email

NAME = "Fred Bloggs"
AUTH_URL = "https://example.com/auth?token=12345"


class TestRegisterMemberEmail:
    def test_basic(self):
        email = render_email("register_member.html", name=NAME, auth_url=AUTH_URL)
        assert "Alumni Network" in email.plaintext
        assert "<p>" not in email.plaintext
        assert NAME in email.plaintext
        assert AUTH_URL in email.plaintext

        assert "Alumni Network" in email.html
        assert "<p>" in email.html
        assert NAME in email.html
        assert AUTH_URL in email.html


class TestLoginEmail:
    def test_basic(self):
        email = render_email(
            "login.html",
            name="Fred Bloggs",
            auth_url="https://example.com/auth?token=12345",
        )
        assert "Alumni Network" in email.plaintext
        assert "<p>" not in email.plaintext
        assert NAME in email.plaintext
        assert AUTH_URL in email.plaintext

        assert "Alumni Network" in email.html
        assert "<p>" in email.html
        assert NAME in email.html
        assert AUTH_URL in email.html
