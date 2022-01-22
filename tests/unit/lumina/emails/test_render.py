from lumina.emails.render import render_email


class TestRegisterMemberEmail:
    def test_basic(self):
        email = render_email(
            "register_member.html",
            name="John Doe",
            auth_url="https://example.com/auth?token=12345",
        )
        assert "Alumni Network" in email.plaintext
        assert "<p>" not in email.plaintext
        assert "John Doe" in email.plaintext
        assert "https://example.com/auth?token=12345" in email.plaintext

        assert "Alumni Network" in email.html
        assert "<p>" in email.html
        assert "John Doe" in email.html
        assert "https://example.com/auth?token=12345" in email.html
