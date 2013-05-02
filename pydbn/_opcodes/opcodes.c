#include <Python.h>

#define Dbn_UNPACK_OPCODE_ARGS() PyObject *interpreter; PyStringObject *arg; if (!PyArg_ParseTuple(args, "OS", &interpreter, &arg)) {return NULL;}

#define Dbn_ASSERT_MIN_STACK_DEPTH(stack, x) if (PyList_GET_SIZE(stack) < x) { PyErr_SetString(PyExc_RuntimeError, "Minimum stack depth not met"); return NULL;}

#define Dbn_RETURN_INTERPRETER() return Py_BuildValue("O", interpreter);

#define Dbn_BINARY_OP_PREFIX() Dbn_UNPACK_OPCODE_ARGS();PyObject *stack = Dbn_InterpreterGetAttr(interpreter, "stack"); Dbn_ASSERT_MIN_STACK_DEPTH(stack, 2); long top = Dbn_PopLong(stack); long top1 = Dbn_PopLong(stack);

/*********************************
 * Stack methods
 *********************************/

// Returns borrowed reference
// This is similar to how listpop is implemented in stdlib
static PyObject * _Dbn_StackPop(PyObject *stack) {
  PyObject *item;
  Py_ssize_t length = PyList_GET_SIZE(stack);
  if (length == 0) {
    PyErr_SetString(PyExc_IndexError, "Pop from empty list");
    return NULL;
  }
  item = PyList_GET_ITEM(stack, length - 1);
  // Delete the last item
  PyList_SetSlice(stack, length - 1, length, NULL);
  return item;
}

// Pops a long from the stack
// returns it
static long Dbn_PopLong(PyObject *stack) {
  PyObject *temp = _Dbn_StackPop(stack);
  return PyInt_AS_LONG(temp);
}

// Pushes a long onto the stack
// return the stack
static PyObject * Dbn_PushLong(PyObject *stack, long value) {
  PyObject *temp = PyInt_FromLong(value);
  PyList_Append(stack, temp);
  return stack;
}

// Pops a string from the stack (char *)
// returns it
static char * Dbn_PopString(PyObject *stack) {
  PyObject *temp = _Dbn_StackPop(stack);
  return PyString_AS_STRING(temp);
}

// Pushes a string onto the stack (char *)
// returns the stack
static PyObject * Dbn_PushString(PyObject *stack, char *string) {
  PyObject *temp = PyString_FromString(string);
  PyList_Append(stack, temp);
  return stack;
}


/*********************************
 * Interpreter methods
 *********************************/

// Returns the attribute given
// Borrowed reference
static PyObject * Dbn_InterpreterGetAttr(PyObject *interpreter, char *attr) {
  return PyObject_GetAttrString(interpreter, attr);
}

// Sets the given attribute
// returns the interpreter
static PyObject * Dbn_InterpreterSetAttr(PyObject *interpreter, char *attr, PyObject *value) {
  PyObject_SetAttrString(interpreter, attr, value);
  return interpreter;
}

// Sets the pointer attribute
static long Dbn_SetPointer(PyObject *interpreter, long value) {
  Dbn_InterpreterSetAttr(interpreter, "pointer", PyInt_FromLong(value));
  return value;
}

// Increments the pointer
static long Dbn_IncrementPointer(PyObject *interpreter) {
  PyObject *temp = Dbn_InterpreterGetAttr(interpreter, "pointer");
  long current = PyInt_AS_LONG(temp);
  return Dbn_SetPointer(interpreter, current + 1);
}

// Sets terminated attribute to True
static void Dbn_TerminateInterpreter(PyObject *interpreter) {
  Dbn_InterpreterSetAttr(interpreter, "terminated", Py_True);
}


/*********************************
 * Op code definitions
 *********************************/

// END
static PyObject * opcode_END(PyObject *self, PyObject *args) {
  Dbn_UNPACK_OPCODE_ARGS();

  Dbn_TerminateInterpreter(interpreter);
  Dbn_RETURN_INTERPRETER()
}

// BINARY_ADD
static PyObject * opcode_BINARY_ADD(PyObject *self, PyObject *args) {
  Dbn_BINARY_OP_PREFIX();

  long result = top + top1;
  Dbn_PushLong(stack, result);

  Dbn_IncrementPointer(interpreter);
  Dbn_RETURN_INTERPRETER();
}


/*********************************
 * Python Module Interface
 *********************************/

// Method definitions
static PyMethodDef OpcodeMethods[] = {

  {"_op_END"            , opcode_END          , METH_VARARGS, "END"          },
  {"_op_BINARY_ADD"     , opcode_BINARY_ADD   , METH_VARARGS, "BINARY_ADD"   },

  {NULL, NULL, 0, NULL}
};

// Public method list factory
static PyObject * Dbn_PublicOpcodes() {
    PyObject *list = PyList_New(0);

    // register the op codes
    Dbn_PushString(list, "_op_END");
    Dbn_PushString(list, "_op_BINARY_ADD");

    return list;
}

// Module initialization funciton
PyMODINIT_FUNC init_opcodes(void) {
  PyObject *module = Py_InitModule("_opcodes", OpcodeMethods);

  // set the list of public opcodes as the `__all__` attribute
  PyModule_AddObject(module, "__all__", Dbn_PublicOpcodes());
}
