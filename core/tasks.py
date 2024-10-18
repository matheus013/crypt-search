# core/tasks.py
import hashlib
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from Pyfhel import PyCtxt
from celery import shared_task
from django.db import transaction

from core.models.container import TextVector
from core.tools.key import VectorModelManager
from core.tools.vector import encrypted_dot_product
from core.tools.vector import normalize_vector, vectorize_text, encrypt_vector

logger = logging.getLogger(__name__)


@shared_task
def save_encrypted_vectors_task(texts, user_id, batch_size=1000):
    """
    Task Celery para salvar vetores criptografados em lotes para grandes volumes de textos.
    Também retorna o tamanho do dado original e do dado criptografado para cada vetor.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.get(id=user_id)

        vector_data = []
        size_comparisons = []  # Lista para armazenar os tamanhos originais e criptografados

        for i, text in enumerate(texts):
            vector = vectorize_text(text)
            normalized_vector = normalize_vector(vector) # TODO explorar tamanho max suportado
            encrypted_vector = encrypt_vector(normalized_vector)

            checksum = hashlib.sha256(normalized_vector.tobytes()).hexdigest()

            identifier = uuid.uuid4()

            original_size_kb = len(vector.tobytes()) / 1024

            encrypted_size_kb = len(encrypted_vector.to_bytes()) / 1024

            vector_data.append(
                TextVector(
                    identifier=identifier,
                    encrypted_vector=encrypted_vector.to_bytes(),
                    checksum=checksum,
                    owner=user
                )
            )

            # Armazena a comparação de tamanhos
            size_comparisons.append({
                'identifier': identifier,
                'original_size_kb': original_size_kb,
                'encrypted_size_kb': encrypted_size_kb,
                'checksum': checksum
            })

            # Quando atingir o batch_size, salva o lote
            if (i + 1) % batch_size == 0:
                _save_batch(vector_data)
                vector_data.clear()  # Limpa a lista após o salvamento

        # Salva o último lote restante
        if vector_data:
            _save_batch(vector_data)

        logger.info(f"Vetores criptografados salvos com sucesso para o usuário {user}")
        return size_comparisons
    except Exception as e:
        logger.error(f"Erro ao salvar vetores criptografados: {e}")
        return []


def _save_batch(vector_data):
    """Salva um lote de vetores criptografados."""
    with transaction.atomic():  # Usa transações para garantir integridade
        TextVector.objects.bulk_create(vector_data)  # Salva em massa para otimizar


@shared_task
def compare_with_existing_vectors_task(text, user_id, batch_size=1000):
    """
    Task Celery para comparar um texto com os vetores criptografados existentes do usuário em lotes.
    Retorna apenas as 10 maiores similaridades.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        manager = VectorModelManager()
        vector_new_text = normalize_vector(vectorize_text(text))
        enc_vector_new_text = encrypt_vector(vector_new_text)

        similarities = []
        he_instance = manager.get_he()

        # Paginação para evitar carregar todos os dados de uma vez
        stored_vectors = TextVector.objects.filter(owner=user).iterator(chunk_size=batch_size)

        # Processa os vetores paginados em paralelo usando um pool de threads
        with ThreadPoolExecutor() as executor:
            futures = []
            batch = []
            for stored_vector in stored_vectors:
                enc_vector_stored = PyCtxt(pyfhel=he_instance, bytestring=bytes(stored_vector.encrypted_vector))
                batch.append((enc_vector_new_text, enc_vector_stored, stored_vector.identifier))

                # Quando atingir o batch_size, envia para processamento paralelo
                if len(batch) >= batch_size:
                    futures.append(executor.submit(_process_batch, batch, he_instance))
                    batch = []

            # Processa o último lote
            if batch:
                futures.append(executor.submit(_process_batch, batch, he_instance))

            # Espera e coleta os resultados
            for future in futures:
                similarities.extend(future.result())

        # Ordena as similaridades pelo maior valor e seleciona os 10 maiores
        top_similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:10]

        return top_similarities
    except Exception as e:
        logger.error(f"Erro ao comparar vetores: {e}")
        return []


def _process_batch(batch, he_instance):
    """
    Processa um lote de comparações de vetores.
    :param batch: Lista de tuplas com (enc_vector_new_text, enc_vector_stored, identifier).
    :param he_instance: Instância do Pyfhel para manipulação de criptografia.
    :return: Lista de dicionários com identifier e similaridade.
    """
    results = []
    for enc_vector_new_text, enc_vector_stored, identifier in batch:
        enc_similarity = encrypted_dot_product(enc_vector_new_text, enc_vector_stored)
        similarity = he_instance.decrypt(enc_similarity)
        results.append({"identifier": identifier, "similarity": float(np.sum(similarity))})
    return results
