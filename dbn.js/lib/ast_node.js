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

define(function (require, exports, module) {
  
  var DBNDot        = require('lib/structures/dot')
    , DBNVariable   = require('lib/structures/variable')
    , DBNProcedure  = require('lib/structures/procedure')
    ;
  
  var DBNASTNode = module.exports = function (options) {
    this.type = options.type;
    this.lineNo = options.lineNo || -1;
    this.tokens = options.tokens || [];
    this.children = options.children || [];
    this.name = options.name || options.type;
  }

  (function() {

    this.start_location = function () {
      if (this.tokens.length > 0) {
        var firstToken = this.tokens[0];
        return {
          lineNo : firstToken.lineNo
        , charNo : firstToken.charNo
        };
      } else {
        return null;
      }
    };

    this.end_location = function () {
      if (this.tokens.length > 0) {
        var last_token = this.tokens[this.tokens.length - 1];
        return {
          lineNo: lastToken.lineNo
        , charNo: lastToken.charNo
        };
      } else {
        return null;
      }
    };

    this.apply = function (state) {
      var typeApplyFuncHash = {

        block: function (state) {
          for (var i = 0; i < this.children.length; i++) {
            state = this.children[i].apply(state);
          }
          return state;
        }

      , set: function (state) {
          state = state.setLineNo(this.lineNo);

          var left = this.children[0]
            , right = this.children[1]
            ;

          var leftVal = left.evaluate_lazy(state)
            , rightVal = right.evaluate(state)
            ;

          return state.set(leftVal, rightVal);
        }

      , repeat: function (state) {
          state = state.setLineNo(this.lineNo);

          var variable = this.children[0]
            , start = this.children[1]
            , end = this.children[2]
            , body = this.children[3]
            ;

          var variableName = variable.evaluateLazy(state)
            , startVal = start.evaluate(state)
            , endVal = end.evaluate(state)
            ;

          var rangeStart
            , rangeEnd
            ;

          if (endVal > startVal) {
            rangeStart = startVal;
            rangeEnd = endVal;
          } else {
            rangeStart = endVal;
            rangeEnd = startVal;
          }

          for (var variableValue = rangeStart; variableValue <= rangeEnd; variableValue++) {
            state = state.setVariable(variableName.name, variableValue);
            state = body.apply(state);
          }

          return state;
        }

      , question: function (state) {
          state = state.setLineNo(this.lineNo);

          var left = this.children[0]
            , right = this.children[1]
            , body = this.children[2]
            ;

          var leftVal = left.evaluate(state)
            , rightVal = right.evaluate(state)
            ;

          var questionFunctions = {
            Same: function (l, r) {
              return l === r;
            }

          , NotSame: function (l, r) {
              return l !== r;
            }

          , Smaller: function (l, r) {
              return l < r;
            }

          , NotSmaller: function (l, r) {
              return l >= r;
            }
          };

          var doBranch = questionFunctions[this.name](leftVal, rightVal);

          if (doBranch) {
            state = body.apply(state);
          }

          return state;
        }

      , command: function (state) {
          state = state.setLineNo(this.lineNo)

          var evaluatedArgs = [];

          for (var i = 0; i < this.children.length; i++) {
            evaluatedArgs.push(this.children[i].evaluate(state));
          }

          var proc = state.lookupCommand(this.name);
          if (proc === null) {
            throw new SyntaxError("Command " + this.name + " is not defined!");
          }

          if (proc.arg_count != evaluated_args.length) {
            throw new SyntaxError(
              this.name + " requires " + proc.argCount + "arguments, but " + evaluatedArgs.length + " were provided"
            );
          }

          var commandBindings = {};
          for (var i = 0; i < proc.argCount; i++) {
            commandBindings[proc.formalArgs[i]] = evaluatedArgs[i];
          }

          state = state.push();
          state = state.setVariables(commandBindings);
          state = proc.body.apply(state);
          state = state.pop();

          return state;
        }

      , command_definition: function (state) {
          state = state.setLineNo(this.lineNo);

          // Ensure that this.children is not mutated;
          var childrenCopy = this.children.slice();

          var nameNode = childrenCopy.shift()
            , name = nameNode.evaluateLazy(state).name
            , body = childrenCopy.pop()
            ;

          var formalArgs = [];
          for (var i = 0; i < childrenCopy.length; i++) {
            formalArgs.push(childrenCopy[i].evaluateLazy(state).name);
          }

          var proc = new DBNProcedure(formalArgs, body);
          proc.lineNo = this.lineNo;
          state = state.addCommand(name, proc);

          return state;
        }

      , javascript: function (state) {
          var code = this.children[0]
          return code(state);
        }

      }

      var applyFunc = typeApplyFuncHash[this.type];
      if (typeof applyFunc === "undefined") {
        throw new TypeError("node type " + this.type + " does not have an apply function");
      }

      return applyFunc.call(this, state)
    };

    this.evaluate = function (state) {
      var typeEvalFuncHash = {

        bracket: function (state) {

          var left = this.children[0]
            , right = this.children[1]
            ;

          var x = left.evaluate(state)
            , y = right.evaluate(state)
            ;

          return state.image.queryPixel(x, y);
        }

      , operation: function (state) {

          var left = this.children[0]
            , right = this.children[1]
            ;

          var leftVal = left.evaluate(state)
            , rightVal = right.evaluate(state)
            ;

          var operations = {
            '+': function (a, b) {
              return a + b;
            }

          , '-': function (a, b) {
              return a - b;
            }

          , '/': function (a, b) {
              return Math.round(a / b);
            }

          , '*': function (a, b) {
              return a * b;
            }
          };

          return operations[this.name](leftVal, rightVal);
        }

      , number: function (state) {
          return parseInt(this.name);
        }

      , word: function (state) {
          return state.lookupVariable(this.name);
        }
      }

      var evalFunc = typeEvalFuncHash[this.type];

      if (typeof evalFunc === "undefined") {
        throw new TypeError("node type " + this.type + " does not have an evaluate function");
      }

      return evalFunc.call(this, state);
    };

    this.evaluateLazy = function (state) {
      var typeEvalLazyFuncHash = {

        bracket: function (state) {

          var left = this.children[0]
            , right = this.children[1]
            ;

          var x = left.evaluate(state)
            , y = right.evaluate(state)
            ;

          return new DBNDot(x, y);
        }

      , word: function (state) {
          return new DBNVariable(this.name);
        }
      }

      var evalLazyFunc = typeEvalLazyFuncHash[this.type];

      if (typeof eval_func === "undefined") {
        throw new TypeError("node type " + this.type + " does not have an evaluate function");
      }

      return evalLazyFunc.call(this, state);
    };

    /**
     * The toString method -
     *
     * @this{DBNBaseNode}
     * @param{Number} depth The depth at which to print. only means anything if indent is set
     * @param{Number} indent If this is a number greater than 0, then will be pretty printed
     * @returns{String} the string
     */
    this.toString = function (depth, indent) {

        // utility method for mapping over children
        var childmap = function (f) {
            var out = [];
            for (var i = 0; i < this.children.length; i++) {
                out.push(f(this.children[i]));
            }
            return out;
        };

        if (typeof indent === "undefined") {
            return "(" + this.name + " " + childmap.call(this, function(c){ return c.toString(); }).join(' ') + ")";
        } else {
            depth = depth || 0

            // we know indent has a value because thats how we got to this branch
            var out = "";
            for (var i = 0; i < depth * indent; i++) {
              out += " ";
            }

            out += "(" + this.name;
            if (this.children.length > 0) {
              out += '\n';
              out += childmap.call(this, function(c) {
                return c.toString(depth + 1, indent);
              }).join('');

              for (var i = 0; i < depth * indent; i++) {
                out += " ";
              }
            }
            out += ")\n";
            return out;
        }
    };
  }).call(DBNASTNode.prototype);

});


 





