import numpy as np

from core.tools.key import VectorModelManager


def vectorize_text(text):
    manager = VectorModelManager()
    vector = manager.get_model().encode(text)

    return vector


def normalize_vector(vector):
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector
    return vector / norm


def encrypt_vector(vector): # TODO tornar mertodo de encrypt um argumento
    manager = VectorModelManager()
    encrypted_vector = manager.get_he().encrypt(vector)
    return encrypted_vector


def encrypted_dot_product(enc_vector1, enc_vector2):
    multiplied = enc_vector1 * enc_vector2

    return multiplied


def encrypt_vector_elementwise(vector):
    """
    Criptografa cada elemento de um vetor individualmente usando a instância do Pyfhel.

    Args:
        vector (np.ndarray): O vetor de números float a ser criptografado.

    Returns:
        list: Lista de elementos criptografados (PyCtxt).
    """

    manager = VectorModelManager()
    encrypted_vector = [manager.get_he().encryptFrac(float(val)) for val in vector]
    return encrypted_vector
