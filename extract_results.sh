#!/usr/bin/env bash
# ==============================================================================
# Script Name: extract_results.sh
# Description: Advanced statistical extraction for probabilistic prime generation.
#              Outputs 11 columns including F1-Score, Hit Rate, and Coverage.
#              FIX: Correctly parses inline counters from the summary line.
# ==============================================================================

LOG_DIR="log"
OLD_DIR="log_old"
FINAL_DIR="log_final_result"
OUTPUT_CSV="final_results.csv"

COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

mkdir -p "$FINAL_DIR" "$OLD_DIR" "$LOG_DIR"
rm -f "$FINAL_DIR"/*

echo "Starting statistical data processing pipeline..."

# --- PHASE 1: Validation ---
for file in "$LOG_DIR"/*.log; do
    [[ -f "$file" ]] || continue
    if grep -q "COMPUTATION FINISHED" "$file"; then
        cp -p "$file" "$FINAL_DIR/"
    fi
done

# --- PHASE 2: Safe Merge ---
for src_file in "$OLD_DIR"/*.log; do
    [[ -f "$src_file" ]] || continue
    base_name=$(basename "$src_file")
    dest_file="$FINAL_DIR/$base_name"

    if [[ -f "$dest_file" ]]; then
        md5_src=$(md5sum "$src_file" | awk '{print $1}')
        md5_dest=$(md5sum "$dest_file" | awk '{print $1}')
        if [[ "$md5_src" != "$md5_dest" ]]; then
            echo -e "${COLOR_RED}FATAL ERROR: Data collision detected for '$base_name'!${COLOR_RESET}"
            exit 1
        else
            continue 
        fi
    else
        cp -p "$src_file" "$FINAL_DIR/"
    fi
done

# --- PHASE 3: Statistical Extraction ---
echo "n,input_prime,max_value,total_attempts,primes_found,precision,recall,f1_score,duplication_rate,hit_rate,space_coverage" > "$OUTPUT_CSV"

for file in "$FINAL_DIR"/*.log; do
    [[ -f "$file" ]] || continue

    extracted_data=$(
        awk '
            # Parse parameters
            /^# input value[ \t\r]*$/ { getline; n = $1 }
            /^# input prime[ \t\r]*$/ { getline; input_prime = $1 }
            /^# max value[ \t\r]*$/   { getline; max_value = $1 }
            
            # Parse Pre-calculated Ratios 
            /^# prime_counter ?\/ ?tot_primes/ { getline; recall = $1 }
            /^# prime_counter ?\/ ?\(not_prime_counter/ { getline; precision = $1 }
            
            # Parse Raw Counters from the single summary line
            # Format: # not prime counter: 89 -- prime counter: 85 -- duplicate counter: 0 -- tot primes: 136
            /^# not prime counter:/ {
                not_prime = $5
                prime = $9
                duplicate = $13
            }
            
            END {
                # 1. Total Effort (Attempts)
                total_attempts = prime + not_prime + duplicate
                
                # 2. F1-Score (Harmonic Mean of Precision & Recall)
                f1_score = 0
                if ((precision + recall) > 0) {
                    f1_score = 2 * (precision * recall) / (precision + recall)
                }
                
                # 3. Duplication Rate
                duplication_rate = 0
                if ((prime + duplicate) > 0) {
                    duplication_rate = duplicate / (prime + duplicate)
                }
                
                # 4. Hit Rate (Probability of success per attempt)
                hit_rate = 0
                if (total_attempts > 0) {
                    hit_rate = prime / total_attempts
                }
                
                # 5. Space Coverage (How much of the domain was sampled)
                space_coverage = 0
                if (max_value > 0) {
                    space_coverage = total_attempts / max_value
                }
                
                # Output formatted CSV row
                printf "%s,%s,%s,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n", \
                       n, input_prime, max_value, total_attempts, prime, \
                       precision, recall, f1_score, duplication_rate, hit_rate, space_coverage
            }
        ' "$file"
    )

    if [[ -n "$extracted_data" ]]; then
        echo "$extracted_data" >> "$OUTPUT_CSV"
    fi
done

# --- Final Sorting ---
{
    head -n 1 "$OUTPUT_CSV"
    tail -n +2 "$OUTPUT_CSV" | sort -t ',' -k1,1n
} > temp.csv
mv temp.csv "$OUTPUT_CSV"

echo "Pipeline complete. 11-column CSV generated at: $OUTPUT_CSV"

