from typing import Any, Dict, List, Set

from cads_catalogue_api_service import constrictor

form: List[Dict[str, List[Any] | str]] = [
    {
        "details": {
            "groups": [{"values": ["Z"]}, {"values": ["T"]}],
        },
        "name": "param",
        "type": "StringListArrayWidget",
    },
    {
        "details": {"values": ["500", "850", "1000"]},
        "name": "level",
        "type": "StringListWidget",
    },
    {
        "details": {"values": ["24", "36", "48"]},
        "name": "step",
        "type": "StringListWidget",
    },
    {
        "details": {"values": ["1", "2", "3"]},
        "name": "number",
        "type": "StringChoiceWidget",
    },
]

parsed_form: Dict[str, Set[Any]] = {
    "level": {"500", "850", "1000"},
    "param": {"Z", "T"},
    "step": {"24", "36", "48"},
    "number": {"1", "2", "3"},
}

valid_combinations: List[Dict[str, List[Any]]] = [
    {"level": ["500"], "param": ["Z", "T"], "step": ["24", "36", "48"]},
    {"level": ["1000"], "param": ["Z"], "step": ["24", "48"]},
    {"level": ["850"], "param": ["T"], "step": ["36", "48"]},
]

parsed_valid_combinations: List[Dict[str, Set[Any]]] = [
    {"level": {"500"}, "param": {"Z", "T"}, "step": {"24", "36", "48"}},
    {"level": {"1000"}, "param": {"Z"}, "step": {"24", "48"}},
    {"level": {"850"}, "param": {"T"}, "step": {"36", "48"}},
]

selections: List[Dict[str, List[Any]]] = [
    {},  # 0
    {"number": ["1", "2"]},  # 1
    {"level": ["850"], "param": ["Z"]},  # 2
    {"level": ["850"], "param": ["Z"], "number": ["1", "2"]},  # 3
    {"level": ["850"]},  # 4
    {"level": ["850"], "number": "1"},  # 5
    {"level": ["1000"], "step": ["24"]},  # 6
    {"level": ["850", "1000"], "param": ["T", "Z"]},  # 7
    {"level": ["850"], "param": ["T"], "step": ["48", "36"], "number": "1"},  # 8
    {
        "level": ["850"],
        "param": ["T"],
        "step": ["48", "36"],
        "number": ["1", "2", "3"],
    },  # 9
    {
        "level": ["1000", "850", "500"],
        "param": ["T", "Z"],
        "step": ["48", "36", "24"],
        "number": ["1", "2", "3"],
    },  # 10
]

parsed_selections: List[Dict[str, Set[Any]]] = [
    {},  # 0
    {"number": {"1", "2"}},  # 1
    {"level": {"850"}, "param": {"Z"}},  # 2
    {"level": {"850"}, "param": {"Z"}, "number": {"1", "2"}},  # 3
    {"level": {"850"}},  # 4
    {"level": {"850"}, "number": {"1"}},  # 5
    {"level": {"1000"}, "step": {"24"}},  # 6
    {"level": {"850", "1000"}, "param": {"T", "Z"}},  # 7
    {"level": {"850"}, "param": {"T"}, "step": {"48", "36"}, "number": {"1"}},  # 8
    {
        "level": {"850"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 9
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 10
]

expected_possible_values: List[Dict[str, Set[Any]]] = [
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 0
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 1
    {},  # 2
    {},  # 3
    {
        "level": {"850"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 4
    {
        "level": {"850"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 5
    {
        "level": {"1000"},
        "param": {"Z"},
        "step": {"24", "48"},
        "number": {"1", "2", "3"},
    },  # 6
    {
        "level": {"850", "1000"},
        "param": {"T", "Z"},
        "step": {"24", "48", "36"},
        "number": {"1", "2", "3"},
    },  # 7
    {
        "level": {"850"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 8
    {
        "level": {"850"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 9
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 10
]

expected_form_states: List[Dict[str, Set[Any]]] = [
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 0
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 1
    {"level": {"1000", "500"}, "param": {"T"}},  # 2
    {"level": {"1000", "500"}, "param": {"T"}},  # 3
    {
        "level": {"850", "1000", "500"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 4
    {
        "level": {"850", "1000", "500"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 5
    {
        "level": {"1000", "500"},
        "param": {"Z"},
        "step": {"24", "48"},
        "number": {"1", "2", "3"},
    },  # 6
    {
        "level": {"500", "850", "1000"},
        "param": {"T", "Z"},
        "step": {"24", "48", "36"},
        "number": {"1", "2", "3"},
    },  # 7
    {
        "level": {"850", "500"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 8
    {
        "level": {"850", "500"},
        "param": {"T"},
        "step": {"48", "36"},
        "number": {"1", "2", "3"},
    },  # 9
    {
        "level": {"1000", "850", "500"},
        "param": {"T", "Z"},
        "step": {"48", "36", "24"},
        "number": {"1", "2", "3"},
    },  # 10
]


def test_get_possible_values() -> None:
    for i in range(len(parsed_selections)):
        result = constrictor.get_possible_values(
            parsed_form,
            parsed_selections[i],
            parsed_valid_combinations,
        )

        for key, value in expected_possible_values[i].items():
            try:
                assert set(value) == set(result[key])
            except AssertionError:
                print(
                    f"Iteration number {i} of {test_get_possible_values.__name__}() failed!"
                )
                raise AssertionError


def test_get_form_state() -> None:
    for i in range(len(parsed_selections)):
        result = constrictor.get_form_state(
            parsed_form,
            parsed_selections[i],
            parsed_valid_combinations,
        )

        for key, value in result.items():
            try:
                assert set(value) == expected_form_states[i][key]
            except AssertionError:
                print(
                    f"Iteration number {i} of {test_get_form_state.__name__}() failed!"
                )
                raise AssertionError


def test_apply_constraints() -> None:
    for i in range(len(expected_form_states)):
        result = constrictor.apply_constraints(
            parsed_form,
            parsed_valid_combinations,
            parsed_selections[i],
        )

        try:
            for key, value in result.items():
                assert set(value) == expected_form_states[i][key]
        except AssertionError:
            print(
                f"Iteration number {i} of "
                f"{test_apply_constraints.__name__}() failed!"
            )
            raise AssertionError


def test_parse_valid_combinations() -> None:
    assert parsed_valid_combinations == constrictor.parse_valid_combinations(
        valid_combinations
    )
    assert [{}] == constrictor.parse_valid_combinations([{}])


def test_parse_form() -> None:
    assert parsed_form == constrictor.parse_form(form)
    assert {} == constrictor.parse_form([])


def test_parse_selection() -> None:
    for i in range(len(selections)):
        try:
            assert parsed_selections[i] == constrictor.parse_selection(selections[i])
        except AssertionError:
            print(
                f"Iteration number {i} of " f"{test_parse_selection.__name__}() failed!"
            )
            raise AssertionError
