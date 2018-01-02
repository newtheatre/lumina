from app import hello_arg

def test_hello():
    hello_result = hello_arg('Alice')
    assert hello_result['message'] == 'Hello Alice!'
