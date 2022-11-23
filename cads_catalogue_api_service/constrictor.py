"""Main module of the request-constraints API."""
import urllib
from typing import Any, Dict, List, Set

import cads_catalogue.database
import requests

from . import config, constrictor


def ensure_list(v):
    if not isinstance(v, list | tuple):
        v = [v]
    return v


def parse_valid_combinations(
    valid_combinations: List[Dict[str, List[Any]]]
) -> List[Dict[str, Set[Any]]]:
    """
    Parse valid combinations for a given dataset. Convert Dict[str, List[Any]] into Dict[str, Set[Any]].

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
            field_values = ensure_list(field_values)
            parsed_valid_combination[field_name] = set(field_values)
        result.append(parsed_valid_combination)
    return result


def parse_selection(selection: Dict[str, List[Any]]) -> Dict[str, Set[Any]]:
    """
    Parse current selection and convert Dict[str, List[Any]] into Dict[str, Set[Any]].

    :param selection: a dictionary containing the current selection
    :type: Dict[str, List[Any]]

    :rtype: Dict[str, Set[Any]]:
    :return: a Dict[str, Set[Any]] containing the current selection.
    """
    result = {}
    for field_name, field_values in selection.items():
        field_values = ensure_list(field_values)
        result[field_name] = set(field_values)
    return result


def apply_constraints(
    form: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
    selection: Dict[str, Set[Any]],
) -> Dict[str, List[Any]]:
    """
    Apply dataset constraints to the current selection.

    :param form: a dictionary of all selectable values
    grouped by field name
    :param valid_combinations: a list of all valid combinations
    :param selection: a dictionary containing the current selection
    :return: a dictionary containing all values that should be left
    active for selection, in JSON format
    """
    return format_to_json(get_form_state(form, selection, valid_combinations))


def get_possible_values(
    form: Dict[str, Set[Any]],
    selection: Dict[str, Set[Any]],
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

    :param form: a dict of all selectable fields and values
    e.g. form = {
        "level": {"500", "850", "1000"},
        "param": {"Z", "T"},
        "step": {"24", "36", "48"},
        "number": {"1", "2", "3"}
    }
    :type: dict[str, Set[Any]]:

    :param valid_combinations: a list of dictionaries representing
    all valid combinations for a specific dataset
    e.g. valid_combinations = [
        {"level": {"500"}, "param": {"Z", "T"}, "step": {"24", "36", "48"}},
        {"level": {"1000"}, "param": {"Z"}, "step": {"24", "48"}},
        {"level": {"850"}, "param": {"T"}, "step": {"36", "48"}},
    ]
    :type: list[dict[str, Set[Any]]]:

    :param selection: a dictionary containing the current selection
    e.g. selection = {
        "param": {"T"},
        "level": {"850", "500"},
        "step": {"36"}
    }
    :type: dict[str, Set[Any]]:

    :rtype: Dict[str, Set[Any]]
    :return: a dictionary containing all possible values given the current selection
    e.g.
    {'level': {'500', '850'}, 'param': {'T', 'Z'}, 'step': {'24', '36', '48'}}

    """
    result: Dict[str, Set[Any]] = {}
    for valid_combination in valid_combinations:
        ok = True
        for field_name, selected_values in selection.items():
            if field_name in valid_combination.keys():
                if len(selected_values & valid_combination[field_name]) == 0:
                    ok = False
                    break
            else:
                ok = False
        if ok:
            for field_name, valid_values in valid_combination.items():
                current = result.setdefault(field_name, set())
                current |= set(valid_values)
    if result:
        result.update(get_always_valid_params(form, valid_combinations))
    return result


def format_to_json(result: Dict[str, Set[Any]]) -> Dict[str, List[Any]]:
    """
    Convert Dict[str, Set[Any]] into Dict[str, List[Any]].

    :param result: Dict[str, Set[Any]] containing a possible form state
    :type: dict[str, Set[Any]]:

    :rtype: Dict[str, List[Any]]
    :return: the same values in Dict[str, List[Any]] format

    """
    return {k: list(v) for (k, v) in result.items()}


def get_form_state(
    form: Dict[str, Set[Any]],
    selection: Dict[str, Set[Any]],
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

    :param form: a dict of all selectable fields and values
    e.g. form = {
        "level": {"500", "850", "1000"},
        "param": {"Z", "T"},
        "step": {"24", "36", "48"},
        "number": {"1", "2", "3"}
    }
    :type: dict[str, Set[Any]]:

    :param valid_combinations: a list of dictionaries representing
    all valid combinations for a specific dataset
    e.g. valid_combinations = [
        {"level": {"500"}, "param": {"Z", "T"}, "step": {"24", "36", "48"}},
        {"level": {"1000"}, "param": {"Z"}, "step": {"24", "48"}},
        {"level": {"850"}, "param": {"T"}, "step": {"36", "48"}},
    ]
    :type: list[dict[str, Set[Any]]]:

    :param selection: a dictionary containing the current selection
    e.g. selection = {
        "param": {"T"},
        "level": {"850", "500"},
        "step": {"36"}
    }
    :type: dict[str, Set[Any]]:

    :rtype: Dict[str, Set[Any]]
    :return: a dictionary containing all form values to be left active given the current selection

    e.g.
    {'level': {'500', '850'}, 'param': {'T', 'Z'}, 'step': {'24', '36', '48'}}

    """
    result: Dict[str, Set[Any]] = {}
    for name in form:
        sub_selection = selection.copy()
        if name in sub_selection:
            sub_selection.pop(name)
        sub_results = get_possible_values(form, sub_selection, valid_combinations)
        result[name] = sub_results.setdefault(name, set())
    return result


def get_always_valid_params(
    form: Dict[str, Set[Any]],
    valid_combinations: List[Dict[str, Set[Any]]],
) -> Dict[str, Set[Any]]:
    """
    Get always valid field and values.

    :param form: a dict of all selectable fields and values
    e.g. form = {
        "level": {"500", "850", "1000"},
        "param": {"Z", "T"},
        "step": {"24", "36", "48"},
        "number": {"1", "2", "3"}
    }
    :type: dict[str, Set[Any]]:

    :param valid_combinations: a list of dictionaries representing
    all valid combinations for a specific dataset
    e.g. valid_combinations = [
        {"level": {"500"}, "param": {"Z", "T"}, "step": {"24", "36", "48"}},
        {"level": {"1000"}, "param": {"Z"}, "step": {"24", "48"}},
        {"level": {"850"}, "param": {"T"}, "step": {"36", "48"}},
    ]
    :type: list[dict[str, Set[Any]]]:

    :rtype: Dict[str, Set[Any]]
    :return: A dictionary containing fields and values that are not constrained (i.e. they are always valid)

    """
    result: Dict[str, Set[Any]] = {}
    for field_name, field_values in form.items():
        if field_name not in valid_combinations[0].keys():
            result.setdefault(field_name, field_values)
    return result


def parse_form(form: List[Dict[str, Any]]) -> Dict[str, set]:
    """
    Parse the from for a given dataset extracting the information on the possible selections.

    :param form: a dictionary containing
    all possible selections in JSON format
    :type: Dict[str, List[Any]]

    :rtype: Dict[str, Set[Any]]:
    :return: a Dict[str, Set[Any]] containing all possible selections.
    """
    selections = {}
    for parameter in form:
        if parameter["type"] in ("StringListWidget", "StringChoiceWidget"):
            values = parameter["details"]["values"]
            values = ensure_list(values)
            selections[parameter["name"]] = set(values)
        elif parameter["type"] == "StringListArrayWidget":
            selections[parameter["name"]] = {}
            selections_p: Set[str] = set([])
            for sub_parameter in parameter["details"]["groups"]:
                values = ensure_list(sub_parameter["values"])
                selections_p = selections_p | set(values)
            selections[parameter["name"]] = selections_p
        else:
            pass
    return selections


def lookup_dataset_by_id(
    id: str,
) -> List[str]:
    session_obj = cads_catalogue.database.ensure_session_obj(None)
    resource = cads_catalogue.database.Resource
    with session_obj() as session:
        query = session.query(resource)
        out = query.filter(resource.resource_uid == id).one()
    return out


def validate_constraints(
    collection_id: str, selection: Dict[str, List[str]]
) -> Dict[str, List[str]]:

    settings = config.Settings()
    storage_url = settings.document_storage_url
    timeout = settings.document_storage_access_timeout

    dataset = lookup_dataset_by_id(collection_id)

    form_url = urllib.parse.urljoin(storage_url, dataset.form)
    raw_form = requests.get(form_url, timeout=timeout).json()
    form = constrictor.parse_form(raw_form)

    valid_combinations_url = urllib.parse.urljoin(storage_url, dataset.constraints)
    raw_valid_combinations = requests.get(
        valid_combinations_url, timeout=timeout
    ).json()
    valid_combinations = constrictor.parse_valid_combinations(raw_valid_combinations)

    selection = constrictor.parse_selection(selection)

    return constrictor.apply_constraints(form, valid_combinations, selection)
