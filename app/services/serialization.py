from pathlib import Path
import pickle

def save_data(data: object, path: str | Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f)
    
def load_data(path: str | Path):
    with open(path, "rb") as f:
        loaded_object = pickle.load(f)
    return loaded_object