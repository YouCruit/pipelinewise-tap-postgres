import unittest

from singer import get_logger, metadata

import tap_postgres
from tests.utils import (
    get_test_connection,
    ensure_test_table,
    get_test_connection_config,
)

LOGGER = get_logger()


def do_not_dump_catalog(catalog):
    pass


tap_postgres.dump_catalog = do_not_dump_catalog


class Conversions(unittest.TestCase):
    maxDiff = None
    table_name = "COW FEEDS"

    def setUp(self):
        table_spec = {
            "columns": [
                {"name": "int_range_col", "type": "int4range"},
            ],
            "name": Conversions.table_name,
        }

        ensure_test_table(table_spec)

    def test_catalog(self):
        conn_config = get_test_connection_config()
        streams = tap_postgres.do_discovery(conn_config)
        cow_streams = [s for s in streams if s["tap_stream_id"] == "public-COW FEEDS"]

        self.assertEqual(len(cow_streams), 1)
        stream_dict = cow_streams[0]
        stream_dict.get("metadata").sort(key=lambda md: md["breadcrumb"])

        # TODO fix it
        self.assertEqual(
            metadata.to_map(stream_dict.get("metadata")),
            {
                (): {
                    "is-view": False,
                    "table-key-properties": [],
                    "row-count": 0,
                    "schema-name": "public",
                    "database-name": "postgres",
                },
                ("properties", "int_range_col"): {
                    "sql-datatype": "int4range",
                    "selected-by-default": False,
                    "inclusion": "unsupported",
                },
                ("properties", "int_range_col_lower"): {
                    "sql-datatype": "int",
                    "selected-by-default": True,
                    "inclusion": "automatic",
                },
                ("properties", "int_range_col_upper"): {
                    "sql-datatype": "int",
                    "selected-by-default": True,
                    "inclusion": "automatic",
                },
            },
        )
