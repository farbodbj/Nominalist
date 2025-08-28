import re
from typing import Optional
import pandas as pd
from functools import lru_cache
from rapidfuzz.distance import Levenshtein, JaroWinkler, DamerauLevenshtein
from typing import List, Tuple, Optional
import logging 

TOP_K = 3
LOG_ENABLED = True
NATIVE_LANG = 'fa'

class DataManager:
    """
    Handles loading and providing access to datasets.
    """
    def __init__(self, names_file: str) -> None:
        self.names_file = names_file

        self.names_df = pd.read_csv(self.names_file)

    def get_names(self, column: str) -> pd.Series:
        """
        Get the names column from the names dataframe.

        :param column: Column name ('name' or 'english_name').
        :return: Pandas Series of names.
        """
        return self.names_df[column]

class NameMatcher:
    """
    Handles matching names using various similarity metrics.
    """

    def __init__(self, data_manager: DataManager, top_k: int = TOP_K, debug: bool = LOG_ENABLED) -> None:
        self.data_manager = data_manager
        self.top_k = top_k
        self.debug = debug

    @lru_cache(maxsize=1024)
    def get_top_matches(
            self,
            name: str,
            lang: str,
            method: str = 'levenshtein'
    ) -> List[Tuple[str, float, str, int]]:
        """
        Get top N matches based on the specified similarity method.

        :param name: The name to match.
        :param lang: Language of the name ('en' or NATIVE_LANG).
        :param method: The similarity method ('levenshtein', 'damerau', 'jaro_winkler').
        :return: List of tuples containing matched name, score, gender, and index.
        """
        column = 'name' if lang == NATIVE_LANG else 'english_name'
        if method == 'levenshtein':
            return self._get_top_matches_levenshtein(name, column)
        elif method == 'damerau':
            return self._get_top_matches_damerau_levenshtein(name, column)
        elif method == 'jaro_winkler':
            return self._get_top_matches_jaro_winkler(name, column)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def _get_top_matches_levenshtein(
            self,
            name: str,
            column: str
    ) -> List[Tuple[str, float, str, int]]:
        scores = self.data_manager.get_names(column).apply(
            lambda x: Levenshtein.normalized_similarity(name, x) * 100
        )
        top_indices = scores.nlargest(self.top_k).index
        matches = [
            (
                self.data_manager.names_df.at[idx, column],
                scores.at[idx],
                self.data_manager.names_df.at[idx, 'english_name'],
                idx
            )
            for idx in top_indices
        ]
        if self.debug:
            logging.info(f"[Levenshtein] Name: {name}, Matches: {matches}")
        return matches

    def _get_top_matches_damerau_levenshtein(
            self,
            name: str,
            column: str
    ) -> List[Tuple[str, float, str, int]]:
        scores = self.data_manager.get_names(column).apply(
            lambda x: DamerauLevenshtein.normalized_similarity(name, x) * 100
        )
        top_indices = scores.nlargest(self.top_k).index
        matches = [
            (
                self.data_manager.names_df.at[idx, column],
                scores.at[idx],
                self.data_manager.names_df.at[idx, 'english_name'],
                idx
            )
            for idx in top_indices
        ]
        if self.debug:
            logging.info(f"[Damerau-Levenshtein] Name: {name}, Matches: {matches}")
        return matches

    def _get_top_matches_jaro_winkler(
            self,
            name: str,
            column: str
    ) -> List[Tuple[str, float, str, int]]:
        scores = self.data_manager.get_names(column).apply(
            lambda x: JaroWinkler.similarity(name, x) * 100
        )
        top_indices = scores.nlargest(self.top_k).index
        matches = [
            (
                self.data_manager.names_df.at[idx, column],
                scores.at[idx],
                self.data_manager.names_df.at[idx, 'english_name'],
                idx
            )
            for idx in top_indices
        ]
        if self.debug:
            logging.info(f"[Jaro-Winkler] Name: {name}, Matches: {matches}")
        return matches



class NameService:
    """Service to get English writing of names from various languages."""
    
    def __init__(self):
        self.data_manager = DataManager(names_file='src/dataset/persian-gender-by-name.csv')    
        self.name_matcher = NameMatcher(data_manager=self.data_manager)
        
    def get_english_name(self, name: str) -> str:
        """
        Get English writing of a name.
        Returns the English equivalent or the original if already in English.
        """
        native_matches = self.name_matcher.get_top_matches(name = name, lang = NATIVE_LANG)
        print(f"native: {native_matches}")
        english_mathces = self.name_matcher.get_top_matches(name = name, lang = 'english_name')
        print(f"english: {english_mathces}")
        
        
        top_match = sorted(english_mathces + native_matches, key=lambda x: x[1], reverse=True)[0]
        return top_match[2]
            
