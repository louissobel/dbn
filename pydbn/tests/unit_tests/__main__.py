import tests.helper

tests.helper.run_modules([
    'tokenizer_tests',
    'parser_tests',
    'interpreter_tests',
    'load_adapter_tests',
], prefix='unit_tests')