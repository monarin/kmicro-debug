import sys

def parse_bulk_file(filename):
    pulse_ids = []
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        data = [int(line, 16) for line in lines]

        i = 1
        while i < len(data):
            if data[i-1] == 0xFFFFFFFFFFFFFFF6:
                # Look for the *next valid* pulse ID after marker
                j = i
                while j < len(data):
                    candidate = data[j]
                    # Ignore 000000FFFFFFF2 or similar invalid patterns
                    if candidate != 0x000000FFFFFFF2:
                        # Mask to 56 bits and store
                        pulse_id = candidate & 0x00FFFFFFFFFFFFFF
                        pulse_ids.append((j, pulse_id))
                        break
                    j += 1
                i = j + 1
            else:
                i += 1
    return pulse_ids


def analyze_bit_diff(val_prev, val_curr):
    xor = val_prev ^ val_curr
    flipped_bits = [i for i in range(56) if (xor >> i) & 1]

    drop_to_zero_bits = [i for i in flipped_bits if ((val_prev >> i) & 1) and not ((val_curr >> i) & 1)]
    flip_1_to_0 = [(i, '1→0') for i in flipped_bits if ((val_prev >> i) & 1) and not ((val_curr >> i) & 1)]
    flip_0_to_1 = [(i, '0→1') for i in flipped_bits if not ((val_prev >> i) & 1) and ((val_curr >> i) & 1)]

    # Check if all flipped bits are 1→0 and in a larger block
    if len(drop_to_zero_bits) == len(flipped_bits) and len(flipped_bits) > 2:
        return 'Drop to zero', len(drop_to_zero_bits), drop_to_zero_bits
    else:
        # Filter bit flips to positions 17 and above
        filtered_flips = [(pos, desc) for (pos, desc) in flip_1_to_0 + flip_0_to_1 if pos >= 17]
        return 'Bit flip', len(filtered_flips), filtered_flips

def find_regressions(pulse_ids):
    regressions = []
    for i in range(1, len(pulse_ids)):
        idx_prev, val_prev = pulse_ids[i-1]
        idx_curr, val_curr = pulse_ids[i]
        if val_curr < val_prev:
            kind, count, bits = analyze_bit_diff(val_prev, val_curr)
            regressions.append({
                "prev_line": idx_prev + 1,
                "prev_value": f"{val_prev:014X}",  # 56-bit hex
                "curr_line": idx_curr + 1,
                "curr_value": f"{val_curr:014X}",
                "difference": val_curr - val_prev,
                "type": kind,
                "bit_info": bits,
                "bit_count": count
            })
    return regressions

def main():
    if len(sys.argv) != 2:
        print("Usage: python pulseid_regression_checker.py <bulk.txt>")
        sys.exit(1)

    filename = sys.argv[1]
    pulse_ids = parse_bulk_file(filename)
    regressions = find_regressions(pulse_ids)

    if not regressions:
        print("✅ No pulse ID regressions detected.")
    else:
        print("⚠️ Pulse ID regressions detected:\n")
        for r in regressions:
            print(f"At line {r['curr_line']}:")
            print(f"  Previous Pulse ID (line {r['prev_line']}): {r['prev_value']}")
            print(f"  Current  Pulse ID (line {r['curr_line']}): {r['curr_value']}")
            print(f"  Difference: {r['difference']}")
            print(f"  Type: {r['type']}")
            if r['type'] == 'Drop to zero':
                print(f"  Dropped {r['bit_count']} bits at positions: {r['bit_info']}")
            else:
                flips = ', '.join([f"bit {pos} ({desc})" for pos, desc in r['bit_info']])
                print(f"  Flipped {r['bit_count']} bit(s): {flips}")
            print()

if __name__ == "__main__":
    main()

