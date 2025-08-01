"""
Marker Parser Engine for processing standardized markers in script output
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MarkerType(Enum):
    STEP_START = "STEP_START"
    STEP_COMPLETE = "STEP_COMPLETE"
    STEP_ERROR = "STEP_ERROR"
    ARTIFACT = "ARTIFACT"
    META = "META"
    LOG = "LOG"
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedMarker:
    """Represents a parsed marker from script output"""
    marker_type: MarkerType
    content: str
    parameters: Dict[str, Any]
    original_line: str
    line_number: int = 0
    
    @property
    def step_name(self) -> Optional[str]:
        """Get step name for step-related markers"""
        if self.marker_type in [MarkerType.STEP_START, MarkerType.STEP_COMPLETE, MarkerType.STEP_ERROR]:
            return self.content
        return None
    
    @property
    def artifact_info(self) -> Optional[Tuple[str, str]]:
        """Get artifact file and description for artifact markers"""
        if self.marker_type == MarkerType.ARTIFACT:
            parts = self.content.split(':', 1)
            if len(parts) == 2:
                return parts[0], parts[1]
            return parts[0], ""
        return None
    
    @property
    def meta_key_value(self) -> Optional[Tuple[str, str]]:
        """Get metadata key-value pair for meta markers"""
        if self.marker_type == MarkerType.META:
            parts = self.content.split(':', 1)
            if len(parts) == 2:
                return parts[0], parts[1]
        return None


class MarkerParser:
    """Parser for standardized markers in script output"""
    
    def __init__(self):
        self.line_number = 0
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile regex patterns for marker detection"""
        self.patterns = {
            MarkerType.STEP_START: re.compile(
                r'^(?:.*?)?STEP_START:(.+?)(?:\s*$)',
                re.IGNORECASE
            ),
            MarkerType.STEP_COMPLETE: re.compile(
                r'^(?:.*?)?STEP_COMPLETE:(.+?)(?:\s*$)',
                re.IGNORECASE
            ),
            MarkerType.STEP_ERROR: re.compile(
                r'^(?:.*?)?STEP_ERROR:(.+?)(?:\s*$)',
                re.IGNORECASE
            ),
            MarkerType.ARTIFACT: re.compile(
                r'^(?:.*?)?ARTIFACT:(.+?)(?:\s*$)',
                re.IGNORECASE
            ),
            MarkerType.META: re.compile(
                r'^(?:.*?)?META:(.+?)(?:\s*$)',
                re.IGNORECASE
            )
        }
    
    def parse_line(self, line: str) -> ParsedMarker:
        """Parse a single line of output for markers"""
        self.line_number += 1
        line = line.strip()
        
        # Try to match each marker type
        for marker_type, pattern in self.patterns.items():
            match = pattern.search(line)
            if match:
                content = match.group(1).strip()
                return ParsedMarker(
                    marker_type=marker_type,
                    content=content,
                    parameters=self._extract_parameters(content),
                    original_line=line,
                    line_number=self.line_number
                )
        
        # No marker found, treat as log
        return ParsedMarker(
            marker_type=MarkerType.LOG,
            content=line,
            parameters={},
            original_line=line,
            line_number=self.line_number
        )
    
    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        """Extract parameters from marker content"""
        parameters = {}
        
        # Look for parameter patterns like [param=value] or {param:value}
        param_patterns = [
            re.compile(r'\[(\w+)=([^\]]+)\]'),  # [duration=60]
            re.compile(r'\{(\w+):([^}]+)\}'),   # {timeout:30}
            re.compile(r'--(\w+)=(\S+)'),       # --timeout=30
        ]
        
        for pattern in param_patterns:
            for match in pattern.finditer(content):
                key, value = match.groups()
                # Try to convert to appropriate type
                try:
                    if value.lower() in ['true', 'false']:
                        parameters[key] = value.lower() == 'true'
                    elif value.isdigit():
                        parameters[key] = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        parameters[key] = float(value)
                    else:
                        parameters[key] = value
                except ValueError:
                    parameters[key] = value
        
        return parameters
    
    def reset(self):
        """Reset parser state"""
        self.line_number = 0
    
    def validate_marker_syntax(self, line: str) -> Tuple[bool, Optional[str]]:
        """Validate marker syntax and return error message if invalid"""
        line = line.strip()
        
        # Check for marker prefix
        marker_prefixes = ['STEP_START:', 'STEP_COMPLETE:', 'STEP_ERROR:', 'ARTIFACT:', 'META:']
        has_marker = any(prefix in line.upper() for prefix in marker_prefixes)
        
        if not has_marker:
            return True, None  # No marker, valid
        
        # Validate specific marker formats
        if 'STEP_START:' in line.upper():
            match = self.patterns[MarkerType.STEP_START].search(line)
            if not match or not match.group(1).strip():
                return False, "STEP_START marker requires a step name"
        
        elif 'STEP_COMPLETE:' in line.upper():
            match = self.patterns[MarkerType.STEP_COMPLETE].search(line)
            if not match or not match.group(1).strip():
                return False, "STEP_COMPLETE marker requires a step name"
        
        elif 'STEP_ERROR:' in line.upper():
            match = self.patterns[MarkerType.STEP_ERROR].search(line)
            if not match or not match.group(1).strip():
                return False, "STEP_ERROR marker requires an error description"
        
        elif 'ARTIFACT:' in line.upper():
            match = self.patterns[MarkerType.ARTIFACT].search(line)
            if not match or not match.group(1).strip():
                return False, "ARTIFACT marker requires a file path"
            content = match.group(1).strip()
            if ':' not in content:
                return False, "ARTIFACT marker format should be 'ARTIFACT:file_path:description'"
        
        elif 'META:' in line.upper():
            match = self.patterns[MarkerType.META].search(line)
            if not match or not match.group(1).strip():
                return False, "META marker requires key:value pair"
            content = match.group(1).strip()
            if ':' not in content:
                return False, "META marker format should be 'META:key:value'"
        
        return True, None
    
    def get_marker_examples(self) -> Dict[MarkerType, List[str]]:
        """Get example markers for documentation"""
        return {
            MarkerType.STEP_START: [
                "echo \"STEP_START:Environment Setup\"",
                "print(\"STEP_START:Data Processing\")",
                "// STEP_START:Code Compilation",
                "STEP_START:Model Training [duration=300]"
            ],
            MarkerType.STEP_COMPLETE: [
                "echo \"STEP_COMPLETE:Environment Setup\"",
                "print(\"STEP_COMPLETE:Data Processing\")",
                "// STEP_COMPLETE:Code Compilation",
                "STEP_COMPLETE:Model Training"
            ],
            MarkerType.STEP_ERROR: [
                "echo \"STEP_ERROR:Failed to install dependencies\"",
                "print(\"STEP_ERROR:Data validation failed\")",
                "STEP_ERROR:Compilation failed with exit code 1"
            ],
            MarkerType.ARTIFACT: [
                "echo \"ARTIFACT:test_results.xml:Test Report\"",
                "print(\"ARTIFACT:model.pkl:Trained Model\")",
                "ARTIFACT:coverage.html:Coverage Report",
                "ARTIFACT:logs/training.log:Training Logs"
            ],
            MarkerType.META: [
                "echo \"META:ESTIMATED_DURATION:300\"",
                "print(\"META:DESCRIPTION:This step processes the data\")",
                "META:TIMEOUT:600",
                "META:RETRY_COUNT:3"
            ]
        }
    
    def get_documentation(self) -> str:
        """Get markdown documentation for marker usage"""
        examples = self.get_marker_examples()
        
        doc = """# ContainerFlow Marker Reference

## Overview
ContainerFlow uses standardized markers to detect steps and collect artifacts from your scripts.

## Marker Types

### Step Control Markers

#### STEP_START
Marks the beginning of a new step.
```bash
# Examples:
""" + '\n'.join(examples[MarkerType.STEP_START]) + """
```

#### STEP_COMPLETE  
Marks successful completion of a step.
```bash
# Examples:
""" + '\n'.join(examples[MarkerType.STEP_COMPLETE]) + """
```

#### STEP_ERROR
Marks step failure with error description.
```bash
# Examples:
""" + '\n'.join(examples[MarkerType.STEP_ERROR]) + """
```

### Artifact Markers

#### ARTIFACT
Declares a generated file as an artifact.
```bash
# Format: ARTIFACT:file_path:description
# Examples:
""" + '\n'.join(examples[MarkerType.ARTIFACT]) + """
```

### Metadata Markers

#### META
Provides metadata for the current step.
```bash
# Format: META:key:value
# Examples:
""" + '\n'.join(examples[MarkerType.META]) + """
```

## Language Integration

### Shell Scripts
```bash
#!/bin/bash
echo "STEP_START:Setup Environment"
pip install -r requirements.txt
echo "STEP_COMPLETE:Setup Environment"
```

### Python Scripts
```python
print("STEP_START:Data Processing")
# Your code here
df = process_data()
print("ARTIFACT:processed_data.csv:Processed Dataset")
print("STEP_COMPLETE:Data Processing")
```

### Docker Files
```dockerfile
FROM python:3.9
RUN echo "STEP_START:Base Image Setup"
RUN echo "STEP_COMPLETE:Base Image Setup"
```

## Best Practices

1. **Consistent Naming**: Use descriptive step names
2. **Error Handling**: Always use STEP_ERROR for failures
3. **Artifact Documentation**: Provide clear descriptions
4. **Metadata Usage**: Use META for additional context
"""
        return doc