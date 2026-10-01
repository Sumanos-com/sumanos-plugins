"""Add, update, or remove Suma MCP servers in Hermes' config.yaml."""

import argparse

from __init__ import materialize_connections, remove_connection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    add = commands.add_parser("add", help="add or update one named connection")
    add.add_argument("--name", required=True)
    add.add_argument("--environment", choices=("production", "development"), required=True)
    add.add_argument("--agent-id", required=True)
    add.add_argument("--key-env", required=True, help="environment variable name, not its value")
    remove = commands.add_parser("remove", help="remove one named connection")
    remove.add_argument("--name", required=True)
    args = parser.parse_args()

    from hermes_cli.config import read_raw_config, save_config

    config = read_raw_config()
    if args.action == "add":
        updated = materialize_connections(
            config,
            [{
                "name": args.name,
                "environment": args.environment,
                "agentId": args.agent_id,
                "keyEnv": args.key_env,
            }],
        )
    else:
        updated = remove_connection(config, args.name)
    save_config(updated)
    print(f"Suma connection {args.name!r} {('updated' if args.action == 'add' else 'removed')}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
