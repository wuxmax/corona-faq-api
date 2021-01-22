from typing import List, Tuple, Mapping, Optional, Union
from numpy import ndarray
from pydantic import BaseModel

import time
import json
import os
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EncoderModel(BaseModel):
    short_name: str
    full_name: str
    vec_dims: int
    st_model: Optional[SentenceTransformer] = None

    class Config:
        arbitrary_types_allowed = True

    def load(self, model_dir: str) -> None:
        logger.info(f"Loading model '{self.short_name}'")
        self.st_model = SentenceTransformer(os.path.abspath(os.path.join(model_dir, self.full_name)))
    
    def encode(self, data: Union[str, List[str]], timed: bool = False) -> Union[Tuple[Union[ndarray, List[ndarray]], int], Union[ndarray, List[ndarray]]]:
        start_time = time.time()
        embedded_data = self.st_model.encode(data, show_progress_bar=False)
        end_time = time.time()

        if timed:
            return embedded_data, end_time - start_time
        else:
            return embedded_data


class EncoderManager:
    models: Mapping[str, EncoderModel]
    model_dir : str
    
    def __init__(self, models: Mapping, model_dir: str, load_models: bool = False):
        
        models_ = [EncoderModel(**model) for model in models]

        if load_models:
            for model in models_: model.load(model_dir)
        
        self.models = {model.short_name: model for model in models_}
        self.model_dir = model_dir

    def encode(self, data: Union[str, List[str]], model_name: str = None) -> Union[Union[ndarray, List[ndarray]], Mapping[str, Union[ndarray, List[ndarray]]]]:
        
        if not model_name:
            for model in self.models.values():
                if not model.st_model:
                    model.load(self.model_dir)
            
            return {model_name: model.encode(data) for model_name, model in self.models.items()}

        else:
            try:
                model = self.models[model_name]
            except KeyError:
                logger.error(f"Model with name {model_name} not defined!")

            # model not loaded yet
            if not model.st_model:
                model.load()

            return model.encode(data)

    def encode_timed(self, data: Union[str, List[str]], model_name: str) -> Tuple[Union[ndarray, List[ndarray]], int]:
        try:
            model = self.models[model_name]
        except KeyError:
            logger.error(f"Model with name {model_name} not defined!")

        # model not loaded yet
        if not model.st_model:
            model.load()

        return model.encode(data, timed=True)

                
                



            







    

