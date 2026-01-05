from utils import get_current_course


def test_get_current_course():
    data = get_current_course("EUR")
    assert data
    assert isinstance(data, float)
