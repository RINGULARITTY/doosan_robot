import pandas as pd
from typing import Dict, List
from path_changer import resource_path
import os
import pandas as pd
import lz4.frame
from cryptography.fernet import Fernet
from key_gen import KeyGen
import pickle

class Material:
    def __init__(self, name, data: Dict[str, List[float]]):
        self.name = name
        self.data: pd.DataFrame = pd.DataFrame.from_dict(data)

    @staticmethod
    def from_dataframe(name, data) -> "Material":
        m = Material(name, None)
        m.data = data
        return m

class Materials:
    MATERIALS_FOLDER = resource_path("materials")
    TRANSLATIONS = {
        "steel": "Acier",
        "aluminum": "Aluminium"
    }
    
    def __init__(self):
        self.materials: List[Material] = []
    
    def load(self, key):
        self.materials = []
        cipher_suite = Fernet(key)
        for file in [f for f in os.listdir(Materials.MATERIALS_FOLDER) if f.split(".")[-1] == "bin"]:
            material_name = ".".join(file.split(".")[:-1])

            with open(os.path.join(Materials.MATERIALS_FOLDER, file), 'rb') as f:
                encrypted_data_read = f.read()

            decrypted_data = cipher_suite.decrypt(encrypted_data_read)
            decompressed_data = lz4.frame.decompress(decrypted_data)
            df_reloaded = pickle.loads(decompressed_data)
            
            self.materials.append(Material.from_dataframe(material_name, df_reloaded))

    def add_materials(self, materials: List[Material]) -> "Materials":
        self.materials.extend(materials)
        return self
    
    def save(self, key):
        cipher_suite = Fernet(key)
        for m in self.materials:
            df_bytes = pickle.dumps(m.data)
            compressed_data = lz4.frame.compress(df_bytes)
            encrypted_data = cipher_suite.encrypt(compressed_data)
            with open(os.path.join(Materials.MATERIALS_FOLDER, f"{m.name}.bin"), 'wb') as f:
                f.write(encrypted_data)
            
    def get_materials_names(self):
        return [m.name for m in self.materials]

if __name__ == "__main__":

    # Create materials
    STEEL = Material("steel", {
        "bead_widths": [3, 4, 5, 6, 8, 10, 12],
        "job": [9]*7,
        "synergic_id": [0]*7,
        "robot_speed": [8.33]*7,
        "passes_amount": [1]*7
    })
    
    ALUMINUM = Material("aluminum", {
        "bead_widths": [3, 4, 5, 6, 8, 10, 12],
        "job": [9]*7,
        "synergic_id": [0]*7,
        "robot_speed": [8.33]*7,
        "passes_amount": [1]*7
    })

    # Load key to decode
    key = KeyGen.get_key("main_2023_08_30_15_23_16")
    
    # Save all materials
    Materials().add_materials([STEEL, ALUMINUM]).save(key)
    
    # Load materials
    m = Materials()
    m.load(key)