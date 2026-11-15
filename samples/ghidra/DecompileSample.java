// Small Ghidra script to verify that the ARM64 decompiler works on this phone.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;

public class DecompileSample extends GhidraScript {
    @Override public void run() throws Exception {
        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) {
                throw new IllegalStateException("Cannot open program in decompiler");
            }
            for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
                if (function.getName().equals("reverse_check")) {
                    DecompileResults result = decompiler.decompileFunction(function, 30, monitor);
                    if (!result.decompileCompleted()) {
                        throw new IllegalStateException(result.getErrorMessage());
                    }
                    println("K70_DECOMPILE_OK " + currentProgram.getName());
                    println(result.getDecompiledFunction().getC());
                    return;
                }
            }
            throw new IllegalStateException("reverse_check function was not found");
        } finally {
            decompiler.dispose();
        }
    }
}
