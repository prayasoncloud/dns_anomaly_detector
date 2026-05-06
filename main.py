import subprocess
import time
import math
from collections import Counter
from datetime import datetime
from sklearn.ensemble import IsolationForest


def calculate_entropy(domains):
    all_chars = "".join(domains)

    if not all_chars:
        return 0

    freq = Counter(all_chars)
    total = len(all_chars)

    entropy = 0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


WINDOW_SIZE = 30 
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

print("[*] DNS Anomaly Detector Started...\n")



domains = []
window_start = time.time()

model = IsolationForest(contamination=0.1)
feature_history = []
model_trained = False


try:
    while True:
        line = process.stdout.readline()

        if not line:
            break

        line = line.strip()


        if "A?" in line or "AAAA?" in line:
            parts = line.split()

            for i, part in enumerate(parts):
                if part == "A?" or part == "AAAA?":
                    if i + 1 < len(parts):
                        domain = parts[i + 1].rstrip(".")
                        domains.append(domain)


        if time.time() - window_start >= WINDOW_SIZE:

            total_queries = len(domains)
            unique_domains = len(set(domains))
            entropy = calculate_entropy(domains)

            features = [total_queries, unique_domains, entropy]
            feature_history.append(features)


            if len(feature_history) >= 20 and not model_trained:
                model.fit(feature_history)
                model_trained = True
                print("[*] Model trained on baseline data\n")



            timestamp = datetime.now().strftime("%H:%M:%S")

            if model_trained:
                prediction = model.predict([features])[0]
                if prediction == -1:
                    print(f"[{timestamp}]  ANOMALY DETECTED | Total: {total_queries} | Unique: {unique_domains} | Entropy: {entropy:.2f}\n")
                else:
                    print(f"[{timestamp}]  NORMAL | Total: {total_queries} | Unique: {unique_domains} | Entropy: {entropy:.2f}\n")
            else:

                print(f"[{timestamp}] Collecting baseline data... ({len(feature_history)}/20)")




            domains = []
            window_start = time.time()


except KeyboardInterrupt:
    print("\n[!] Stopped by user")
    process.terminate()