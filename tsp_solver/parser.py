import re
import numpy as np

def parse_tsp(filepath: str) -> dict:
    """
    Parses a TSPLIB .tsp file and extracts metadata and 2D coordinates.
    """
    metadata = {
        'name': '',
        'type': '',
        'comment': '',
        'dimension': 0,
        'edge_weight_type': 'EUC_2D',
        'coords': None
    }
    
    coords = []
    reading_coords = False
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            
            if line_str == 'EOF' or line_str.startswith('EOF'):
                break
                
            if line_str.startswith('NODE_COORD_SECTION'):
                reading_coords = True
                continue
                
            if not reading_coords:
                if ':' in line_str:
                    key, val = line_str.split(':', 1)
                    key = key.strip().upper()
                    val = val.strip()
                    if key == 'NAME':
                        metadata['name'] = val
                    elif key == 'TYPE':
                        metadata['type'] = val
                    elif key == 'COMMENT':
                        metadata['comment'] = val
                    elif key == 'DIMENSION':
                        metadata['dimension'] = int(val)
                    elif key == 'EDGE_WEIGHT_TYPE':
                        metadata['edge_weight_type'] = val
            else:
                parts = line_str.split()
                if len(parts) >= 3:
                    try:
                        # parts[0] is node id, parts[1] is x, parts[2] is y
                        x = float(parts[1])
                        y = float(parts[2])
                        coords.append([x, y])
                    except ValueError:
                        continue

    metadata['coords'] = np.array(coords, dtype=np.float64)
    if metadata['dimension'] == 0:
        metadata['dimension'] = len(coords)
    if not metadata['name']:
        import os
        metadata['name'] = os.path.splitext(os.path.basename(filepath))[0]
        
    return metadata

