import base64
import json

from core.tools.key import VectorModelManager


def pyctxt_to_json(pyctxt):
    """
    Converte um objeto PyCtxt para uma representação JSON serializável.

    Args:
        pyctxt (PyCtxt): O objeto criptografado a ser convertido.
        HE (Pyfhel): A instância de Pyfhel usada para gerenciar a criptografia.

    Returns:
        str: Uma string JSON contendo a representação base64 do objeto PyCtxt.
    """
    manager = VectorModelManager()
    pyctxt_bytes = manager.get_he().to_bytesCtxt(pyctxt)

    pyctxt_base64 = base64.b64encode(pyctxt_bytes).decode('utf-8')

    print(pyctxt_base64)

    return json.dumps({'encrypted_data': pyctxt_base64})


def json_to_pyctxt(json_str):
    """
    Converte uma string JSON contendo uma representação base64 de PyCtxt de volta para um objeto PyCtxt.

    Args:
        json_str (str): A string JSON a ser convertida.
        HE (Pyfhel): A instância de Pyfhel usada para gerenciar a criptografia.

    Returns:
        PyCtxt: O objeto PyCtxt reconstruído a partir do JSON.
    """
    manager = VectorModelManager()
    pyctxt_dict = json.loads(json_str)
    pyctxt_base64 = pyctxt_dict['encrypted_data']

    pyctxt_bytes = base64.b64decode(pyctxt_base64)

    pyctxt = manager.get_he().from_bytes(pyctxt_bytes)

    return pyctxt
