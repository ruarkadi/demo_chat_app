from .validation_schemas import validation_schemas
import jsonschema

def validate_request_input(req_path, req_method):
  validation_data = validation_schemas[req_path][req_method]['validation_data_func']()
  if validation_data == None:
    return True
  return jsonschema.validate(instance=validation_schemas[req_path][req_method]['validation_data_func'](), schema=validation_schemas[req_path][req_method]['schema'])