import os
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python build_and_run.py <source.C~>")
    sys.exit(1)

src = sys.argv[1]
base = os.path.splitext(src)[0]
ll_file = base + ".ll"
o_file = base + ".o"
exe_file = base + ".exe"

# 1. Compile C~ to LLVM IR (.ll)
subprocess.check_call([sys.executable, "chatgpt_compiler.py", src])

# 2. Compile .ll to .o using llc
subprocess.check_call(["llc", "-filetype=obj", ll_file, "-o", o_file])

# 3. Link .o to .exe using gcc
subprocess.check_call(["gcc", o_file, "-o", exe_file])

# 4. Run the executable
subprocess.check_call([exe_file])