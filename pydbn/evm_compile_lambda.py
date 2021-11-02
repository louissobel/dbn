import json
import base64

import parser
import evm_compiler

def handler(event, context):
    
    body = event.get('body')
    if body is None:
        return unhandled_error(400, 'no body provided!')

    if event.get('isBase64Encoded'):
        body = base64.b64decode(body).decode("utf-8") 

    try:
        request = json.loads(body)
    except json.JSONDecodeError as e:
        return unhandled_error(400, 'error parsing body as json: ' + str(e))


    dbn_script = request.get('code')
    if dbn_script is None:
        return unhandled_error(400, '"code" must be provided in input')

    input_metadata = request.get('metadata')
    if input_metadata is None:
        return unhandled_error(400, '"metadata" must be provided in input (even if empty dict)')

    metadata = evm_compiler.Metadata(
        owning_contract=input_metadata.get('owning_contract'),
        description=input_metadata.get('description'),
    )

    try:
        tokens = parser.tokenize(dbn_script)
        dbn_ast = parser.parse(tokens)
    except parser.ParseError as e:
        return handled_error('parse', e.message, e.line)
    # except Exception as e:
    #     return unhandled_error(500, 'unhandled error during parse: ' + str(e))

    try:
        compiler = evm_compiler.DBNEVMCompiler(verbose=True)
        compilation = compiler.compile(
            dbn_ast,
            metadata=metadata,
        )
    except ValueError as e:
        return unhandled_error(500, 'compile error: ' + str(e))

    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'result': compilation,
        }),
    }


# TODO: position?
def handled_error(type_, message, line_number):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': False,
            'error': {
                'type': type_,
                'message': message,
                'line_number': line_number,
            }
        })
    }

def unhandled_error(code, message):
    return {
        'statusCode': code,
        'body': message + "\n"
    }
