PYTHON := python3

run:
 @$(PYTHON) - <<'EOF' $(filter %.cpp,$(MAKECMDGOALS))
import re, subprocess, sys, tempfile, os

cpp_file = sys.argv[1]
print(f"Checking {cpp_file}...\n")

with open(cpp_file, 'r') as f:
    code_content = f.read()

inputs_match = re.search(r'input_data\s*=\s*\[(.*?)\]', code_content, re.DOTALL)
expected_match = re.search(r'expected_data\s*=\s*\[(.*?)\]', code_content, re.DOTALL)

if not inputs_match or not expected_match:
    print("Could not extract input_data or expected_data. Make sure they are defined as lists of triple-quoted strings in the C++ file as comments or markers.")
    sys.exit(1)

input_cases = re.findall(r'"""(.*?)"""', inputs_match.group(1), re.DOTALL)
expected_cases = re.findall(r'"""(.*?)"""', expected_match.group(1), re.DOTALL)

if len(input_cases) != len(expected_cases):
    print("Mismatch: number of inputs and expected outputs differ.")
    sys.exit(1)

exe_file = tempfile.mktemp(suffix='.out')
compile_cmd = ["g++", cpp_file, "-o", exe_file]
result = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

if result.returncode != 0:
    print("Compilation failed:")
    print(result.stderr)
    sys.exit(1)

for idx, (inp, exp) in enumerate(zip(input_cases, expected_cases), 1):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_input:
        temp_input.write(inp.strip() + '\n')
    input_file = temp_input.name

    output_file = tempfile.mktemp()

    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        subprocess.run([exe_file], stdin=fin, stdout=fout, stderr=subprocess.PIPE, text=True)

    with open(output_file, 'r') as f:
        actual = f.read().strip()

    os.unlink(input_file)
    os.unlink(output_file)

    if actual == exp.strip():
        print(f"Test {idx}: Accepted")
    else:
        print(f"Test {idx}: Wrong Answer")
        print(f"   Input:\n{inp.strip()}")
        print(f"   Expected:\n{exp.strip()}")
        print(f"   Got:\n{actual}")

os.unlink(exe_file)
EOF

%:
 @:
