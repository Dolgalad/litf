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

class CodeExecutionStatus:
    SUCCESS=0
    MISSING_CODE_FILE=1
    NAME_NOT_IN_CONTEXT=2
    DECLARATION_ERROR=3
    INSTANTIATION_ERROR=4
    EXECUTION_ERROR=5
    OUTPUT_NOT_PKL_SERIALIZABLE=6
    INPUT_LOAD_ERROR=7
    CONSTRUCTOR_INPUT_LOAD_ERROR=8
    CLASS_INSTANTIATION_ERROR=9
    UNKWN_CODE_TYPE=10
    OUTPUT_CONVERSION_ERROR=11
    INSTANCE_NOT_CALLABLE_ERROR=12
    PENDING=13
    RUNNING=14
    UNCHECKED=-1

execution_status_msg={-2:"failure",\
                      -1:"unchecked",\
                      0:"success",\
                      1:"missing_code_file",\
                      2:"name_not_in_context",\
                      3:"declaration_error",\
                      4:"instantiation_error",\
                      5:"execution_error",\
                      6:"output_unserializable",\
                      7:"input_load_error",\
                      8:"constructor_input_load_error",\
                      9:"class_instantiation_error",\
                      10:"unknown_code_type",\
                      11:"output_conversion_error",\
                      12:"instance_not_callable_error",\
                      13:"pending",\
                      14:"running"}
