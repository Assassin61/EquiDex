import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config(path: str = "fairprobe.config.yaml") -> dict:
    """
    Reads the config file and returns it as a dictionary.
    Everything in the app reads from this config.
    """
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    
    # Override AI api key from environment variable
    # Never hardcode API keys in config file
    config["ai"]["api_key"] = os.getenv("GEMINI_API_KEY", "")
    
    return config


def get_bias_dimensions(config: dict) -> list:
    """
    Returns list of dimensions to audit from config.
    Example: ["name_origin", "age_group", "ethnicity"]
    """
    return config["audit_dimensions"]


def get_candidate_fields(config: dict) -> list:
    """
    Returns list of candidate fields from config.
    Each field has a name and optional bias_dimension.
    """
    return config["candidate_fields"]


def get_thresholds(config: dict) -> dict:
    """
    Returns bias detection thresholds from config.
    high_bias: flag if disparity exceeds this %
    medium_bias: flag if disparity exceeds this %
    """
    return config["thresholds"]


def get_demo_settings(config: dict) -> dict:
    """
    Returns demo specific settings from config.
    Used by demo hiring AI and candidate generation.
    """
    return config["demo"]