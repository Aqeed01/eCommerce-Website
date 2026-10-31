"""One-time setup: copy the demo data into a shared TiDB database and point the live site at it.

Run it from the project folder, in a terminal where you can type:

    python scripts/setup_tidb.py

You will be asked for the TiDB host, port, user and password (the password is not shown or saved).
Create an empty database first in TiDB Cloud (SQL Editor):  CREATE DATABASE shopnonstop;

What it does:
  1. connects to the database and checks the connection,
  2. creates the tables and copies the bundled demo data into them (replacing anything already there),
  3. stores the connection as DATABASE_URL on the Vercel project (production).
"""
import getpass
import os
import subprocess
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_FILE = os.path.join(ROOT, "instance/ecommerce.db")
BATCH = 400


def fill_gaps(table, row):
    """An older row may leave a required column empty: use the column's default (0 for numbers, '' for text)."""
    for col in table.columns:
        if row.get(col.name) is None and not col.nullable and not col.primary_key:
            default = col.default.arg if (col.default is not None and getattr(col.default, "is_scalar", False)) else None
            if default is None:
                kind = col.type.python_type if hasattr(col.type, "python_type") else str
                default = 0 if kind in (int, float) else ("" if kind is str else None)
            row[col.name] = default
    return row


def ask(prompt, default=""):
    value = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return value or default


def main():
    print("Move ShopNonstop to a shared TiDB database\n")
    host = ask("TiDB host (looks like gateway01.us-east-1.prod.aws.tidbcloud.com)")
    port = ask("Port", "4000")
    user = ask("Username")
    password = getpass.getpass("Password (not shown): ")
    database = ask("Database name", "shopnonstop")
    if not (host and user and password):
        sys.exit("Host, username and password are all required.")

    url = f"mysql+pymysql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{database}"
    os.environ["DATABASE_URL"] = url
    sys.path.insert(0, ROOT)

    from sqlalchemy import create_engine, text
    from app import app, db  # picks up DATABASE_URL, so db.engine is the TiDB database

    with app.app_context():
        target = db.engine
        with target.connect() as conn:
            print("Connected:", conn.execute(text("select version()")).scalar())

        source = create_engine(f"sqlite:///{SQLITE_FILE}")
        print("\nCreating tables ...")
        db.metadata.drop_all(target)
        db.metadata.create_all(target)

        print("Copying data ...")
        with source.connect() as src, target.begin() as dst:
            for table in db.metadata.sorted_tables:
                rows = [fill_gaps(table, dict(r)) for r in src.execute(table.select()).mappings()]
                for i in range(0, len(rows), BATCH):
                    dst.execute(table.insert(), rows[i:i + BATCH])
                print(f"  {table.name:<20} {len(rows):>5} rows")

        with target.connect() as conn:
            print("\nCheck (rows now in TiDB):")
            for table in db.metadata.sorted_tables:
                n = conn.execute(text(f"select count(*) from `{table.name}`")).scalar()
                print(f"  {table.name:<20} {n:>5}")

    print("\nStoring DATABASE_URL on Vercel (production) ...")
    result = subprocess.run(["vercel", "env", "add", "DATABASE_URL", "production", "--force", "--scope", "aqeed01s-projects"],
                            input=url, text=True, cwd=ROOT, shell=(os.name == "nt"))
    if result.returncode != 0:
        print("Vercel did not accept it; add DATABASE_URL by hand in the project's Environment Variables.")
    print("\nDone. Tell Claude it is finished and it will deploy and test the live site.")


if __name__ == "__main__":
    main()
