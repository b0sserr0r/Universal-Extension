import sys
import os
import subprocess


def main():
    getjob = ["kubectl", "get", "jobs", "-n", "dev"]
    result = subprocess.run(getjob, capture_output=True, text=True)
    output = result.stdout.strip() + "\n" + result.stderr.strip()
    print(output)

main()