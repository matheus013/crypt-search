import os

from Pyfhel import Pyfhel
from sentence_transformers import SentenceTransformer


class VectorModelManager:
    _instance = None
    model = None
    HE = None
    context_generated = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorModelManager, cls).__new__(cls)
            cls._initialize(cls._instance)

        return cls._instance

    @classmethod
    def _initialize(cls, instance):
        instance.model = SentenceTransformer('all-MiniLM-L6-v2')
        instance.HE = Pyfhel(key_gen=False)

        if cls.check_existing_keys():
            instance.load()
        else:
            instance.HE.contextGen(scheme='ckks', n=2 ** 14, scale=2 ** 30, qi_sizes=[60, 30, 30, 30, 60])

            instance.HE.keyGen()
            instance.save()

    @classmethod
    def check_existing_keys(cls):
        """Verifica se todos os arquivos de chave e contexto necessários já existem."""
        required_files = [
            '.env/secret_key',
            '.env/public_key',
            '.env/context'
        ]
        return all(os.path.exists(file) for file in required_files)

    def get_model(self):
        return self.model

    def get_he(self):
        return self.HE

    def save(self):
        """Salva as chaves e o contexto."""
        os.makedirs('.env', exist_ok=True)

        self.HE.save_context(fileName='.env/context')
        self.HE.save_secret_key(fileName='.env/secret_key')
        self.HE.save_public_key(fileName='.env/public_key')

    def load(self):
        """Carrega o contexto e as chaves salvas."""
        self.HE.load_context(fileName='.env/context')

        self.HE.load_secret_key(fileName='.env/secret_key')
        self.HE.load_public_key(fileName='.env/public_key')

    def regenerate_keys(self):
        """Método para regerar as chaves e salvar o novo estado no arquivo."""
        self.HE.keyGen()
        self.save()
