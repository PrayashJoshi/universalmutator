import json
import argparse
import os
import sys

def load_mutation(jsonl_file, mutation_id):
    """Load a specific mutation by ID from a JSONL file."""
    with open(jsonl_file, 'r') as f:
        for line in f:
            mutation = json.loads(line)
            if mutation['id'] == mutation_id:
                return mutation
    return None

def apply_mutation(source_file, mutation, output_file=None):
    """Apply a mutation to a source file."""
    with open(source_file, 'r') as f:
        source_lines = f.readlines()
    
    # Handle different mutation types
    if 'mutation_type' in mutation and mutation['mutation_type'] == 'SWAP':
        # Handle line swaps
        line_a, line_b = mutation['line_numbers']
        temp = source_lines[line_a - 1]
        source_lines[line_a - 1] = source_lines[line_b - 1]
        source_lines[line_b - 1] = temp
    else:
        # Handle regular mutations
        line_num = mutation['line_number']
        
        if line_num <= len(source_lines):
            original_line = source_lines[line_num - 1]
            mutated_code = mutation['mutated_code']
            original_code = mutation['original_code']
            
            # Simple replacement approach
            if original_code.strip() in original_line:
                mutated_line = original_line.replace(
                    original_code.strip(), 
                    mutated_code.strip()
                )
                source_lines[line_num - 1] = mutated_line
            else:
                print(f"Warning: Could not find original code in line {line_num}")
                print(f"Original line: {original_line}")
                print(f"Expected code: {original_code}")
                return False
        else:
            print(f"Error: Line number {line_num} exceeds file length")
            return False
    
    # Generate default output filename if not provided
    if not output_file:
        project = mutation.get('project', 'unknown')
        file_part = os.path.basename(source_file)
        mutation_id = mutation['id']
        output_file = f"{file_part}.{project}.mutant.{mutation_id}"
    
    # Write the mutated source
    with open(output_file, 'w') as f:
        f.writelines(source_lines)
    
    print(f"Mutation {mutation['id']} applied and written to {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Apply a mutation from a JSONL log to a source file.')
    parser.add_argument('jsonl_file', help='JSONL file containing mutations')
    parser.add_argument('source_file', help='Source file to apply mutation to')
    parser.add_argument('mutation_id', type=int, help='ID of the mutation to apply')
    parser.add_argument('--output', '-o', help='Output file (default: <source>.mutant.<id>)')
    
    args = parser.parse_args()
    
    # Load mutation
    mutation = load_mutation(args.jsonl_file, args.mutation_id)
    if not mutation:
        print(f"Error: Mutation with ID {args.mutation_id} not found")
        sys.exit(1)
    
    # Apply mutation
    success = apply_mutation(args.source_file, mutation, args.output)
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()