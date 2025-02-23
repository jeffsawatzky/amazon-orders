__copyright__ = "Copyright (c) 2024 Alex Laird"
__license__ = "MIT"

import json
import os
import sys
from datetime import datetime

from parameterized import parameterized

from tests.integrationtestcase import IntegrationTestCase

PRIVATE_RESOURCES_DIR = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),
                 "private-resources"))

private_json_file_data = []
if os.path.exists(PRIVATE_RESOURCES_DIR):
    for filename in os.listdir(PRIVATE_RESOURCES_DIR):
        if filename == ".gitignore" or filename.startswith("example-"):
            continue

        with open(os.path.join(PRIVATE_RESOURCES_DIR, filename), "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            private_json_file_data.append((filename, data))

env_json_data = []
if "AMAZON_ORDERS_INTEGRATION_TEST_JSON" in os.environ:
    data = json.loads(os.environ["AMAZON_ORDERS_INTEGRATION_TEST_JSON"])
    if not isinstance(data, list):
        print("AMAZON_ORDERS_INTEGRATION_TEST_JSON must be a list of JSON objects")

        sys.exit(1)

    i = 0
    for test in data:
        env_json_data.append((f"env_var_test_{i}", test))
        i += 1


class TestIntegrationJSON(IntegrationTestCase):
    """
    The two JSON files committed to "private-resources" are provided as examples of the syntax. Any other
    files created in "private-resources" will be ignored by ``.gitignore``. Alternatively, instead of files,
    this same JSON syntax can be provided as a list in the environment variable AMAZON_ORDERS_INTEGRATION_TEST_JSON.

    The starting JSON of a test description is:

    .. code:: json

        {
            "func": "<some_AmazonOrders_function>"
        }

    Field assertion values can be as follows:

    * Primitives and literals (ex. 23.43, "some string")
    * Dates formatted YYYY-MM-DD (ex. 2023-12-15)
    * isNone
    * isNotNone
    * Nested values (ex. a list / dict, if a corresponding list / object exists in the entity

    Details
    =======
    In a ``get_order`` test, any top-level field (other than ``func``) in the JSON will be asserted on
    the ``Order`` (including nested fields). So, for example, if we want to assert the ``Order`` was
    placed on 2023-12-15 by "John Doe", the minimal test would be:

    .. code:: json

        {
            "func": "get_order",
            "order_placed_date": "2023-12-15",
            "recipient": {
                "name": "John Doe"
            }
        }

    History
    =======
    In a ``get_order_history`` test, additional top-level fields are needed to define the test, and they are:

    .. code:: json

        {
            "year": <map to AmazonOrders.get_order_history(year)>,
            "start_index": <map to AmazonOrders.get_order_history(start_index)>,
            "full_details": <map to AmazonOrders.get_order_history(full_details)>,
            "orders_len": <the expected response list length>,
            "orders": {
                "3": {
                    # ... The Order at index 3
                },
                "7": {
                    # ... The Order at index 7
                }
            }
        }

    With this syntax, multiple ``Orders`` from the response can be asserted against. The indexed dictionaries under
    the ``orders`` key then match the assertion functionality when testing against a single order, meaning you
    define here the fields and values under the ``Order`` that you want to assert on.
    """

    @parameterized.expand(private_json_file_data + env_json_data, skip_on_empty=True)
    def test_json(self, testname, data):
        print(f"Info: Dynamic test is running from JSON {testname}")

        # GIVEN
        func = data.pop("func")

        if func == "get_order_history":
            order_len = data.pop("orders_len")
            orders_json = data.pop("orders")
            full_details = data.get("full_details")

            # WHEN
            orders = self.amazon_orders.get_order_history(**data)

            # THEN
            self.assertEqual(order_len, len(orders))
            for index, order_json in orders_json.items():
                order = orders[int(index)]
                self.assertEqual(order.full_details, full_details)
                self.assert_json_items(order, order_json)
        elif func == "get_order":
            order_json = data
            order_id = order_json["order_number"]

            # WHEN
            order = self.amazon_orders.get_order(order_id)

            # THEN
            self.assertEqual(order.full_details, True)
            self.assert_json_items(order, order_json)
        else:
            self.fail(
                f"Unknown function AmazonOrders. {func}, check JSON in test file {filename}")

    def assert_json_items(self, entity, json_dict):
        for json_key, json_value in json_dict.items():
            entity_attr = getattr(entity, json_key)
            if json_value == "isNone":
                self.assertIsNone(entity_attr)
            elif json_value == "isNotNone":
                self.assertIsNotNone(entity_attr)
            elif isinstance(json_value, list):
                i = 0
                for element in json_value:
                    self.assert_json_items(entity_attr[i], element)
                    i += 1
            elif isinstance(json_value, dict):
                self.assert_json_items(entity_attr, json_value)
            else:
                try:
                    self.assertEqual(
                        datetime.strptime(json_value, "%Y-%m-%d").date(), entity_attr)
                except (TypeError, ValueError):
                    self.assertEqual(json_value, entity_attr)
