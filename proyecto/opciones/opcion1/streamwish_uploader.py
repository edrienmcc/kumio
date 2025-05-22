import requests
import logging
import json
import os
from pathlib import Path
import time

# Configurar logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('StreamWishUploader')

class StreamWishUploader:
    """
    Cliente para subir videos a StreamWish usando su API
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.upload_url = "https://s1.myvideo.com/upload/01"
        self.alternative_url = "http://s1.xvs.tt/upload/01"
        
        # Headers para las requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Configuración por defecto
        self.default_config = {
            'file_public': 1,      # Público por defecto
            'file_adult': 1,       # Contenido adulto
            'tags': 'pornhub, video, hd',
            'fld_id': None,        # Carpeta (opcional)
            'cat_id': None         # Categoría (opcional)
        }
    
    def set_api_key(self, api_key):
        """
        Establece la clave API
        """
        self.api_key = api_key
        logger.info("✅ API key configurada")
    
    def upload_video(self, video_path, video_data=None, custom_config=None):
        """
        Sube un video a StreamWish
        
        Args:
            video_path: Ruta al archivo de video
            video_data: Datos del video (título, descripción, etc.)
            custom_config: Configuración personalizada
            
        Returns:
            dict: Respuesta de la API con información del video subido
        """
        try:
            if not self.api_key:
                logger.error("❌ API key no configurada")
                return None
            
            if not os.path.exists(video_path):
                logger.error(f"❌ Archivo no encontrado: {video_path}")
                return None
            
            # Preparar datos del video
            upload_data = self._prepare_upload_data(video_data, custom_config)
            
            # Preparar archivos
            files = self._prepare_files(video_path, video_data)
            
            logger.info(f"📤 Iniciando upload: {os.path.basename(video_path)}")
            logger.info(f"📊 Tamaño del archivo: {self._get_file_size_mb(video_path):.1f} MB")
            
            # Intentar upload con URL principal
            response = self._upload_to_server(self.upload_url, upload_data, files)
            
            # Si falla, intentar con URL alternativa
            if not response:
                logger.warning("⚠️ Reintentando con servidor alternativo...")
                response = self._upload_to_server(self.alternative_url, upload_data, files)
            
            if response:
                return self._process_response(response)
            else:
                logger.error("❌ Upload falló en ambos servidores")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error durante el upload: {str(e)}")
            return None
    
    def upload_multiple_videos(self, video_paths, video_data_list=None):
        """
        Sube múltiples videos en una sola request
        """
        try:
            if not self.api_key:
                logger.error("❌ API key no configurada")
                return None
            
            # Verificar que todos los archivos existan
            for path in video_paths:
                if not os.path.exists(path):
                    logger.error(f"❌ Archivo no encontrado: {path}")
                    return None
            
            logger.info(f"📤 Iniciando upload múltiple: {len(video_paths)} videos")
            
            # Preparar datos
            upload_data = {'key': self.api_key}
            upload_data.update(self.default_config)
            
            # Preparar archivos múltiples
            files = []
            for i, video_path in enumerate(video_paths):
                video_data = video_data_list[i] if video_data_list and i < len(video_data_list) else None
                file_data = self._prepare_files(video_path, video_data)
                files.extend(file_data)
            
            # Upload
            response = self._upload_to_server(self.upload_url, upload_data, files)
            
            if response:
                return self._process_response(response)
            else:
                logger.error("❌ Upload múltiple falló")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error durante upload múltiple: {str(e)}")
            return None
    
    def _prepare_upload_data(self, video_data, custom_config):
        """
        Prepara los datos para el upload
        """
        upload_data = {'key': self.api_key}
        
        # Configuración por defecto
        upload_data.update(self.default_config)
        
        # Configuración personalizada
        if custom_config:
            upload_data.update(custom_config)
        
        # Datos del video
        if video_data:
            if video_data.get('title'):
                upload_data['file_title'] = self._clean_title(video_data['title'])
            
            if video_data.get('description'):
                upload_data['file_descr'] = video_data['description']
            
            # Agregar tags adicionales basados en el video
            additional_tags = self._generate_tags(video_data)
            if additional_tags:
                existing_tags = upload_data.get('tags', '')
                upload_data['tags'] = f"{existing_tags}, {additional_tags}"
        
        return upload_data
    
    def _prepare_files(self, video_path, video_data):
        """
        Prepara los archivos para el upload
        """
        files = []
        
        # Archivo de video principal
        files.append(('file', (
            os.path.basename(video_path),
            open(video_path, 'rb'),
            'video/mp4'
        )))
        
        # Buscar snapshot/thumbnail si existe
        snapshot_path = self._find_snapshot(video_path, video_data)
        if snapshot_path and os.path.exists(snapshot_path):
            files.append(('snapshot', (
                os.path.basename(snapshot_path),
                open(snapshot_path, 'rb'),
                'image/jpeg'
            )))
            logger.info(f"📸 Snapshot incluido: {os.path.basename(snapshot_path)}")
        
        return files
    
    def _upload_to_server(self, url, data, files):
        """
        Realiza el upload al servidor
        """
        try:
            logger.info(f"🌐 Conectando a: {url}")
            
            # Realizar upload con progreso
            response = requests.post(
                url,
                data=data,
                files=files,
                headers=self.headers,
                timeout=300,  # 5 minutos timeout
                stream=True
            )
            
            # Cerrar archivos abiertos
            for file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1][1], 'close'):
                    file_tuple[1][1].close()
            
            if response.status_code == 200:
                logger.info("✅ Upload completado exitosamente")
                return response
            else:
                logger.error(f"❌ Error HTTP: {response.status_code}")
                logger.error(f"❌ Respuesta: {response.text[:500]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout durante el upload")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ Error de conexión")
            return None
        except Exception as e:
            logger.error(f"❌ Error en upload: {str(e)}")
            return None
    
    def _process_response(self, response):
        """
        Procesa la respuesta del servidor
        """
        try:
            # Intentar parsear como JSON
            try:
                result = response.json()
                logger.info("📋 Respuesta JSON recibida")
            except json.JSONDecodeError:
                # Si no es JSON, puede ser HTML redirect
                result = {
                    'status': 200,
                    'msg': 'Upload successful (HTML response)',
                    'html_response': response.text[:1000]
                }
                logger.info("📋 Respuesta HTML recibida")
            
            # Procesar resultado
            if result.get('status') == 200:
                logger.info("✅ Upload exitoso!")
                
                # Mostrar información de archivos subidos
                if 'files' in result:
                    for file_info in result['files']:
                        filecode = file_info.get('filecode', 'N/A')
                        filename = file_info.get('filename', 'N/A')
                        file_status = file_info.get('status', 'N/A')
                        
                        logger.info(f"📁 Archivo: {filename}")
                        logger.info(f"🔗 Código: {filecode}")
                        logger.info(f"📊 Estado: {file_status}")
                        
                        # Construir URLs de acceso
                        if filecode != 'N/A':
                            view_url = f"https://streamwish.to/{filecode}"
                            embed_url = f"https://streamwish.to/e/{filecode}"
                            
                            logger.info(f"🌐 Ver: {view_url}")
                            logger.info(f"📺 Embed: {embed_url}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando respuesta: {str(e)}")
            return None
    
    def _clean_title(self, title):
        """
        Limpia el título para StreamWish
        """
        # Eliminar caracteres especiales
        clean_title = title.replace('\n', ' ').replace('\r', ' ')
        
        # Limitar longitud
        if len(clean_title) > 100:
            clean_title = clean_title[:97] + "..."
        
        return clean_title.strip()
    
    def _generate_tags(self, video_data):
        """
        Genera tags adicionales basados en los datos del video
        """
        tags = []
        
        # Tags basados en duración
        if video_data.get('duration'):
            duration = video_data['duration']
            if ':' in duration:
                try:
                    parts = duration.split(':')
                    minutes = int(parts[-2]) if len(parts) > 1 else 0
                    if minutes > 30:
                        tags.append('long')
                    elif minutes > 15:
                        tags.append('medium')
                    else:
                        tags.append('short')
                except:
                    pass
        
        # Tags basados en uploader
        if video_data.get('uploader'):
            uploader = video_data['uploader'].lower()
            if any(word in uploader for word in ['premium', 'official', 'verified']):
                tags.append('premium')
        
        return ', '.join(tags)
    
    def _find_snapshot(self, video_path, video_data):
        """
        Busca un archivo de snapshot/thumbnail
        """
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Posibles nombres de snapshot
        snapshot_names = [
            f"{video_name}.jpg",
            f"{video_name}.jpeg",
            f"{video_name}.png",
            f"{video_name}_thumb.jpg",
            "thumbnail.jpg"
        ]
        
        for name in snapshot_names:
            snapshot_path = os.path.join(video_dir, name)
            if os.path.exists(snapshot_path):
                return snapshot_path
        
        return None
    
    def _get_file_size_mb(self, file_path):
        """
        Obtiene el tamaño del archivo en MB
        """
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0
    
    def test_connection(self):
        """
        Prueba la conexión con la API
        """
        try:
            if not self.api_key:
                logger.error("❌ API key no configurada para test")
                return False
            
            # Crear un archivo de prueba pequeño
            test_file_path = "test_upload.txt"
            with open(test_file_path, 'w') as f:
                f.write("Test upload file")
            
            test_data = {
                'key': self.api_key,
                'file_title': 'Test Upload',
                'file_descr': 'Test file for API validation'
            }
            
            files = [('file', ('test.txt', open(test_file_path, 'rb'), 'text/plain'))]
            
            response = requests.post(
                self.upload_url,
                data=test_data,
                files=files,
                headers=self.headers,
                timeout=30
            )
            
            # Limpiar archivo de prueba
            files[0][1][1].close()
            os.remove(test_file_path)
            
            if response.status_code == 200:
                logger.info("✅ Conexión con StreamWish exitosa")
                return True
            else:
                logger.error(f"❌ Error en test: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en test de conexión: {str(e)}")
            return False