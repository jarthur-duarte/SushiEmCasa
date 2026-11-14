"""Armazenamento das fotos enviadas pelo painel (banners e produtos) no Vercel Blob.

Na Vercel o disco do servidor é temporário, então os uploads não podem ficar em
MEDIA_ROOT. Este storage só é usado quando BLOB_READ_WRITE_TOKEN está definido
(veja STORAGES em settings.py); no computador de vocês continua valendo a pasta media/.
"""
import mimetypes
import posixpath
import uuid

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class VercelBlobStorage(Storage):
    def __init__(self, base_url=None):
        self._base_url = base_url

    # --- auxiliares -------------------------------------------------------
    def _sdk(self):
        from vercel.blob import sync as blob  # importado só quando necessário
        return blob

    @property
    def base_url(self):
        if not self._base_url:
            from vercel.blob._internal.credentials import default_sync_credentials
            store_id = default_sync_credentials().store_id
            self._base_url = f"https://{store_id}.public.blob.vercel-storage.com/"
        return self._base_url

    # --- API do Storage ---------------------------------------------------
    def _open(self, name, mode="rb"):
        from django.core.files.base import ContentFile
        resultado = self._sdk().get_blob(self.url(name), access="public")
        return ContentFile(resultado.body, name=name)

    def _save(self, name, content):
        if hasattr(content, "seek"):
            content.seek(0)
        dados = content.read()
        tipo = getattr(content, "content_type", None) or mimetypes.guess_type(name)[0]
        resultado = self._sdk().put_blob(
            name, dados, access="public", content_type=tipo, allow_overwrite=True,
        )
        return resultado.pathname

    def get_available_name(self, name, max_length=None):
        # evita sobrescrever fotos com o mesmo nome sem precisar consultar o Blob
        pasta, arquivo = posixpath.split(name.replace("\\", "/"))
        raiz, ext = posixpath.splitext(arquivo)
        novo = posixpath.join(pasta, f"{raiz}_{uuid.uuid4().hex[:8]}{ext}")
        if max_length and len(novo) > max_length:
            novo = posixpath.join(pasta, f"{uuid.uuid4().hex[:12]}{ext}")
        return novo

    def delete(self, name):
        if name:
            self._sdk().delete_blob(self.url(name))

    def exists(self, name):
        try:
            self._sdk().head_blob(self.url(name))
            return True
        except Exception:
            return False

    def size(self, name):
        return self._sdk().head_blob(self.url(name)).size

    def url(self, name):
        return self.base_url + name.replace("\\", "/").lstrip("/")
