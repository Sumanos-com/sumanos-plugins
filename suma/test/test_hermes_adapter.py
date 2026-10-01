import copy
import importlib.util
import unittest
from pathlib import Path


ADAPTER_PATH = Path(__file__).parents[1] / "adapters" / "hermes" / "__init__.py"
spec = importlib.util.spec_from_file_location("suma_hermes_adapter", ADAPTER_PATH)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class FakePluginContext:
    def __init__(self):
        self.skills = []
        self.private_calls = []

    def register_skill(self, *args, **kwargs):
        self.skills.append((args, kwargs))

    def register_mcp_server(self, *args, **kwargs):
        self.private_calls.append((args, kwargs))


class HermesConnectionContractTests(unittest.TestCase):
    def setUp(self):
        self.first = {
            "name": "Acme Production",
            "environment": "production",
            "agentId": "agent-prod-1",
            "keyEnv": "ACME_PROD_KEY",
        }
        self.second = {
            "name": "Acme Development",
            "environment": "development",
            "agentId": "agent-dev-2",
            "keyEnv": "ACME_DEV_KEY",
        }

    def test_multiple_connections_are_isolated_and_use_exact_endpoints_and_env_refs(self):
        config = {"model": {"name": "keep-me"}, "mcp_servers": {"unrelated": {"url": "https://other"}}}
        result = adapter.materialize_connections(config, [self.first, self.second])
        servers = result["mcp_servers"]

        self.assertEqual(len(servers), 3)
        prod = next(
            server
            for server in servers.values()
            if server.get("suma", {}).get("connection_name") == "acme production"
        )
        dev = next(
            server
            for server in servers.values()
            if server.get("suma", {}).get("connection_name") == "acme development"
        )
        self.assertEqual(prod["url"], "https://app.sumanos.com/mcp/authoring/agents/agent-prod-1")
        self.assertEqual(dev["url"], "https://development.sumanos.com/mcp/authoring/agents/agent-dev-2")
        self.assertEqual(prod["headers"]["Authorization"], "Bearer ${ACME_PROD_KEY}")
        self.assertEqual(dev["headers"]["Authorization"], "Bearer ${ACME_DEV_KEY}")
        self.assertEqual(
            prod["suma"],
            {
                "schema": "suma.hermes-connection/v1",
                "adapter": "suma-hermes",
                "connection_name": "acme production",
                "environment": "production",
                "agentId": "agent-prod-1",
                "keyEnv": "ACME_PROD_KEY",
            },
        )
        self.assertEqual(set(prod["headers"]), {"Authorization"})
        self.assertNotEqual(prod["headers"]["Authorization"], dev["headers"]["Authorization"])
        self.assertEqual(result["model"], {"name": "keep-me"})
        self.assertEqual(servers["unrelated"], {"url": "https://other"})

    def test_add_update_remove_are_idempotent(self):
        initial = {"mcp_servers": {"keep": {"enabled": False}}}
        added = adapter.materialize_connections(initial, [self.first])
        self.assertEqual(adapter.materialize_connections(added, [self.first]), added)
        self.assertEqual(
            adapter.materialize_connections(added, [{**self.first, "name": "acme production"}]),
            added,
        )

        changed = {**self.first, "agentId": "agent-prod-new"}
        updated = adapter.materialize_connections(added, [changed])
        self.assertNotIn("agent-prod-1", str(updated))
        self.assertIn("agent-prod-new", str(updated))
        removed = adapter.remove_connection(updated, self.first["name"])
        self.assertEqual(removed, {"mcp_servers": {"keep": {"enabled": False}}})
        self.assertEqual(adapter.remove_connection(removed, self.first["name"]), removed)

    def test_sequential_slug_colliding_names_get_distinct_servers_without_replacement(self):
        initial = {"mcp_servers": {}}
        first_added = adapter.materialize_connections(initial, [self.first])
        second_descriptor = {
            **self.second,
            "name": "Acme-Production",
            "agentId": "agent-prod-alt",
            "keyEnv": "ACME_ALT_KEY",
        }

        both_added = adapter.materialize_connections(first_added, [second_descriptor])

        servers = both_added["mcp_servers"]
        self.assertEqual(len(servers), 2)
        self.assertIn("agent-prod-1", str(servers))
        self.assertIn("agent-prod-alt", str(servers))

    def test_remove_refuses_a_server_that_only_resembles_suma(self):
        server_name = next(iter(adapter.materialize_connections({}, [self.first])["mcp_servers"]))
        unrelated = {
            "mcp_servers": {
                server_name: {
                    "url": "https://other.example/mcp/authoring/agents/agent-prod-1",
                    "headers": {"Authorization": "Bearer ${OTHER_KEY}"},
                    "purpose": "unrelated service",
                }
            }
        }
        snapshot = copy.deepcopy(unrelated)
        wrongly_owned = copy.deepcopy(unrelated)
        wrongly_owned["mcp_servers"][server_name]["suma"] = {
            "schema": "suma.hermes-connection/v1",
            "adapter": "suma-hermes",
            "connection_name": "different connection",
            "environment": "production",
            "agentId": "agent-prod-1",
            "keyEnv": "OTHER_KEY",
        }

        for config in (unrelated, wrongly_owned):
            before = copy.deepcopy(config)
            with self.assertRaises(ValueError):
                adapter.remove_connection(config, self.first["name"])
            self.assertEqual(config, before)
        self.assertEqual(unrelated, snapshot)

    def test_invalid_or_duplicate_descriptors_fail_without_mutating_input(self):
        original = {"mcp_servers": {"keep": {"url": "https://other"}}}
        snapshot = copy.deepcopy(original)
        invalid = [
            [{**self.first, "environment": "staging"}],
            [{**self.first, "environment": []}],
            [{**self.first, "agentId": "../other"}],
            [{**self.first, "keyEnv": "bad-name"}],
            [self.first, {**self.second, "name": self.first["name"]}],
            [self.first, {**self.second, "agentId": self.first["agentId"]}],
            [self.first, {**self.second, "keyEnv": self.first["keyEnv"]}],
        ]
        for descriptors in invalid:
            with self.subTest(descriptors=descriptors):
                with self.assertRaises(ValueError):
                    adapter.materialize_connections(original, descriptors)
                self.assertEqual(original, snapshot)

    def test_sequential_add_enforces_managed_agent_and_key_uniqueness(self):
        original = adapter.materialize_connections({}, [self.first])
        snapshot = copy.deepcopy(original)
        for duplicate in (
            {**self.second, "agentId": self.first["agentId"]},
            {**self.second, "keyEnv": self.first["keyEnv"]},
        ):
            with self.subTest(duplicate=duplicate):
                with self.assertRaises(ValueError):
                    adapter.materialize_connections(original, [duplicate])
                self.assertEqual(original, snapshot)

    def test_unrelated_server_id_collision_fails_without_mutation(self):
        expected_id = next(iter(adapter.materialize_connections({}, [self.first])["mcp_servers"]))
        unrelated = {"mcp_servers": {expected_id: {"url": "https://unrelated.example/mcp"}}}
        snapshot = copy.deepcopy(unrelated)

        with self.assertRaises(ValueError):
            adapter.materialize_connections(unrelated, [self.first])
        self.assertEqual(unrelated, snapshot)

    def test_registers_all_shipped_skills_through_public_context(self):
        ctx = FakePluginContext()
        adapter.register(ctx)
        names = [args[0] for args, _ in ctx.skills]
        self.assertEqual(
            names,
            ["suma-playbook", "sumanos-capabilities", "agent-recipes", "writing-agent-souls"],
        )
        self.assertEqual(ctx.private_calls, [])
        for args, _ in ctx.skills:
            self.assertTrue(Path(args[1]).is_file())


if __name__ == "__main__":
    unittest.main()
