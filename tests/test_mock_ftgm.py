"""Profile detection of the demo (mock) FTGM engine."""
import pytest

from app.modules.forecasting.infrastructure.adapters.mock_ftgm import SENTINELS, profile_name_for


@pytest.mark.parametrize(
    "names,expected",
    [
        # Level 1: the documented sentinel switches the profile on its own.
        (["iPhone 15 Pro Max 256GB", "cable usb-c"], "apple"),
        (["Oud Royal Intense 100ml"], "perfumes"),
        (["Esencia de Caracol Premium 96%"], "skincare"),
        (["Casaca Vintage Levi's 90s"], "vintage"),
        (["Oxford Cuero Marrón Clásico"], "calzado"),
        # Level 2: sentinel renamed or left out — the catalogue fingerprint still lands.
        (["iphone 13 128gb", "airpods pro", "cargador magsafe"], "apple"),
        (["zapato derby negro", "botín chelsea camel", "mocasín penny loafer"], "calzado"),
        (["serum niacinamida", "mascarilla hidrogel", "protector solar spf50"], "skincare"),
        (["casaca cuero 90s", "jean wrangler recto", "camisa franela grunge"], "vintage"),
        # A real shop that looks like none of them keeps the generic retail profile.
        (["arroz costeño 5kg", "aceite primor 1l", "leche gloria"], "general"),
        (["cuaderno rayado"], "general"),
        ([], "general"),
    ],
)
def test_profile_detection(names, expected):
    assert profile_name_for([n.lower() for n in names]) == expected


def test_every_sentinel_maps_to_a_profile():
    from app.modules.forecasting.infrastructure.adapters.mock_ftgm import _PROFILES

    for profile in SENTINELS.values():
        assert profile in _PROFILES
