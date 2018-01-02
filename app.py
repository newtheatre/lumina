import os
from chalice import Chalice

app = Chalice(app_name='lumina', debug=True)


@app.route('/hello')
def hello() -> dict:
    return {'message': 'Hello World!'}


@app.route('/hello/{arg}')
def hello_arg(arg: str) -> dict:
    return {'message': f'Hello {arg}!'}


@app.route('/debug/log/{message}')
def debug_log(message: str) -> dict:
    from chalicelib import models

    log = models.LogModel(message)
    log.save()
    log.refresh()
    return {
        'uuid': log.uuid,
        'timestamp': log.timestamp.isoformat(),
        'message': log.message,
    }


@app.route('/debug/introspect')
def debug_introspect():
    return app.current_request.to_dict()


@app.route('/debug/stage')
def debug_stage() -> dict:
    from chalicelib import settings

    return {
        'stage_settings': settings.STAGE,
        'stage_env': os.environ['STAGE']
    }


@app.route('/debug/context')
def debug_stage_vars():
    return app.current_request.context


@app.route('/admin/migrate')
def admin_migrate() -> dict:
    from chalicelib import models
    count = models.create_tables()
    return {
        'status': 'success',
        'message': f'{count} tables created',
    }

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
