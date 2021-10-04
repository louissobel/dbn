
import {InterpreterDebuggerAction, RunState} from "@ethereumjs/vm/dist/evm/interpreter"
import {Operation} from "@ethersproject/asm"

const prompt = require('prompt')
const asm = require("@ethersproject/asm")
const sprintf = require("sprintf-js").sprintf
const BN = require('bn.js');


export default class InteractiveDebugger {
  firstRun: boolean

  constructor() {
    this.firstRun = true;
  }

  dumpDisassemble(runState: RunState, beforePC : number, afterPC : number) {
    const bytecodes = asm.disassemble(runState.code);
    const bytecodeIndex = bytecodes.findIndex((op: Operation) => {
      return op.offset === runState.programCounter;
    })

    const start = Math.max(bytecodeIndex - beforePC, 0);
    const end = start + afterPC + beforePC;

    bytecodes.slice(start, end).forEach((op: Operation) => {
      console.log(this.formatBytecode(op, runState.programCounter))
    })
  }

  dumpStack(runState: RunState) {
    const stackData = runState.stack._store;

    console.log("+" + "-".repeat(64 + 2) + "+")
    for (var i = stackData.length - 1; i >= 0; i--) {
      console.log(sprintf("|0x%064s|", stackData[i].toString(16)));
      console.log("+" + "-".repeat(64 + 2) + "+")
    }

    if (stackData.length === 0) {
      console.log("+" + "-".repeat(64 + 2) + "+")
    }
  }

  dumpMemory(runState: RunState) {
    for (var i = 0; i < runState.memory._store.length; i += 32) {
      const word = runState.memory.read(i, 32)

      let bytes = []
      for (var j = 0; j < 32; j++) {
        bytes.push(sprintf("%02x", word[j]))
      }
      console.log(sprintf("%04x", i) + "| " + bytes.join(" "));
    }
  }


  formatBytecode(op: Operation, currentProgramCounter: number): string {
    const opcode = op.opcode;

    let offset = sprintf("%04x", op.offset);
    if (opcode.isValidJumpDest()) {
        offset += "*";
    } else {
        offset += " ";
    }

    let operation = opcode.mnemonic;

    if (opcode.isPush()) {
      operation = operation + " " + op.pushValue;
    }

    let prefix = "    ";
    if (op.offset === currentProgramCounter) {
      prefix = "==> ";
    }

    return prefix + offset + ": " + operation
  }


  async getAction(runState: RunState): Promise<InterpreterDebuggerAction> {
    prompt.start();

    if (this.firstRun) {
      console.log("EVM Debugger!!")
      console.log("Commands are [step, continue, stack, memory]")
      this.firstRun = false;
    }

    this.dumpDisassemble(runState, 5, 10);

    console.log("Stack:")
    this.dumpStack(runState);

    while (true) {
      const answer = (await prompt.get([">"]))['>']
      if (answer === 'step') {
        return InterpreterDebuggerAction.Step;
      } else if (answer === 'continue') {
        return InterpreterDebuggerAction.Continue;
      } else if (answer === 'stack') {
        this.dumpStack(runState);
      } else if (answer === 'memory') {
        this.dumpMemory(runState);
      } else {
        console.log("invalid command")
      }
    }
  }
}