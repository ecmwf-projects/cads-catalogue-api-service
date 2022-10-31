"""Main module of the request-constraints API."""

from typing import Any, Dict, List, Set


def parse_valid_combinations(
    valid_combinations: List[Dict[str, List[Any]]]
) -> List[Dict[str, Set[Any]]]:
    """
    Parse valid combinations for a given dataset.

    :param valid_combinations: valid combinations in JSON format
    :type: List[Dict[str, List[Any]]]

    :rtype: list[Dict[str, Set[Any]]]:
    :return: list of Dict[str, Set[Any]] containing all valid combinations
    for a given dataset.

    """
    result = []
    for combination in valid_combinations:
        parsed_valid_combination = {}
        for field_name, field_values in combination.items():
            parsed_valid_combination[field_name] = set(field_values)
        result.append(parsed_valid_combination)
    return result


def parse_possible_selections(
    possible_selections: Dict[str, List[Any]]
) -> Dict[str, Set[Any]]:
    """
    Parse possible form selections for a given dataset.

    :param possible_selections: a dictionary containing
    all possible selections in JSON format
    :type: Dict[str, List[Any]]

    :rtype: Dict[str, Set[Any]]:
    :return: a Dict[str, Set[Any]] containing all possible selections.

    """
    result = {}
    for field_name, field_values in possible_selections.items():
        result[field_name] = set(field_values)
    return result


def parse_current_selection(
    current_selection: Dict[str, List[Any]]
) -> Dict[str, Set[Any]]:
    """
    Parse current selection.

    :param current_selection: a dictionary containing the current selection
    :type: Dict[str, List[Any]]

    :rtype: Dict[str, Set[Any]]:
    :return: a Dict[str, Set[Any]] containing the current selection.
    """
    result = {}
    for field_name, field_values in current_selection.items():
        result[field_name] = set(field_values)
    return result


def apply_constraints(
    possible_selections: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
    current_selection: Dict[str, Set[Any]],
) -> Dict[str, List[Any]]:
    """
    Apply dataset constraints to the current selection.

    :param possible_selections: a dictionary of all selectable values
    grouped by field name
    :param valid_combinations: a list of all valid combinations
    :param current_selection: a dictionary containing the current selection
    :return: a dictionary containing all values that should be left
    active for selection, in JSON format
    """
    return format_to_json(
        get_form_state(possible_selections, current_selection, valid_combinations)
    )


def get_possible_values(
    possible_selections: Dict[str, Set[Any]],
    current_selection: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
) -> Dict[str, Set[Any]]:
    """
    Get possible values given the current selection.

    Works only for enumerated fields, i.e. fields with values
    that must be selected one by one (no ranges).
    Checks the current selection against all valid combinations.
    A combination is valid if every field contains
    at least one value from the current selection.
    If a combination is valid, its values are added to the pool
    of valid values (i.e. those that can still be selected without
    running into an invalid request).

    :param possible_selections: a dict of all selectable fields and values
    e.g. possible_selections = {
        "level": ["500", "850", "1000"],
        "param": ["Z", "T"],
        "step": ["24", "36", "48"],
        "number": ["1", "2", "3"]
    }
    :type: dict[str, set[Any]]:

    :param valid_combinations: a list of dictionaries representing
    all valid combinations for a specific dataset
    e.g. valid_combinations = [
        {"level": {"500"}, "param": {"Z", "T"}, "step": {"24", "36", "48"}},
        {"level": {"1000"}, "param": {"Z"}, "step": {"24", "48"}},
        {"level": {"850"}, "param": {"T"}, "step": {"36", "48"}},
    ]
    :type: list[dict[str, set[Any]]]:

    :param current_selection: a dictionary containing the current selection
    e.g. current_selection = {
        "param": ["T"],
        "level": ["850", "500"],
        "step": ["36"]
    }
    :type: dict[str, set[Any]]:

    :rtype: Dict[str, Set[Any]]
    :return: a dictionary containing all possible values,
    i.e. those that can still be selected without running into
    an invalid request
    e.g.
    {'level': {'500', '850'}, 'param': {'T', 'Z'}, 'step': {'24', '36', '48'}}

    """
    result: Dict[str, Set[Any]] = {}
    for valid_combination in valid_combinations:
        ok = True
        for field_name, selected_values in current_selection.items():
            if field_name in valid_combination.keys():
                if len(selected_values & valid_combination[field_name]) == 0:
                    ok = False
                    break
        if ok:
            for field_name, valid_values in valid_combination.items():
                current = result.setdefault(field_name, set())
                current |= set(valid_values)
    if result:
        result.update(get_always_valid_params(possible_selections, valid_combinations))
    return result


def format_to_json(result: Dict[str, Set[Any]]) -> Dict[str, List[Any]]:
    """
    Convert Dict[str, Set[Any]] into Dict[str, List[Any]].

    :param result: Dict[str, Set[Any]] containing a possible form state
    :return: the equivalent set of

    """
    return {k: list(v) for (k, v) in result.items()}


def get_form_state(
    possible_selections: Dict[str, Set[Any]],
    current_selection: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
) -> Dict[str, Set[Any]]:
    """
    Compute the form state given the current selection.

    :param possible_selections:
    :param current_selection:
    :param valid_combinations:
    :return:

    """
    result: Dict[str, Set[Any]] = {}
    for name in possible_selections:
        sub_selection = current_selection.copy()
        if name in sub_selection:
            sub_selection.pop(name)
        sub_results = get_possible_values(
            possible_selections, sub_selection, valid_combinations
        )
        if sub_results:
            result[name] = sub_results[name]
    return result


def get_always_valid_params(
    possible_selections: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
) -> Dict[str, Set[Any]]:
    """
    After computing possible values, include unconstrained params.

    :param possible_selections:
    :param valid_combinations:
    :return:

    """
    result: Dict[str, Set[Any]] = {}
    for field_name, field_values in possible_selections.items():
        if field_name not in valid_combinations[0].keys():
            result.setdefault(field_name, field_values)
    return result
