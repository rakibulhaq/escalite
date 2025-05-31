from escalite.formatters.dict_table_formatter import DictTableFormatter


def test_dict_table_formatter():
    formatter = DictTableFormatter()
    data = {"Name": "Alice", "Age": 30, "Country": "Wonderland"}
    expected = (
        "Key     | Value     \n"
        "--------+-----------\n"
        "Name    | Alice     \n"
        "Age     | 30        \n"
        "Country | Wonderland"
    )
    result = formatter.format(data)
    assert [line.rstrip() for line in result.splitlines()] == [line.rstrip() for line in expected.splitlines()]
