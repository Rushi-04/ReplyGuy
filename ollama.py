import requests
import json


def query_ollama(prompt, model="gemma3:1b"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error Connecting to ollama: {e}")
        return None


if __name__ == "__main__":
    prompt_text = "Consider Your Name is ReplyGuy, Hello ReplyGuy"
    answer = query_ollama(prompt_text)
    # answer = stream_query_ollama(prompt_text)
    print("Model Output: ")
    print(answer)