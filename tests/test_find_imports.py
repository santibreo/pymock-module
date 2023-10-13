from mock_module import find_imports


def test_not_found_modules() -> None:
    expected = [
        "non_existent_inner_package",
        "non_existent_inner_module",
        "non_existent_module",
        "non_existent_package",
        "a_non_existent_package",
        "b_non_existent_package",
    ]
    observed = find_imports(".dummy", "tests")
    not_observed = set(expected) - set(observed)
    assert not not_observed, f"Not observed modules: {not_observed}"
    not_expected = set(observed) - set(expected)
    assert not not_expected, f"Not expected modules: {not_expected}"


def test_find_modules_not_listed() -> None:
    not_expected = [
        "itertools",
        "functools",
    ]
    observed = find_imports(".dummy", "tests")
    not_expected_observed = set(not_expected).intersection(set(observed))
    assert (
        not not_expected_observed
    ), f"Observed not expected modules: {not_expected_observed}"


def test_multiple_calls_same_return() -> None:
    expected = [
        #  "non_existent_inner_package",
        #  "non_existent_inner_module",
        "non_existent_module",
        "non_existent_package",
        "a_non_existent_package",
        "b_non_existent_package",
    ]
    observed_a = find_imports(".dummy", "tests")
    observed_b = find_imports(".dummy", "tests")
    not_observed = set(expected) - set(observed_a)
    assert not not_observed, f"Not observed at first call modules: {not_observed}"
    not_expected = set(observed_a) - set(expected)
    assert not not_expected, f"Not expected at first call modules: {not_expected}"
    observed_a_but_not_b = set(observed_a) - set(observed_b)
    assert (
        not observed_a_but_not_b
    ), f"Observed modules at first call but not at second: {observed_a_but_not_b}"
    observed_b_but_not_a = set(observed_b) - set(observed_a)
    assert (
        not observed_b_but_not_a
    ), f"Observed modules at second call but not at first: {observed_b_but_not_a}"


def test_find_not_installed_modules() -> None:
    expected = ['pandas']
    observed = find_imports('pandas')
    not_observed = set(expected) - set(observed)
    assert not not_observed, f"Not observed modules: {not_observed}"
    not_expected = set(observed) - set(expected)
    assert not not_expected, f"Not expected modules: {not_expected}"

