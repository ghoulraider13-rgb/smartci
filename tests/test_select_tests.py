import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from select_tests import map_changes_to_tests, get_changed_files


class TestMapChangesToTests:
    def test_pricing_change_runs_pricing_and_cart(self):
        tests = map_changes_to_tests(['src/pricing.py'])
        assert 'tests/test_pricing.py' in tests
        assert 'tests/test_cart.py' in tests

    def test_inventory_change_runs_only_inventory(self):
        tests = map_changes_to_tests(['src/inventory.py'])
        assert tests == ['tests/test_inventory.py']

    def test_cart_change_runs_only_cart(self):
        tests = map_changes_to_tests(['src/cart.py'])
        assert tests == ['tests/test_cart.py']

    def test_requirements_txt_triggers_full_suite(self):
        tests = map_changes_to_tests(['requirements.txt'])
        assert tests == ['all']

    def test_pytest_ini_triggers_full_suite(self):
        tests = map_changes_to_tests(['pytest.ini'])
        assert tests == ['all']

    def test_workflow_file_triggers_full_suite(self):
        tests = map_changes_to_tests(['.github/workflows/ci.yml'])
        assert tests == ['all']

    def test_script_change_triggers_full_suite(self):
        tests = map_changes_to_tests(['scripts/dep_graph.py'])
        assert tests == ['all']

    def test_direct_test_file_change_runs_that_test(self):
        tests = map_changes_to_tests(['tests/test_pricing.py'])
        assert tests == ['tests/test_pricing.py']

    def test_unknown_file_triggers_full_suite(self):
        tests = map_changes_to_tests(['README.md'])
        assert tests == ['all']

    def test_multiple_changes_union_of_tests(self):
        tests = map_changes_to_tests(['src/pricing.py', 'src/inventory.py'])
        assert 'tests/test_pricing.py' in tests
        assert 'tests/test_cart.py' in tests
        assert 'tests/test_inventory.py' in tests

    def test_empty_changes_triggers_full_suite(self):
        tests = map_changes_to_tests([])
        assert tests == ['all']