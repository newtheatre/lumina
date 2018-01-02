from app import hello

def test_hello():
    hello_result = hello()
    assert hello_result['message'] == 'Hello World!'
