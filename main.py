import subprocess
import time
from collections import Counter 
import math
from sklearn.ensemble import IsolationForest


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

    return entropy


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

model = IsolationForest(contamination=0.1)
feature_history=[]
model_trained = False

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
                    domain = parts[i + 1].rstrip(".")

                    domains.append(domain)

        
        if time.time() - window_start >= Window_size:
            
            total_domains = len(domains)
            unique_domains = len(set(domains))
            entropy = calculate_entropy(domains)

            # print(f"[FEATURES] {total_domains}, {unique_domains}, {round(entropy, 3)}")
            features = [total_domains, unique_domains, entropy]
            feature_history.append(features)

            if len(feature_history) >= 20 and model_trained == False:
                model.fit(feature_history)
                model_trained = True
                print("[1]Model have been trained at first\n")

            if model_trained == True:
                prediction = model.predict([features])[0]

                if prediction == -1:
                    print (f"anomaly_detected {features}\n")

                else:
                    print(f"Normal {features}\n")

            
            domains = []
            window_start = time.time()



    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        process.terminate()

