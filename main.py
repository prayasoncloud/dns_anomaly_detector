import subprocess

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


while True:
    try:
        line = process.stdout.readline()
        if not line:
            break

        print(line.strip())

    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        process.terminate()

