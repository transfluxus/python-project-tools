from tools.env_root import root
from tools.local_bags import local_bag

tests_dir = root() / "data/tests/"
test_path = (tests_dir / "bag")
test_path.mkdir(exist_ok=True)
test_temp_dir = root() / "data/tests/temp"


def test_basic():
    local_bag([test_path / "t1"], "bag_t1", {})

test_basic()