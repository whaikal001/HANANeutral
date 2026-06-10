path = r"c:\Users\ACER\OneDrive\Desktop\RenpyProject\HANA - Copy\game\script.rpy"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Target 1: Line 1005 to 1103 (1-based)
# But we must be careful with line contents shifting or being slightly off.
# Let's find the anchors.

start_index = -1
end_index = -1

for i, line in enumerate(lines):
    if "# 1. Pick a fresh technique" in line and i > 980 and i < 1020:
        start_index = i
    if "calming_loop_max_reached" in line and i > 1080 and i < 1110:
        # We find the following return
        for j in range(i, i+10):
            if "return" in lines[j]:
                end_index = j
                break
        if end_index != -1: break

print(f"DEBUG: T1 Start={start_index+1}, End={end_index+1}")

# Target 2: "if tech == \"breathing\":" near 1105 through end of that block before Phase 5
start_index_2 = -1
end_index_2 = -1
for i in range(len(lines)):
    if 'if tech == "breathing":' in lines[i] and i > 1080:
        start_index_2 = i
        break

if start_index_2 != -1:
    for i in range(start_index_2, len(lines)):
        if "# Summarize" in lines[i] or "label phase5" in lines[i]:
            end_index_2 = i - 1
            break
print(f"DEBUG: T2 Start={start_index_2+1}, End={end_index_2+1}")

# Remove in reverse order
if start_index_2 != -1 and end_index_2 != -1:
    del lines[start_index_2:end_index_2+1]
if start_index != -1 and end_index != -1:
    del lines[start_index:end_index+1]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
