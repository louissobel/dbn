import json
import base64

import parser
import evm_compiler

def handler(event, context):
    
    body = event.get('body')
    if body is None:
        return error(400, 'no body provided!')

    if event.get('isBase64Encoded'):
        body = base64.b64decode(body).decode("utf-8") 

    try:
        request = json.loads(body)
    except json.JSONDecodeError as e:
        return error(400, 'error parsing body as json: ' + str(e))


    dbn_script = request.get('code')
    if dbn_script is None:
        return error(400, '"code" must be provided in input')

    input_metadata = request.get('metadata')
    if input_metadata is None:
        return error(400, '"metadata" must be provided in input (even if empty dict)')

    metadata = evm_compiler.Metadata(
        owning_contract=input_metadata.get('owning_contract'),
        description=input_metadata.get('description'),
    )

    try:
        tokens = parser.tokenize(dbn_script)
        dbn_ast = parser.parse(tokens)
    except ValueError as e:
        return error(500, 'parse error: ' + str(e))

    try:
        compiler = evm_compiler.DBNEVMCompiler(verbose=True)
        compilation = compiler.compile(
            dbn_ast,
            metadata=metadata,
        )
    except ValueError as v:
        return error(500, 'compile error: ' + str(e))

    return {
        'statusCode': 200,
        'body': compilation,
    }


def error(code, message):
    return {
        'statusCode': code,
        'body': message + "\n"
    }
