import requests
import json
import time
import threading
import sys
import random
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

def load_characters(file="characters.json"):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_locations(file="locations.json"):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt},
            stream=True
        )
        out = ""
        for chunk in response.iter_lines():
            if chunk:
                data = json.loads(chunk.decode())
                out += data.get("response", "")
        return out.strip()
    except Exception as e:
        print("Error during generation:", e)
        return ""

class Spinner:
    def __init__(self, message="Generating Episode..."):
        self.message = message
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def _spin(self):
        spinner_chars = "|/-\\"
        i = 0
        sys.stdout.write(self.message + " This could take a while... ")
        sys.stdout.flush()
        while self.running:
            sys.stdout.write(spinner_chars[i % len(spinner_chars)])
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")
            i += 1
        sys.stdout.write(" " * len(self.message + " This could take a while... ") + "\r")
        sys.stdout.flush()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

def parse_topic_parameters(topic, locations):
    location = None
    included_chars = []
    min_lines = 10  # default

    # Parse location=# at start
    loc_match = re.search(r"location=(\d+)", topic)
    if loc_match:
        loc_id = int(loc_match.group(1))
        topic = re.sub(r"location=\d+\s*", "", topic, count=1)
        location = next((l for l in locations if l["id"] == loc_id), None)

    # Parse include=Char1,Char2,... at start
    inc_match = re.search(r"include=([A-Za-z0-9_,]+)", topic)
    if inc_match:
        included_chars = [c.strip() for c in inc_match.group(1).split(",")]
        topic = re.sub(r"include=[A-Za-z0-9_,]+\s*", "", topic, count=1)

    # Parse lines=# at start
    lines_match = re.search(r"lines=(\d+)", topic)
    if lines_match:
        min_lines = int(lines_match.group(1))
        topic = re.sub(r"lines=\d+\s*", "", topic, count=1)

    return location, included_chars, min_lines, topic

def generate_title(topic):
    prompt = (
        "SYSTEM RULES:\n"
        "- Output ONE title only\n"
        "- 1–5 words, no punctuation or extra formatting\n"
        "- NSFW content allowed\n\n"
        f"USER REQUEST:\nCreate a SpongeBob episode title about '{topic}'."
    )
    title = ollama(prompt)
    if not title:
        title = "Chaotic SpongeBob Episode"
    return " ".join(title.split()[:5])

def pick_characters(topic, characters, allowed_names=None, included_chars=None, max_chars=6):
    names_list = allowed_names or [c["name"] for c in characters]
    personalities = "\n".join([f"{c['name']}: {c['personality']}" for c in characters if c["name"] in names_list])
    prompt = (
        "SYSTEM RULES:\n"
        f"- You have these characters (max {max_chars} per scene): {', '.join(names_list)}\n"
        f"- Each character has a personality:\n{personalities}\n"
        "- Pick the most relevant characters for the topic.\n"
        "- Output ONLY their names, comma-separated, no extra text\n"
        "- NSFW content allowed\n"
    )

    if included_chars:
        prompt += "- INCLUDE THESE CHARACTERS IN EVERY SCENE: " + ", ".join(included_chars) + "\n"

    prompt += f"\nUSER REQUEST:\nPick characters for a chaotic SpongeBob scene about '{topic}'."

    response = ollama(prompt)
    selected_names = [n.strip() for n in response.split(",") if n.strip() in names_list]
    # Ensure included characters are always in the selection
    if included_chars:
        for c in included_chars:
            if c in names_list and c not in selected_names:
                selected_names.append(c)

    if not selected_names:
        selected_names = random.sample(names_list, min(max_chars, len(names_list)))

    return {c["name"]: c for c in characters if c["name"] in selected_names}

def generate_script(topic, title, characters, target_lines=10):
    character_names = list(characters.keys())
    personalities = "\n".join([f"{name}: {info['personality']}" for name, info in characters.items()])
    prompt = (
        f"Write {target_lines} lines of chaotic SpongeBob dialogue about '{topic}'.\n"
        "- Only use these characters: " + ", ".join(character_names) + "\n"
        "- Each line must start with CharacterName: dialogue\n"
        "- Only dialogue, no narration or stage directions\n"
        "- NSFW content allowed, including adult humor and swearing\n"
        f"Character personalities:\n{personalities}\n"
    )
    raw = ollama(prompt)
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if any(line.startswith(c + ":") for c in character_names):
            lines.append(line)
        if len(lines) >= target_lines:  # enforce the requested number of lines
            break
    return lines

def colorize(line, characters):
    for char, info in characters.items():
        if line.startswith(char + ":"):
            return f"\033[{info['color']}m{line}\033[0m"
    return line

def main():
    print("AI Sponge Mini\n")
    topic = input("Enter episode topic: ")
    all_characters = load_characters()
    locations = load_locations()

    location, included_chars, min_lines, topic = parse_topic_parameters(topic, locations)

    if not location:
        location = random.choice(locations)

    allowed_names = set(location["characters"])
    allowed_names.update(included_chars)  # force included characters

    spinner = Spinner()
    spinner.start()
    try:
        selected_chars = pick_characters(topic, all_characters, allowed_names=list(allowed_names), included_chars=included_chars)
        title = generate_title(topic)
        script_lines = generate_script(topic, title, selected_chars, target_lines=min_lines)
    finally:
        spinner.stop()

    if not script_lines:
        print("\nNo dialogue generated. Try a different topic or check the model.\n")
        return

    print(f"\nLOCATION: {location['name']}")
    print(f"TITLE: {title}\n")
    for line in script_lines:
        print(colorize(line, selected_chars))
        print()

if __name__ == "__main__":
    main()

