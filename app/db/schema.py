from sqlalchemy import inspect
from sqlalchemy.orm import Session

def get_schema_description(db: Session) -> str:
    """
    Extracts all table names and their columns from the connected
    PostgreSQL database and returns a formatted string.
    """

    inspector = inspect(db.get_bind())

    schema_output = []

    # Get all table names
    tables = inspector.get_table_names()

    for table in tables:
        table_block = f"Table: {table}"

        columns = inspector.get_columns(table)

        column_lines = []
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            column_lines.append(f"  - {col_name} ({col_type})")

        # Combine table + columns
        full_table_block = table_block + "\n" + "\n".join(column_lines)
        schema_output.append(full_table_block)

    # Join all tables into one string
    return "\n\n".join(schema_output)