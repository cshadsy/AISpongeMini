# AISpongeMini

**AI Sponge Mini** is a Spongebob episode generator akin to AI Sponge Rehydrated. AI Sponge Mini is not affiliated with AI Sponge Rehydrated, Paramount, Nickelodeon, or Viacom.

---

## Features

- Generates **1–5 word episode titles**.  
- Creates **10–15 line scripts** featuring Spongebob characters.   
- **Locations** control which characters appear in a scene.  
- **Color-coded dialogue** per character.  
- **cross-platform**: Linux, Windows, macOS.  
- Works free and offline using Ollama!

---

## Requirements

- Python 3.13+  
- [Ollama](https://ollama.com) running locally  
- `requests` Python library  
- Terminal with ANSI color support (Windows 10+ CMD, PowerShell, Linux, macOS, pretty much anything modern)  

Install dependencies:

```bash
pip install requests
```

---

## Installation

Clone the repository or download the source code from Releases and navigate into the project directory:

```bash
git clone https://github.com/cshadsy/AISpongeMini.git
cd AISpongeMini
```

Ensure `characters.json` and `locations.json` exist in the same directory as `sponge.py`.

---

## Usage

Run the script:

```bash
python sponge.py
```

Enter your episode topic when prompted. Optionally, you may specify a location by starting the topic with `location=#`. The script will pick characters allowed in that location and remove the location tag from the topic before generating the episode.

Color-coded dialogue will print to your terminal.

---

## Notes

- Ensure your local Ollama model (e.g., `phi3:mini`, this is customizable in the script) is running.  
- Characters and locations can be customized through `characters.json` and `locations.json`.  
- The script generates up to 10 lines per episode by default; this can be adjusted in the code.  

---

## License

MIT License – free to use and modify.  
