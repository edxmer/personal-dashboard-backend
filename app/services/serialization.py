import pickle

def save_data(data: object, path: str) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f)
    
def load_data(path: str) -> object:
    with open(path, "rb") as f:
        loaded_object = pickle.load(f)
    return loaded_object