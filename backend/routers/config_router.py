from fastapi import APIRouter, Request, HTTPException
import yaml
import os

router = APIRouter(prefix="/config", tags=["Config"])

CONFIG_PATH = "fairprobe.config.yaml"

@router.get("/")
async def get_config(request: Request):
    """Returns the current config parsed as JSON."""
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="Config file not found")
        
    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f)
        
    return config_data

@router.post("/")
async def update_config(request: Request):
    """Updates the config with the provided JSON payload."""
    payload = await request.json()
    
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(status_code=404, detail="Config file not found")
        
    # Read current to preserve structure
    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f)
        
    # Merge updates
    def merge_dict(target, source):
        for k, v in source.items():
            if isinstance(v, dict) and k in target and isinstance(target[k], dict):
                merge_dict(target[k], v)
            else:
                target[k] = v
                
    merge_dict(config_data, payload)
    
    # Write back to file
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
    # Update app state config
    # Avoid wiping ai api key which is loaded from env during app start
    request.app.state.config.update(payload)
    
    return {"status": "success", "message": "Configuration updated successfully"}
