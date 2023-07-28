import boto3
import pytest
from lumina import ssm
from lumina.config import settings
from moto import mock_ssm


class TestGetSsmParameter:
    @mock_ssm()
    def test_get_param(self):
        boto3.client("ssm", region_name=settings.aws_region).put_parameter(
            Name="/test/exists", Value="test", Type="String"
        )
        assert ssm.get_parameter("/test/exists") == "test"

    @mock_ssm()
    def test_get_missing_param(self):
        with pytest.raises(ValueError):
            ssm.get_parameter("/test/not-exists")
