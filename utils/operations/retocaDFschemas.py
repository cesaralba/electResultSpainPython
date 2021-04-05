#   https://pypi.org/project/jsonschema/
# https://json-schema.org/specification.html
# https://json-schema.org/understanding-json-schema/index.html

# TODO: UNITARIOS!

regexColName = r"^[_a-zA-Z][_a-zA-Z0-9]*$"
typeNumberOrValue = {"anyOf": [{"type": "string"}, {"type": "number"}]}
typeColName = {"type": "string", "pattern": regexColName, "minLength": 1}

monocolOpList = ["2numeric", "upper", "lower"]
monocolOpProperties = {k: {"$ref": "#/definitions/monocolTrfParam"} for k in monocolOpList}

errorFixSchema = {
    "type": "array",
    "definitions": {
        "colValuePair": {
            "type": "object",
            "properties": {regexColName: typeNumberOrValue},
        },
        "pairCondFix": {
            "type": "object",
            "properties": {
                "condition": {"$ref": "#/definitions/colValuePair"},
                "fix": {"$ref": "#/definitions/colValuePair"},
            },
            "required": ["condition", "fix"],
            "additionalProperties": True,
        },
    },
    "items": {"$ref": "#/definitions/pairCondFix"},
    "minItems": 1,
}

transformDFschema = {
    "type": "array",
    "definitions": {
        "colName": typeColName,
        "colList": {
            "type": "array",
            "items": {"$ref": "#/definitions/colName"},
            "minItems": 1,
        },
        "concatTrfParam": {
            "type": "object",
            "properties": {regexColName: {"$ref": "#/definitions/colList"}},
        },
        "concatTrfOp": {
            "type": "object",
            "properties": {"concat": {"$ref": "#/definitions/concatTrfParam"}},
            "additionalProperties": False,
        },
        "monocolTrfParam": {
            "type": "object",
            "properties": {
                "prefix": {"type": "string", "minLength": 1, "pattern": regexColName},
                "cols": {"$ref": "#/definitions/colList"},
            },
            "required": ["cols"],
            "additionalProperties": False,
        },
        "monocolTrfOp": {
            "type": "object",
            "properties": monocolOpProperties,
            "maxProperties": 1,
            "minProperties": 1,
            "additionalProperties": False,
        },
        "dfOps": {
            "oneOf": [
                {"$ref": "#/definitions/concatTrfOp"},
                {"$ref": "#/definitions/monocolTrfOp"},
            ]
        },
    },
    "items": {"$ref": "#/definitions/dfOps"},
    "minItems": 1,
}

validatorDFschema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "definitions": {
        "colName": typeColName,
        "colNamePair": {
            "type": "array",
            "items": {"$ref": "#/definitions/colName"},
            "minItems": 2,
            "maxItems": 2,
        },
        "complexColNamePair": {
            "type": "object",
            "properties": {"pair": {"$ref": "#/definitions/colNamePair"}},
            "required": ["pair"],
            "additionalProperties": True,
        },
        "validatorItem": {
            "oneOf": [
                {"$ref": "#/definitions/colNamePair"},
                {"$ref": "#/definitions/complexColNamePair"},
            ]
        },
    },
    "minItems": 1,
    "items": {"$ref": "#/definitions/validatorItem"},
}
