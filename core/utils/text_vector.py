# import hashlib
# import logging
# import uuid
# from concurrent.futures import ThreadPoolExecutor
#
# import numpy as np
# from Pyfhel import PyCtxt
# from django.db import transaction
#
# from core.models.container import TextVector
# from core.tools.key import VectorModelManager
# from core.tools.vector import encrypted_dot_product
# from core.tools.vector import normalize_vector, vectorize_text, encrypt_vector
#
# logger = logging.getLogger(__name__)
#
#
# def save_encrypted_vectors(texts, user, batch_size=1000):
#     """
#     Salva vetores criptografados em lotes para grandes volumes de textos com checksum para verificar integridade.
#     Também retorna o tamanho do dado original e do dado criptografado para cada vetor.
#
#     :param texts: Lista de textos a serem transformados em vetores.
#     :param user: Usuário dono dos vetores criptografados.
#     :param batch_size: Quantidade de registros processados por lote.
#     :return: Lista de dicionários contendo o identificador, checksum e comparativo de tamanho.
#     """
#     try:
#         if not texts or not user:
#             raise ValueError("Texto e usuário são obrigatórios")
#
#         vector_data = []  # Lista para armazenar vetores a serem salvos
#         size_comparisons = []  # Lista para armazenar os tamanhos originais e criptografados
#
#         for i, text in enumerate(texts):
#             vector = vectorize_text(text)
#             normalized_vector = normalize_vector(vector)
#             encrypted_vector = encrypt_vector(normalized_vector)
#
#             # Calcula o checksum (usando SHA-256) do vetor original (antes da criptografia)
#             checksum = hashlib.sha256(normalized_vector.tobytes()).hexdigest()
#
#             identifier = uuid.uuid4()
#
#             # Tamanho do vetor original em KB
#             original_size_kb = len(normalized_vector.tobytes()) / 1024  # Convertido de bytes para KB
#             # Tamanho do vetor criptografado em KB
#             encrypted_size_kb = len(encrypted_vector.to_bytes()) / 1024  # Convertido de bytes para KB
#
#             # Armazena os dados a serem salvos
#             vector_data.append(
#                 TextVector(
#                     identifier=identifier,
#                     encrypted_vector=encrypted_vector.to_bytes(),
#                     checksum=checksum,  # Armazena o checksum
#                     owner=user
#                 )
#             )
#
#             # Armazena a comparação de tamanhos
#             size_comparisons.append({
#                 'identifier': identifier,
#                 'original_size_kb': original_size_kb,
#                 'encrypted_size_kb': encrypted_size_kb,
#                 'checksum': checksum
#             })
#
#             # Quando atingir o batch_size, salva o lote
#             if (i + 1) % batch_size == 0:
#                 _save_batch(vector_data)
#                 vector_data.clear()  # Limpa a lista após o salvamento
#
#         # Salva o último lote restante
#         if vector_data:
#             _save_batch(vector_data)
#
#         logger.info(f"Vetores criptografados salvos com sucesso para o usuário {user}")
#         return size_comparisons
#     except Exception as e:
#         logger.error(f"Erro ao salvar vetores criptografados: {e}")
#         return []
#
#
# def _save_batch(vector_data):
#     """Salva um lote de vetores criptografados."""
#     with transaction.atomic():  # Usa transações para garantir integridade
#         TextVector.objects.bulk_create(vector_data)  # Salva em massa para otimizar
#
#
# # TODO 1 - 1
# def compare_with_existing_vectors(text, user, batch_size=1000):
#     """
#     Compara um texto com os vetores criptografados existentes do usuário em lotes.
#
#     :param text: Texto a ser comparado.
#     :param user: Usuário dono dos vetores armazenados.
#     :param batch_size: Tamanho do lote para processamento.
#     :return: Lista de dicionários com identificador e similaridade.
#     """
#     manager = VectorModelManager()
#     vector_new_text = normalize_vector(vectorize_text(text))
#     enc_vector_new_text = encrypt_vector(vector_new_text)
#
#     similarities = []
#     he_instance = manager.get_he()
#
#     # Paginação para evitar carregar todos os dados de uma vez
#     stored_vectors = TextVector.objects.filter(owner=user).iterator(chunk_size=batch_size)
#
#     # Processa os vetores paginados em paralelo usando um pool de threads
#     with ThreadPoolExecutor() as executor:
#         futures = []
#         batch = []
#         for stored_vector in stored_vectors:
#             enc_vector_stored = PyCtxt(pyfhel=he_instance, bytestring=bytes(stored_vector.encrypted_vector))
#             batch.append((enc_vector_new_text, enc_vector_stored, stored_vector.identifier))
#
#             # Quando atingir o batch_size, envia para processamento paralelo
#             if len(batch) >= batch_size:
#                 futures.append(executor.submit(_process_batch, batch, he_instance))
#                 batch = []
#
#         # Processa o último lote
#         if batch:
#             futures.append(executor.submit(_process_batch, batch, he_instance))
#
#         # Espera e coleta os resultados
#         for future in futures:
#             similarities.extend(future.result())
#
#     return similarities
#
#
# def _process_batch(batch, he_instance):
#     """
#     Processa um lote de comparações de vetores.
#     :param batch: Lista de tuplas com (enc_vector_new_text, enc_vector_stored, identifier).
#     :param he_instance: Instância do Pyfhel para manipulação de criptografia.
#     :return: Lista de dicionários com identifier e similaridade.
#     """
#     results = []
#     for enc_vector_new_text, enc_vector_stored, identifier in batch:
#         enc_similarity = encrypted_dot_product(enc_vector_new_text, enc_vector_stored)
#         similarity = he_instance.decrypt(enc_similarity)
#         results.append({"identifier": identifier, "similarity": float(np.sum(similarity))})
#     return results
