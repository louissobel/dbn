/*
This module has the classes
for all the nodes in the AST
of a dbn program


note on line number tracking:
done using a line_no attribute
Commands and Keywords (Set, Repeat, Questions... (block level nodes))
are the ones that this matters for

Also, note that the line_no of the stored procedure created by the
DefineCommandNode gets set to the line_no of the DefineCommandNode
*/


function DBNASTNode(options) {

    this.type = options.type
    this.line_no = options.line_no || -1
    this.tokens = options.tokens || []
    this.children = options.children || []
    this.name = options.name || options.type
}


DBNASTNode.prototype.start_location = function() {
    if (this.tokens.length > 0) {
        var first_token = this.tokens[0];
        return {
            line_no : first_token.line_no,
            char_no : first_token.char_no
        };
    } else {
        return null;
    }
}


DBNASTNode.prototype.end_location = function() {
    if (this.tokens.length > 0) {
        var last_token = this.tokens[this.tokens.length - 1];
        return {
            line_no : last_token.line_no,
            char_no : last_token.char_no
        };
    } else {
        return null;
    }
}


DBNASTNode.prototype.apply = function(state) {
    var type_apply_func_hash = {
        
        block : function(state) {
            for (var i=0; i<this.children.length; i++) {
                state = this.children[i].apply(state);
            }
            return state 
        },
        
        set : function(state) {
            state = state.set_line_no(this.line_no)
            
            var left = this.children[0]
            var right = this.children[1]

            var left_val = left.evaluate_lazy(state);
            var right_val = right.evaluate(state);
            
            return state.set(left_val, right_val);
        },
        
        repeat : function(state) {
            state = state.set_line_no(this.line_no)
            
            var variable = this.children[0]
            var start = this.children[1]
            var end = this.children[2]
            var body = this.children[3]

            var variable_name = variable.evaluate_lazy(state);
            var start_val = start.evaluate(state);
            var end_val = end.evaluate(state);

            var range_start, range_end;
            if (end_val > start_val) {
                range_start = start_val;
                range_end = end_val;
            } else {
                range_start = end_val;
                range_end = start_val;
            }

            for (var variable_value = range_start; variable_value <= range_end; variable_value++) {
                state = state.set_variable(variable_name.name, variable_value)
                state = body.apply(state)
            }

            return state
        },
        
        question : function(state) {
            state = state.set_line_no(this.line_no)

            var left = this.children[0]
            var right = this.children[1]
            var body = this.children[2]

            var left_val = left.evaluate(state);
            var right_val = right.evaluate(state);

            var question_functions = {
                Same : function(l, r) { return l == r},
                NotSame : function(l, r) { return l != r},
                Smaller : function(l, r) { return l < r},
                NotSmaller : function(l, r) { return l >= r}
            }

            var do_branch = question_functions[this.name](left_val, right_val);
            if (do_branch) {
                state = body.apply(state);
            }

            return state
        },
        
        command : function(state) {
            state = state.set_line_no(this.line_no)

            var evaluated_args = []
            for (var i=0; i<this.children.length; i++) {
                evaluated_args.push(this.children[i].evaluate(state))
            }

            var proc = state.lookup_command(this.name);
            if (proc == null) {
                throw new SyntaxError("Command " + this.name + " is not defined!");
            }

            if (proc.arg_count != evaluated_args.length) {
                throw new SyntaxError(
                    this.name +
                    " requires " +
                    proc.arg_count +
                    "arguments, but " +
                    evaluated_args.length +
                    " were provided"
                )
            }

            var command_bindings = {};
            for (var i=0;i<proc.arg_count;i++) {
                command_bindings[proc.formal_args[i]] = evaluated_args[i];
            }

            state = state.push();
            state.set_variables(command_bindings);
            state = proc.body.apply(state);
            state = state.pop();

            return state;
        },
        
        command_definition : function(state) {
            state = state.set_line_no(this.line_no)

            var args = this.children[0]
            var body = this.children[1]
            
            var proc = new DBNProcedure(args, body);
            proc.line_no = this.line_no;
            state = state.add_command(this.name, proc);

            return state;
        },
        
        javascript : function(state) {
            var code = this.children[0]
            
            return code(state);
        },
        
    }
    
    var apply_func = type_apply_func_hash[this.type]
    if (typeof apply_func == "undefined") {
        throw new TypeError("node type " + this.type + " does not have an apply function")
    }
    
    return apply_func(state)
}


DBNASTNode.prototype.evaluate = function(state) {
    var type_eval_func_hash = {
        
        bracket : function(state) {
            
            var left = this.children[0]
            var right = this.children[1]
            
            var x = left.evaluate(state);
            var y = right.evaluate(state);
        
            return state.image.query_pixel(x, y);
        },
        
        binary_op : function(state) {
            
            var left = this.children[0]
            var right = this.children[1]
                        
            var left_val = left.evaluate(state);
            var right_val = right.evaluate(state);

            var operations = {
                '+' : function(a,b) {return a + b},
                '-' : function(a,b) {return a - b},
                '/' : function(a,b) {return Math.round(a/b)},
                '*' : function(a,b) {return a * b}
            }

            return operations[this.name](left_val, right_val);
        },
        
        number : function(state) {
            return parseInt(this.name);
        },
        
        word : function(state) {
            return this.name;
        },
    }
    
    var eval_func = type_eval_func_hash[this.type]
    if (typeof eval_func == "undefined") {
        throw new TypeError("node type " + this.type + " does not have an evaluate function")
    }
    
    return eval_func(state)
}

DBNASTNode.prototype.evaluate_lazy = function(state) {
    var type_eval_lazy_func_hash = {
        
        bracket : function(state) {
            
            var left = this.children[0]
            var right = this.children[1]
            
            var x = left.evaluate(state);
            var y = right.evaluate(state);
        
            return new DBNDot(x, y)
        },
        
        word : function(state) {
            return new DBNVariable(this.name)
        },
    }
    
    var eval_func = type_eval_func_hash[this.type]
    if (typeof eval_func == "undefined") {
        throw new TypeError("node type " + this.type + " does not have an evaluate function")
    }
    
    return eval_func(state)
}


/**
 * The toString method - 
 * expects a function printInfo that returns an object with name, children
 *
 * @this{DBNBaseNode}
 * @param{Number} depth The depth at which to print. only means anything if indent is set
 * @param{Number} indent If this is a number greater than 0, then will be pretty printed
 * @returns{String} the string
 */
DBNASTNode.prototype.toString = function(depth, indent) {
    var childmap = function(f) {
        var out = [];
        for (var i=0;i<this.children.length;i++) {
            out.push(f(this.children[i]))
        }
        return out;
    }
    
    var print_info = this.print_info();

    if (typeof(indent) === "undefined") {
        var out = "(" + print_info.name + " " + childmap.call(print_info, function(c){return c.toString()}).join(' ') + ")";
        return out;
    } else {
        depth = depth || 0
        // we know indent has a value because thats how we got to this branch

        var out = "";
        for (var i=0; i<depth*indent; i++) { out += " " }
        out += "(" + print_info.name + "\n";
        out += childmap.call(print_info, function(c){c.toString(depth+1, indent)}).join('');
        for (var i=0; i<depth*indent; i++) { out += " " }
        out += ")\n";
        return out        
    }
}
 

/**
 * STRUCTURES
 *
 */


/**
 * DBNVariable = encapsulates a variable name
 *
 * @constructor
 * @param{String} name The variable name
 */
function DBNVariable(name) {
    this.name = name;
}


/**
 * DBNDot - encapsulates a dot (with x, y coords)
 *
 * @param{Number} x The x coordinate of the dot
 * @param{Number} y The y coordinate of the dot        
 */
function DBNDot(x, y) {
    this.x = x;
    this.y = y;
}


/**
 * DBNProcedure - a class to encapsulate a procedure, its args and its body
 * halfy implements the DBNBaseNode interface, so while its sort of like as AST, it really belongs here
 *
 * @constructor
 * @param{Array<String>} formal_args A list of formal arguments (this will have values bound upon invocation)
 * @param{DBNBaseNode} body A DBNBaseNode that will be applied upon invocation
 */
function DBNProcedure(formal_args, body) {
    this.formal_args = formal_args;
    this.arg_count = formal_args.length;
    this.body = body;
}

/**
 * The print_info for a DBNprocedure
 *
 * @this{DBNProcedure}
 * @returns{Object} with keys [name, children] for printing
 */
DBNProcedure.prototype.print_info = function() {
    return {
        name : 'proc',
        children : [this.formal_args.join(','), this.body]
    }
}

/**
 * The toString method for a DBNProcedure 
 *
 * Jacked from base node
 */
DBNProcedure.prototype.toString = DBNBaseNode.prototype.toString;

