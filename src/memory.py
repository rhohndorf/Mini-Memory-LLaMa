import dataclasses
import orjson
from typing import Any, List, Optional
import numpy as np
from scipy.spatial.distance import cdist
import os
import config as cfg


EMBED_DIM = cfg.EMBED_DIM
SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS

def create_default_embeddings():
    return np.zeros((0, EMBED_DIM)).astype(np.float32)


@dataclasses.dataclass
class CacheContent:
    texts: List[str] = dataclasses.field(default_factory=list)
    embeddings: np.ndarray = dataclasses.field(
        default_factory=create_default_embeddings
    )


class Memory:

    # on load, load our database
    def __init__(self, llm) -> None:
        self.llm = llm
        self.filename = f"{cfg.MEM_FILE}.json"
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                loaded = orjson.loads(f.read())
                self.data = CacheContent(**loaded)
        else:
            self.data = CacheContent()

    def add(self, text: str):
        """
        Add text to our list of texts, add embedding as row to our
            embeddings-matrix

        Args:
            text: str

        Returns: None
        """
        if 'Command Error:' in text:
            return ""
        self.data.texts.append(text)

        embedding = self.llm.embed(text)
        vector = np.array(embedding).astype(np.float32)
        vector = vector[np.newaxis, :]
        self.data.embeddings = np.concatenate(
            [
                self.data.embeddings,
                vector,
            ],
            axis=0,
        )

        with open(self.filename, 'wb') as f:
            out = orjson.dumps(
                self.data,
                option=SAVE_OPTIONS
            )
            f.write(out)
        return text


    def get(self, data: str) -> Optional[List[Any]]:
        """
        Gets the data from the memory that is most relevant to the given data.

        Args:
            data: The data to compare to.

        Returns: The most relevant data.
        """
        return self.get_relevant(data, 1)

    def get_relevant(self, text: str, k: int) -> List[Any]:
        """"
        matrix-vector mult to find score-for-each-row-of-matrix
         get indices for top-k winning scores
         return texts for those indices
        Args:
            text: str
            k: int

        Returns: List[str]
        """
        embedding = self.llm.embed(text)
        scores = 1 - cdist(self.data.embeddings, np.expand_dims(embedding, axis=0), 'cosine').flatten()
        top_k_indices = np.argsort(scores)[-k:][::-1]
        return [self.data.texts[i] for i in top_k_indices]

    def get_stats(self):
        """
        Returns: The stats of the local cache.
        """
        return len(self.data.texts), self.data.embeddings.shape
