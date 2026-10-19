import yaml

from models.base import HOURS


def test_params_load():
    params = yaml.safe_load(open("config/params.yaml"))
    assert params["site"]["name"] == "Laayoune"
    assert params["finance"]["discount_rate"] == 0.08


def test_hours_constant():
    assert HOURS == 365 * 24
