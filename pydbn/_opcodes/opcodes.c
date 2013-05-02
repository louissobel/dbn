#include <Python.h>

// macros


/*
PyObject *interpreter;
PyStringObject *arg;

if (!PyArg_ParseTuple(args, "OS", &interpreter, &arg)) {
  return NULL;
}
*/
#define Dbn_UNPACK_OPCODE_ARGS() PyObject *interpreter;PyStringObject *arg;if (!PyArg_ParseTuple(args, "OS", &interpreter, &arg)) {return NULL;}

#define Dbn_INTERPRETER_ATTR(attr) PyObject_GetAttrString(interpreter, attr);


// Helpers

// Returns new reference
// A borrowed reference
// This is similar to how listpop is implemented in stdlib
static PyObject * listpop(PyObject *list) {
  PyObject *item;
  Py_ssize_t length = PyList_GET_SIZE(list);
  if (length == 0) {
    PyErr_SetString(PyExc_IndexError, "Pop from empty list");
    return NULL;
  }
  item = PyList_GET_ITEM(list, length - 1);
  // Delete the last item
  PyList_SetSlice(list, length - 1, length, NULL);
  return item;
}

// Pops a long from the stack
// Assumes that stack is not empty
// TODO error checking
static long Dbn_PopLong(PyObject *stack) {
  PyObject *temp = listpop(stack);
  return PyInt_AS_LONG(temp);
}

// Pushes a long onto the stack
// return the stack
static PyObject * Dbn_PushLong(PyObject *stack, long value) {
  PyObject *temp = PyInt_FromLong(value);
  PyList_Append(stack, temp);
  return stack;
}

// Pushes a string onto the stack (char *)
static PyObject * Dbn_PushString(PyObject *stack, char *string) {
  PyObject *temp = PyString_FromString(string);
  PyList_Append(stack, temp);
  return stack;
}

// Sets the pointer attribute
static long Dbn_SetPointer(PyObject *interpreter, long value) {
  PyObject_SetAttrString(interpreter, "pointer", PyInt_FromLong(value));
  return value;
}

// Increments the pointer
static long Dbn_IncrementPointer(PyObject *interpreter) {
  PyObject *temp = Dbn_INTERPRETER_ATTR("pointer");
  long current = PyInt_AS_LONG(temp);
  return Dbn_SetPointer(interpreter, current + 1);
}

// Sets terminated attribute to True

static PyObject * opcode_BINARY_ADD(PyObject *self, PyObject *args) {
  Dbn_UNPACK_OPCODE_ARGS();

  PyObject *stack = Dbn_INTERPRETER_ATTR("stack");

  long top = Dbn_PopLong(stack);
  long top1 = Dbn_PopLong(stack);

  long result = top + top1;
  Dbn_PushLong(stack, result);

  Dbn_IncrementPointer(interpreter);
  return Py_BuildValue("O", interpreter);
}

// Method definitions
static PyMethodDef OpcodeMethods[] = {

  {"_op_BINARY_ADD", opcode_BINARY_ADD, METH_VARARGS, "BINARY_ADD"},

  {NULL, NULL, 0, NULL}
};


static PyObject * Dbn_PublicOpcodes() {
    PyObject *list = PyList_New(0);
    
    // register the op codes
    Dbn_PushString(list, "_op_BINARY_ADD");
    
    return list;
}

PyMODINIT_FUNC init_opcodes(void) {
  PyObject *module = Py_InitModule("_opcodes", OpcodeMethods);
  
  PyModule_AddObject(module, "__all__", Dbn_PublicOpcodes());
}
