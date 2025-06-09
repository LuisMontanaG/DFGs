import os
import pandas as pd

class DataManager:
    def __init__(self, data_folder: str = "data/"):
        self.data_root = data_folder
        self.data = {}
        self.datasets = {}
        self.dataset = None
        self.file_paths = {}

        self.load_datasets()

    def load_datasets(self):
        try:
            folders = [name for name in os.listdir(self.data_root) if os.path.isdir(os.path.join(self.data_root, name))]
            self.datasets = {folder: folder for folder in folders}
        except Exception as e:
            print(f"Failed to load datasets from {self.data_root}: {e}")
            self.datasets = {}

    def load_dataset(self, dataset_name):
        self.dataset = dataset_name
        self.data_root = os.path.join(self.data_root, dataset_name)
        event_types_path = os.path.join(self.data_root, "event_types_" + dataset_name + ".csv")
        clustering_path = os.path.join(self.data_root, "clustering_" + dataset_name + ".txt")
        good_k_path = os.path.join(self.data_root, "good_k_" + dataset_name + ".txt")
        unique_sequences_path = os.path.join(self.data_root, "unique_sequences_" + dataset_name + ".csv")
        self.file_paths = {
            "event_types": event_types_path,
            "clustering": clustering_path,
            "good_k": good_k_path,
            "unique_sequences": unique_sequences_path,
        }

    def load_files(self):
        # Load event types from the database
        self.data["event_types"] = self.load_event_types()
        # Create acronym for event types
        self.data["event_types_acronyms"] = self.create_event_types_acronyms(self.data["event_types"])
        # Load clustering data
        self.data["clustering"] = self.load_clustering()
        # Load good k values
        self.data["good_k"] = self.load_good_k()
        # Load unique sequences
        self.data["unique_sequences"] = self.load_unique_sequences()

    def load_event_types(self):
        types = {}
        if os.path.exists(self.file_paths["event_types"]):
            try:
                df = pd.read_csv(self.file_paths["event_types"])
                print(f"Loaded event types with shape {df.shape} from {self.file_paths['event_types']}")
                # Convert to dictionary with id as key and event type as value
                types = df.set_index('id_eventType')['type'].to_dict()
                self.data["event_types"] = types
            except Exception as e:
                print(f"Failed to load data from {self.file_paths['event_types']}: {e}")
        else:
            print(f"Event types file {self.file_paths['event_files']} does not exist.")
        return types

    def load_clustering(self):
        clustering = {}
        if os.path.exists(self.file_paths["clustering"]):
            try:
                with open(self.file_paths["clustering"], "r") as f:
                    for line in f:
                        if 'k' in line:
                            k = int(line.split(':')[1].strip())
                            clustering[k] = {}
                        if 'cluster' in line:
                            line_array = line.split(';')
                            cluster_id = int(line_array[1].strip())
                            nodes = list(line_array[2].strip().split(':')[1].strip().split(','))
                            clustering[k][cluster_id] = nodes
            except Exception as e:
                print(f"Failed to load clustering data from {self.file_paths['clustering']}: {e}")
        else:
            print(f"Clustering file {self.file_paths['clustering']} does not exist.")
        return clustering

    def load_good_k(self):
        good_k = {}
        if os.path.exists(self.file_paths["good_k"]):
            try:
                with open(self.file_paths["good_k"], "r") as f:
                    for line in f:
                        if 'best' in line:
                            k = int(line.split(':')[1].strip())
                            good_k['best'] = k
                        if 'good' in line:
                            k = list(line.split(':')[1].strip().split(','))
                            # Remove first element of list since it is repeated
                            k.pop(0)
                            good_k['good'] = k
            except Exception as e:
                print(f"Failed to load good k values from {self.file_paths['good_k']}: {e}")
        else:
            print(f"Good k file {self.file_paths['good_k']} does not exist.")
        return good_k

    def load_unique_sequences(self):
        if os.path.exists(self.file_paths["unique_sequences"]):
            try:
                df = pd.read_csv(self.file_paths["unique_sequences"])
                # Sort by frequency and reset index
                self.data["unique_sequences"] = df
                print(f"Loaded unique sequences with shape {df.shape} from {self.file_paths['unique_sequences']}")
                return df
            except Exception as e:
                print(f"Failed to read unique sequences from {self.file_paths['unique_sequences']}: {e}")
                return None
        else:
            print(f"Unique sequences file {self.file_paths['unique_sequences']} does not exist.")
            return None

    def get_max_k(self):
        if self.data.get("clustering"):
            return max(self.data["clustering"].keys(), default=None)
        return None

    def get_min_k(self):
        if self.data.get("clustering"):
            return min(self.data["clustering"].keys(), default=None)
        return None

    def get_best_k(self):
        return self.data.get("good_k", {}).get('best', None)

    def get_good_k(self):
        return self.data.get("good_k", {}).get('good', None)

    def get_clustering(self, k):
        clustering = self.data.get("clustering", {}).get(k, None)
        clustering = self.sort_clustering_by_frequency(clustering)
        return clustering

    def get_unique_sequences(self):
        return self.data.get("unique_sequences", None)

    def get_event_types(self):
        return self.data.get("event_types", None)

    def get_event_types_acronyms(self):
        return self.data.get("event_types_acronyms", None)

    def get_available_datasets(self):
        return [{"label": label, "value": key} for key, label in self.datasets.items()]

    def sort_clustering_by_frequency(self, clustering):
        unique_sequences = self.get_unique_sequences()

        k_frequencies = {}

        for k, ids in clustering.items():
            total_frequency = 0
            for id in ids:
                total_frequency += unique_sequences.loc[unique_sequences['id_uniqueSeq'] == int(id), 'frequency'].values[0]
            k_frequencies[k] = total_frequency

        # Sort clustering by frequency
        sorted_clustering = dict(sorted(clustering.items(), key=lambda item: k_frequencies[item[0]], reverse=True))
        return sorted_clustering

    def create_event_types_acronyms(self, event_types):
        acronyms = {}
        for event_type in event_types.values():
            # If the event type is only one word, use the first 3 characters
            if len(event_type.split()) == 1:
                acronyms[event_type] = event_type[:3].upper()
            else:
                # If the event type is multiple words, use the first letter of the first three words that are longer that two letters
                words = event_type.split()
                acronyms[event_type] = ''.join([word[0].upper() for word in words if len(word) > 2][:3])
        return acronyms