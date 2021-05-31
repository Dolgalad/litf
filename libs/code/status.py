"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Code status
"""

class CodeStatus:
    UNCHECKED=-1
    VALID=0
    REQUIREMENT_INVALID=1
    DEPENDENCIES_INVALID=2
    DECLARATION_INVALID=3
    INSTANTIATION_INVALID=4
    INPUT_INVALID=5
    OUTPUT_INVALID=6

class ExecutionStatus:
    SUCCESS=0
    PENDING=1
    FAIL=2
    RUNNING=3
