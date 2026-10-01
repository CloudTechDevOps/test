from tools import calculator, current_time


def test_calculator_basic():
    assert calculator("(25*4)+10") == {"result": 110}


def test_calculator_rejects_code():
    assert "error" in calculator("__import__('os').system('dir')")


def test_calculator_rejects_huge_pow():
    assert "error" in calculator("9**999999")


def test_calculator_div_zero():
    assert "error" in calculator("1/0")


def test_current_time_ist():
    assert current_time(5.5)["time"].endswith("+05:30")
