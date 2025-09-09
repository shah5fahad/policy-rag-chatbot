import os
import re
from typing import Dict, Tuple


def parse_model_file(file_path: str) -> Tuple[str, str, Dict[str, Tuple[str, bool]]]:
    with open(file_path, "r") as f:
        content = f.read()

    # Find class name
    class_match = re.search(r"class (\w+)\(BaseModel\):", content)
    class_name = class_match.group(1) if class_match else None

    # Find table name
    table_match = re.search(r'__tablename__ = "(\w+)"', content)
    table_name = table_match.group(1) if table_match else None

    # Find fields
    fields = {}
    # Match field = Column(Type(...), ...)
    field_pattern = re.compile(r"(\w+) = Column\(([^,]+),?\s*(.*)\)", re.MULTILINE)
    for match in field_pattern.finditer(content):
        field_name = match.group(1)
        type_part = match.group(2).strip()
        options = match.group(3)

        # Extract type
        type_match = re.match(r"(\w+)\(", type_part)
        if type_match:
            col_type = type_match.group(1)
        else:
            col_type = type_part

        # Extract nullable
        nullable = True
        if "nullable=False" in options or "nullable = False" in options:
            nullable = False

        fields[field_name] = (col_type, nullable)

    return class_name, table_name, fields


def map_sqlalchemy_to_pydantic(sql_type: str) -> str:
    """Map SQLAlchemy type to Pydantic type."""
    mapping = {
        "String": "str",
        "Text": "str",
        "Integer": "int",
        "Boolean": "bool",
        "Numeric": "float",
        "Date": "date",
        "JSON": "Dict[str, Any]",
        "ForeignKey": "int",  # Assuming id is int
    }
    return mapping.get(sql_type, "str")


def generate_repository(entity_name: str, class_name: str, file_path: str):
    content = f"""from ..base import BaseRepository
from ._model import {class_name}


class {class_name}Repository(BaseRepository):
    def __init__(self):
        super().__init__({class_name})

"""
    with open(file_path, "w") as f:
        f.write(content)


def generate_service(entity_name: str, class_name: str, file_path: str):
    content = f"""from ..base import BaseService
from ._repository import {class_name}Repository


class {class_name}Service(BaseService):
    def __init__(self):
        super().__init__({class_name}Repository)

"""
    with open(file_path, "w") as f:
        f.write(content)


def generate_controller(entity_name: str, class_name: str, file_path: str):
    content = f"""from ..base import BaseController
from ._schema import {class_name}Schema
from ._service import {class_name}Service


class {class_name}Controller(BaseController[{class_name}Schema]):
    def __init__(self):
        super().__init__({class_name}Service, {class_name}Schema)

"""
    with open(file_path, "w") as f:
        f.write(content)


def generate_schema(
    entity_name: str,
    class_name: str,
    fields: Dict[str, Tuple[str, bool]],
    file_path: str,
):
    imports = "from typing import Any, Dict, Optional\n\n"
    if any("date" in map_sqlalchemy_to_pydantic(t) for t, _ in fields.values()):
        imports = "from datetime import date\n" + imports

    content = imports
    content += f"""from ..base import BaseSchema


class {class_name}Schema(BaseSchema):
"""
    for field_name, (sql_type, nullable) in fields.items():
        pydantic_type = map_sqlalchemy_to_pydantic(sql_type)
        if nullable:
            pydantic_type = f"Optional[{pydantic_type}]"
        content += f"    {field_name}: {pydantic_type}\n"

    with open(file_path, "w") as f:
        f.write(content)


def update_init(entity_dir: str):
    init_path = os.path.join(entity_dir, "__init__.py")
    content = """from ._controller import *
from ._model import *
from ._repository import *
from ._schema import *
from ._service import *

"""
    with open(init_path, "w") as f:
        f.write(content)


def main():
    entities_dir = "src/entities"
    entities = [
        d
        for d in os.listdir(entities_dir)
        if os.path.isdir(os.path.join(entities_dir, d)) and d not in ["base", "test"]
    ]

    for entity in entities:
        entity_dir = os.path.join(entities_dir, entity)
        model_file = os.path.join(entity_dir, "_model.py")
        service_file = os.path.join(entity_dir, "_service.py")

        if os.path.exists(model_file) and not os.path.exists(service_file):
            print(f"Generating files for {entity}")

            class_name, table_name, fields = parse_model_file(model_file)
            print(
                f"Parsed {entity}: class={class_name}, table={table_name}, fields={fields}"
            )
            if not class_name:
                print(f"Could not parse class name for {entity}")
                continue

            # Generate repository
            generate_repository(
                entity, class_name, os.path.join(entity_dir, "_repository.py")
            )

            # Generate service
            generate_service(
                entity, class_name, os.path.join(entity_dir, "_service.py")
            )

            # Generate controller
            generate_controller(
                entity, class_name, os.path.join(entity_dir, "_controller.py")
            )

            # Generate schema
            generate_schema(
                entity, class_name, fields, os.path.join(entity_dir, "_schema.py")
            )

            # Update __init__.py
            update_init(entity_dir)

            print(f"Generated files for {entity}")


if __name__ == "__main__":
    main()
