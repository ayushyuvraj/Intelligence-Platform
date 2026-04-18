import pytest

import pytest

def pytest_collection_modifyitems(config, items):
    for item in items:
        if "test_golden_path_e2e" in item.name:
            item.add_marker(pytest.mark.xfail(reason="E2E requires dev server", strict=False))
