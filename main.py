import subprocess
import time
from collections import Counter 
import math


def calculate_entropy(domains):

    all_char = "".join(domains)

    if not all_char:
        return 0
    
    freq = Counter(all_char)
    total = len(all_char)

    entropy = 0
    for count in freq.values():
    p = count / total
    entropy -= p * math.log2(p)


cmd = [
    "sudo",
    "tcpdump",
    "-nn",
    "-l",
    "-i",
    "any",
    "udp",
    "port",
    "53"
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True
)

print("Listening the traffic")



domains = []
window_start = time.time()
Window_size = 30



while True:
    try:
        line = process.stdout.readline()
        if not line:
            break

        # print(line.strip())

        parts = line.split()

        for i, part in enumerate(parts):
            if part == "A?" or part == "AAAA?":
                if i + 1 < len(parts):
                    domain = parts[i + 1]

                    domains.append(domain)

        
        if time.time() - window_start >= Window_size:
            
            total_domains = len(domains)
            unique_domains = len(set(domains))
            entropy = calculate_entropy(domains)

            print(f"[FEATURES] {total_domains}, {unique_domains}, {round(entropy, 3)}")

            
            domains = []
            window_start = time.time()



    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        process.terminate()

