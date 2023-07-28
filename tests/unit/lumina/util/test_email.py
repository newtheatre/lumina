import pytest
from lumina.util import email


class TestMaskEmail:
    @pytest.mark.parametrize(
        "input,expected",
        [
            ("fred@bloggs.test", "fr***@bl***.test"),
            ("fred-bloggington.email+1@subdomain.bloggs.test.net", "fr***@su***.net"),
            ("alice.bloggs@gmail.co.uk", "al***@gm***.uk"),
        ],
    )
    def test_mask_email(self, input, expected):
        assert email.mask_email(input) == expected

    @pytest.mark.parametrize(
        "input",
        [
            ("fred@bloggs.test@gmail.com"),
            ("@"),
            (""),
            ("fred@tld"),
        ],
    )
    def test_raises_value_error(self, input):
        with pytest.raises(ValueError):
            print(email.mask_email(input))
