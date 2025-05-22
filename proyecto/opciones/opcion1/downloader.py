import requests
from bs4 import BeautifulSoup
import logging
import json
import re
import os
import time
import subprocess
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Configurar logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('VideoDownloader')

class VideoDownloader:
    def __init__(self):
        self.base_url = "https://es.pornhub.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://es.pornhub.com/'
        }
        
        # Crear carpeta de descargas si no existe
        self.download_folder = Path.home() / "Downloads" / "PornhubVideos"
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
    def download_video(self, video_url, video_data):
        """
        Descarga un video desde la URL proporcionada
        """
        try:
            logger.info(f"🔍 Analizando video: {video_data.get('title', 'Sin título')}")
            
            # Obtener el HTML de la página del video
            response = requests.get(video_url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"❌ Error al acceder a la página: {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar las URLs de video en los scripts
            video_urls = self._extract_video_urls(response.text)
            
            if not video_urls:
                logger.error("❌ No se encontraron URLs de video")
                return False
            
            # Seleccionar la mejor calidad disponible
            best_video_url, video_format = self._select_best_quality(video_urls)
            
            if not best_video_url:
                logger.error("❌ No se pudo determinar la mejor calidad")
                return False
            
            logger.info(f"🎥 URL de video encontrada: {best_video_url[:100]}...")
            logger.info(f"📹 Formato detectado: {video_format}")
            
            # Descargar según el formato
            if video_format == 'hls':
                return self._download_hls_with_ffmpeg(best_video_url, video_data)
            elif video_format == 'mp4':
                return self._download_direct_mp4(best_video_url, video_data)
            else:
                logger.error(f"❌ Formato no soportado: {video_format}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error general durante la descarga: {str(e)}")
            return False
    
    def _extract_video_urls(self, html_content):
        """
        Extrae las URLs de video del HTML, priorizando MP4 directo sobre HLS
        """
        video_urls = {}
        
        try:
            # Buscar en flashvars
            flashvars_match = re.search(r'var flashvars_\d+\s*=\s*({.*?});', html_content, re.DOTALL)
            if flashvars_match:
                flashvars_str = flashvars_match.group(1)
                # Limpiar y parsear JSON
                flashvars_str = re.sub(r',\s*}', '}', flashvars_str)
                flashvars_str = re.sub(r',\s*]', ']', flashvars_str)
                
                try:
                    flashvars = json.loads(flashvars_str)
                    
                    # Buscar mediaDefinitions
                    if 'mediaDefinitions' in flashvars:
                        for media in flashvars['mediaDefinitions']:
                            if 'videoUrl' in media and 'quality' in media:
                                quality = media['quality']
                                if isinstance(quality, list) and len(quality) > 0:
                                    quality = quality[0]
                                elif isinstance(quality, str):
                                    quality = quality
                                else:
                                    quality = str(quality)
                                
                                video_url = media['videoUrl']
                                
                                # Determinar formato
                                if '.m3u8' in video_url or '/hls/' in video_url:
                                    format_type = 'hls'
                                elif '.mp4' in video_url and 'seg-' not in video_url:
                                    format_type = 'mp4'
                                else:
                                    format_type = 'unknown'
                                
                                video_urls[quality] = {
                                    'url': video_url,
                                    'format': format_type
                                }
                                logger.info(f"📹 Calidad encontrada: {quality} ({format_type})")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Error parseando flashvars JSON: {str(e)}")
            
            # Método alternativo: buscar URLs directamente en el HTML
            if not video_urls:
                logger.info("🔍 Buscando URLs alternativas...")
                # Buscar patrones de URLs de video MP4 directos
                mp4_patterns = [
                    r'"(https://[^"]*\.mp4[^"]*)"',
                    r'videoUrl:\s*"([^"]+\.mp4[^"]*)"',
                ]
                
                for pattern in mp4_patterns:
                    matches = re.findall(pattern, html_content)
                    for match in matches:
                        # Limpiar URL
                        clean_url = match.replace('\\/', '/')
                        if 'mp4' in clean_url and 'seg-' not in clean_url:
                            # Intentar extraer calidad del URL
                            quality_match = re.search(r'(\d+)P?_', clean_url)
                            quality = quality_match.group(1) if quality_match else 'unknown'
                            video_urls[quality] = {
                                'url': clean_url,
                                'format': 'mp4'
                            }
                            logger.info(f"📹 MP4 directo encontrado: {quality}")
            
            return video_urls
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo URLs de video: {str(e)}")
            return {}
    
    def _select_best_quality(self, video_urls):
        """
        Selecciona la mejor calidad disponible, priorizando MP4 directo
        """
        if not video_urls:
            return None, None
        
        # Prioridad de calidades (de mayor a menor)
        quality_priority = ['1080', '720', '480', '240']
        
        # Primero buscar MP4 directo
        for quality in quality_priority:
            if quality in video_urls and video_urls[quality]['format'] == 'mp4':
                logger.info(f"✅ Seleccionado MP4 directo: {quality}p")
                return video_urls[quality]['url'], 'mp4'
        
        # Si no hay MP4 directo, buscar HLS
        for quality in quality_priority:
            if quality in video_urls and video_urls[quality]['format'] == 'hls':
                logger.info(f"⚠️ Seleccionado HLS: {quality}p")
                return video_urls[quality]['url'], 'hls'
        
        # Último recurso: tomar cualquier formato disponible
        first_quality = list(video_urls.keys())[0]
        video_info = video_urls[first_quality]
        logger.info(f"⚠️ Usando formato disponible: {first_quality} ({video_info['format']})")
        return video_info['url'], video_info['format']
    
    def _download_direct_mp4(self, video_url, video_data):
        """
        Descarga un archivo MP4 directo
        """
        return self._download_file(video_url, video_data, '.mp4')
    
    def _download_hls_with_ffmpeg(self, m3u8_url, video_data):
        """
        Descarga un stream HLS usando ffmpeg
        """
        try:
            # Verificar si ffmpeg está instalado
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("❌ FFmpeg no está instalado. Instalando...")
                return self._install_and_use_ffmpeg(m3u8_url, video_data)
            
            # Limpiar el nombre del archivo
            title = video_data.get('title', 'video_sin_titulo')
            safe_title = self._clean_filename(title)
            filename = f"{safe_title}.mp4"
            filepath = self.download_folder / filename
            
            # Verificar si el archivo ya existe
            if filepath.exists():
                logger.info(f"ℹ️ El archivo ya existe: {filename}")
                return True
            
            logger.info(f"⬇️ Descargando HLS: {filename}")
            
            # Comando ffmpeg
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', m3u8_url,
                '-c', 'copy',  # Copiar sin recodificar
                '-bsf:a', 'aac_adtstoasc',  # Fix para audio AAC
                '-y',  # Sobrescribir archivo si existe
                str(filepath)
            ]
            
            # Ejecutar ffmpeg
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Descarga HLS completada: {filepath}")
                return True
            else:
                logger.error(f"❌ Error en ffmpeg: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error descargando HLS: {str(e)}")
            return False
    
    def _install_and_use_ffmpeg(self, m3u8_url, video_data):
        """
        Intenta instalar ffmpeg y descargar el video
        """
        try:
            import platform
            system = platform.system().lower()
            
            logger.info("🔧 Intentando instalar ffmpeg...")
            
            if system == "darwin":  # macOS
                try:
                    # Intentar instalar con Homebrew
                    subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                    return self._download_hls_with_ffmpeg(m3u8_url, video_data)
                except subprocess.CalledProcessError:
                    logger.error("❌ No se pudo instalar ffmpeg con Homebrew")
            
            elif system == "linux":
                try:
                    # Intentar con apt
                    subprocess.run(['sudo', 'apt', 'update'], check=True)
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
                    return self._download_hls_with_ffmpeg(m3u8_url, video_data)
                except subprocess.CalledProcessError:
                    logger.error("❌ No se pudo instalar ffmpeg con apt")
            
            # Fallback: descargar segmentos manualmente
            logger.warning("⚠️ Fallback: descargando segmentos HLS manualmente...")
            return self._download_hls_manually(m3u8_url, video_data)
            
        except Exception as e:
            logger.error(f"❌ Error en instalación de ffmpeg: {str(e)}")
            return False
    
    def _download_hls_manually(self, m3u8_url, video_data):
        """
        Descarga manual de HLS obteniendo la playlist y segmentos
        """
        try:
            logger.info("📋 Descargando playlist HLS...")
            
            # Descargar playlist m3u8
            response = requests.get(m3u8_url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"❌ Error descargando playlist: {response.status_code}")
                return False
            
            playlist_content = response.text
            
            # Extraer URLs de segmentos
            segment_urls = []
            base_url = m3u8_url.rsplit('/', 1)[0] + '/'
            
            for line in playlist_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('http'):
                        segment_urls.append(line)
                    else:
                        segment_urls.append(base_url + line)
            
            if not segment_urls:
                logger.error("❌ No se encontraron segmentos en la playlist")
                return False
            
            logger.info(f"📦 Encontrados {len(segment_urls)} segmentos")
            
            # Descargar segmentos y combinar
            title = video_data.get('title', 'video_sin_titulo')
            safe_title = self._clean_filename(title)
            temp_folder = self.download_folder / f"temp_{safe_title}"
            temp_folder.mkdir(exist_ok=True)
            
            # Descargar cada segmento
            for i, segment_url in enumerate(segment_urls):
                try:
                    segment_response = requests.get(segment_url, headers=self.headers)
                    if segment_response.status_code == 200:
                        segment_path = temp_folder / f"segment_{i:04d}.ts"
                        with open(segment_path, 'wb') as f:
                            f.write(segment_response.content)
                        
                        if i % 10 == 0:  # Log cada 10 segmentos
                            progress = (i + 1) / len(segment_urls) * 100
                            logger.info(f"📊 Progreso: {progress:.1f}% ({i+1}/{len(segment_urls)})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error descargando segmento {i}: {str(e)}")
            
            # Combinar segmentos
            final_path = self.download_folder / f"{safe_title}.mp4"
            with open(final_path, 'wb') as output_file:
                for i in range(len(segment_urls)):
                    segment_path = temp_folder / f"segment_{i:04d}.ts"
                    if segment_path.exists():
                        with open(segment_path, 'rb') as segment_file:
                            output_file.write(segment_file.read())
            
            # Limpiar archivos temporales
            import shutil
            shutil.rmtree(temp_folder)
            
            logger.info(f"✅ Video HLS combinado: {final_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en descarga manual HLS: {str(e)}")
            return False
    
    def _download_file(self, video_url, video_data, extension='.mp4'):
        """
        Descarga un archivo directo
        """
        try:
            # Limpiar el nombre del archivo
            title = video_data.get('title', 'video_sin_titulo')
            safe_title = self._clean_filename(title)
            filename = f"{safe_title}{extension}"
            filepath = self.download_folder / filename
            
            # Verificar si el archivo ya existe
            if filepath.exists():
                logger.info(f"ℹ️ El archivo ya existe: {filename}")
                return True
            
            logger.info(f"⬇️ Descargando: {filename}")
            
            # Realizar la descarga
            with requests.get(video_url, headers=self.headers, stream=True) as response:
                response.raise_for_status()
                
                # Obtener el tamaño total si está disponible
                total_size = int(response.headers.get('content-length', 0))
                
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    chunk_size = 8192
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Mostrar progreso cada MB
                            if downloaded % (1024 * 1024) == 0 or downloaded == total_size:
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    logger.info(f"📊 Progreso: {progress:.1f}% ({downloaded / (1024*1024):.1f}MB)")
                                else:
                                    logger.info(f"📊 Descargado: {downloaded / (1024*1024):.1f}MB")
            
            logger.info(f"✅ Descarga completada: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la descarga del archivo: {str(e)}")
            return False
    
    def _clean_filename(self, filename):
        """
        Limpia el nombre del archivo para que sea válido en el sistema de archivos
        """
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        
        # Reemplazar caracteres inválidos
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limitar longitud
        if len(filename) > 100:
            filename = filename[:100]
        
        # Eliminar espacios al inicio y final
        filename = filename.strip()
        
        return filename