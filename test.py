PYTHON := python3

run:
 @$(PYTHON) - <<'EOF' $(filter %.py,$(MAKECMDGOALS))
import re, subprocess, sys, tempfile, os

file_name = sys.argv[1]
print(file_name)

with open(file_name, 'r') as f:
    code_content = f.read()

input_match = re.search(r'input_data\s*=\s*"""(.*?)"""', code_content, re.DOTALL)
expected_match = re.search(r'expected_data\s*=\s*"""(.*?)"""', code_content, re.DOTALL)

if not input_match or not expected_match:
    print("Could not extract input or expected from the file. Ensure they are defined as multi-line strings with triple quotes.")
    sys.exit(1)

input_str = input_match.group(1).strip()
expected_str = expected_match.group(1).strip()

input_lines = input_str.splitlines()

with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_input:
    temp_input.write(input_str + '\n')
input_file = temp_input.name

output_file = tempfile.mktemp()

cmd = f"{sys.executable} {file_name} < {input_file} > {output_file}"
subprocess.run(cmd, shell=True)

with open(output_file, 'r') as f:
    actual_str = f.read().strip()

os.unlink(input_file)
os.unlink(output_file)

expected_lines = expected_str.splitlines()
actual_lines = actual_str.splitlines()

if actual_str == expected_str:
    print("Accepted")
else:
    print("Wrong Answer")
    for i, (exp, act) in enumerate(zip(expected_lines, actual_lines), 1):
        if exp != act:
            input_line = input_lines[i-1].strip() if i <= len(input_lines) else "<no input>"
            print(f"Test case {i}: input \"{input_line}\" expected \"{exp.strip()}\" got \"{act.strip()}\"")
    if len(actual_lines) < len(expected_lines):
        for i in range(len(actual_lines) + 1, len(expected_lines) + 1):
            input_line = input_lines[i-1].strip() if i <= len(input_lines) else "<no input>"
            print(f"Test case {i}: input \"{input_line}\" expected \"{expected_lines[i-1].strip()}\" got nothing")
    elif len(actual_lines) > len(expected_lines):
        for i in range(len(expected_lines) + 1, len(actual_lines) + 1):
            input_line = input_lines[i-1].strip() if i <= len(input_lines) else "<no input>"
            print(f"Test case {i}: input \"{input_line}\" expected nothing got \"{actual_lines[i-1].strip()}\"")
EOF

%:
 @:
