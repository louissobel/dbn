"""
Will assembly a compilation
"""
import structures


def assemble(compilation, offset=0):
    """
    Go through and give a value to each label
    """
    label_values = {}
    counter = offset

    for component in compilation:
        if isinstance(component, structures.Label):
            label_values[component.name] = counter
        else:
            counter += 1

    bytecode = []

    for index, component in enumerate(compilation):
        if isinstance(component, structures.Bytecode):
            if component.has_label:
                label = component.label
                if label.name in label_values:
                    value = label_values[label.name]
                    component.arg = str(value)
                else:
                    raise ValueError("No label for '%s' at code index %d" % (label.name, index))
            bytecode.append(component)

    return bytecode
