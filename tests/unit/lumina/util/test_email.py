import pytest
from lumina.util import email


class TestMaskEmail:
    @pytest.mark.parametrize(
        "input,expected",
        [
            ("fred@bloggs.com", "fr***@bl***.com"),
            ("fred-bloggington.email+1@subdomain.bloggs.com.net", "fr***@su***.net"),
            ("alice.bloggs@gmail.co.uk", "al***@gm***.uk"),
        ],
    )
    def test_mask_email(self, input, expected):
        assert email.mask_email(input) == expected

    @pytest.mark.parametrize(
        "input",
        [
            ("fred@bloggs.com@gmail.com"),
            ("@"),
            (""),
            ("fred@tld"),
        ],
    )
    def test_raises_value_error(self, input):
        with pytest.raises(ValueError):
            email.mask_email(input)
