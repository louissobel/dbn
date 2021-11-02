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
    # Any other kind of error is system failure and we let it bubble

    try:
        compiler = evm_compiler.DBNEVMCompiler(verbose=True)
        compilation = compiler.compile(
            dbn_ast,
            metadata=metadata,
        )
    except evm_compiler.CompileError as e:
        return handled_error(
            'compile',
            e.message,
            e.line,
            related_line_number=e.related_line,
            line_number_in_message=e.line_number_in_message,
        )
    # Let anything else bubblw

    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'result': compilation,
        }),
    }


# TODO: position?
def handled_error(type_, message, line_number, related_line_number=None, line_number_in_message=False):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': False,
            'error': {
                'type': type_,
                'message': message,
                'line_number': line_number,
                'related_line_number': related_line_number,
                'line_number_in_message': line_number_in_message,
            }
        })
    }

def unhandled_error(code, message):
    return {
        'statusCode': code,
        'body': message + "\n"
    }
