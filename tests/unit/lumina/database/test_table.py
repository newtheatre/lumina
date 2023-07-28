import moto
from lumina.database import connection, table


@moto.mock_dynamodb
def test_create_tables():
    table.create_tables()
    tables = list(connection.get_dynamo_db().tables.all())
    assert len(tables) == 1
    assert tables[0].name == "LuminaMember-dev"
