input_file = "output/output.csv"
output_file = "output/output_censored.csv"

# Shift in degrees to apply to latitude and longitude
shift_1 = 0.0 
shift_2 = 0.0

with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        
        a, b, c = map(float, line.split(","))
        a += shift_1
        b += shift_2
        f_out.write(f"{a},{b},{c}\n")