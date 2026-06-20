# main file for function 
# input is a email
# return a boolean value 

from collections import defaultdict

# Use a defaultdict to easily group words under the same letter
tld_map = defaultdict(list)

key = None

# Open and process the file
with open('tldnames.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        
        # Skip empty lines, comments, or headers
        if not line or line.startswith('#'):
            continue
            
        # Get the first letter as the key (uppercase)
        first_letter = line[0].upper()
        
        # Add the domain name to that letter's list
        tld_map[first_letter].append(line)

# Convert back to standard dictionary format
tld_map = dict(tld_map)

# Example output test
print("A total of", len(tld_map['A']), "entries start with 'A'.")
print("First 5 entries for 'A':", tld_map['A'][:5])

def manual_binary_search(sorted_list, target):
    low = 0
    high = len(sorted_list) - 1

    while low <= high:
        # Calculate the middle index
        mid = (low + high) // 2
        guess = sorted_list[mid]

        # Target found
        if guess == target:
            return mid
        # Guess was too high
        elif guess > target:
            high = mid - 1
        # Guess was too low
        else:
            low = mid + 1
            
    return -1  # Target not found

# --- Implementation ---

if key:
    key.sort() # Remember to sort first!
    index = manual_binary_search(key, target_tld)
    
    if index != -1:
        print(f"Found {target_tld} at index {index}")
    else:
        print(f"{target_tld} not found")


#-- FINAL-FINAL -FINAL SUBMISSION 

def validate(tld):
    """
    Takes a raw TLD string, finds the matching alphabet bucket in the hashmap,
    sorts it, and returns True if the TLD is found using binary search.
    """
    # Guard against empty string inputs
    if not tld:
        return False
        
    # Get the uppercase first letter to find the matching bucket key
    first_letter = tld[0].upper()
    
    # Check if the alphabet key exists in our hashmap
    if first_letter in tld_map:
        # Isolate the list bucket for this specific letter
        bucket = tld_map[first_letter]
        
        # Binary search requires a sorted list
        bucket.sort()
        
        # Execute your binary search function
        index = manual_binary_search(bucket, tld)
        
        # Return True if found (index is not -1)
        return index != -1
        
    return False
