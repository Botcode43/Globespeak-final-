"""
WebSocket consumers for real-time translation communication
"""

import json
import asyncio
import base64
import tempfile
import os
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
# ConversationRoom and ConversationMessage models removed
from .services.translate import translate_text
from .services.stt import speech_to_text_from_bytes
from .services.tts import text_to_speech
from .services.summarize import summarize_text

logger = logging.getLogger(__name__)


class TranslationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time translation"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Handle both room-based and direct connections
            self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        self.room_group_name = f'translation_{self.room_name}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Create or get conversation room
        room = await self.get_or_create_room()
        if room:
            await self.add_user_to_room(room)
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to translation room: {self.room_name}',
            'user_id': self.user.id if self.user.is_authenticated else None,
                'username': self.user.username if self.user.is_authenticated else 'Anonymous',
                'status': 'connected',
                'debug': {
                    'client_ip': self.scope.get('client', ['unknown'])[0],
                    'user_agent': self.scope.get('headers', {}).get(b'user-agent', b'unknown').decode(),
                    'room_name': self.room_name
                }
            }))
            
            logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} connected to room {self.room_name} from {self.scope.get('client', ['unknown'])[0]}")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.username if self.user.is_authenticated else 'Anonymous'} disconnected from room {self.room_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'audio_translation':
                await self.handle_audio_translation(data)
            elif message_type == 'text_translation':
                await self.handle_text_translation(data)
            elif message_type == 'join_room':
                await self.handle_join_room(data)
            elif message_type == 'leave_room':
                await self.handle_leave_room(data)
            elif message_type == 'get_room_info':
                await self.handle_get_room_info(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error: {str(e)}'
            }))

    async def handle_audio_translation(self, data):
        """Handle real-time conversation communication: STT -> Translation -> TTS"""
        try:
            logger.info(f"Received audio translation request from {self.scope.get('client', ['unknown'])[0]}")
            
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
            
            audio_data = data.get('audio_data')
            source_lang = data.get('source_lang', 'en-US')
            target_lang = data.get('target_lang', 'hi')
            user_id = data.get('user_id', self.user.id)
            username = data.get('username', self.user.username)
            
            if not audio_data:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Audio data is required'
                }))
                return
            
            # Send processing status immediately
            await self.send(text_data=json.dumps({
                    'type': 'processing_started',
                    'user_id': user_id,
                    'username': username,
                'message': 'Processing speech...',
                'status': 'processing'
            }))
            
            # Convert base64 audio to bytes
            try:
                audio_bytes = base64.b64decode(audio_data.split(',')[1])
            except:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid audio data format'
                }))
                return
            
            # Step 1: Speech to text (optimized for speed)
            start_time = asyncio.get_event_loop().time()
            transcribed_text = await self.speech_to_text_async(audio_bytes, source_lang)
            stt_time = asyncio.get_event_loop().time() - start_time
            
            if not transcribed_text or transcribed_text.strip() == "":
                await self.send(text_data=json.dumps({
                        'type': 'processing_error',
                        'user_id': user_id,
                        'username': username,
                    'message': 'No speech detected. Please try speaking clearly.',
                    'status': 'error'
                }))
                return
            
            # Step 2: Translation (parallel processing)
            start_time = asyncio.get_event_loop().time()
            translated_text = await self.translate_text_async(
                transcribed_text, 
                source_lang.split('-')[0], 
                target_lang
            )
            translation_time = asyncio.get_event_loop().time() - start_time
            
            # Step 3: Text to speech (optimized for real-time)
            start_time = asyncio.get_event_loop().time()
            audio_url = await self.text_to_speech_async(translated_text, target_lang)
            tts_time = asyncio.get_event_loop().time() - start_time
            
            total_time = stt_time + translation_time + tts_time
            
            # Log performance metrics
            logger.info(f"Real-time processing times - STT: {stt_time:.2f}s, Translation: {translation_time:.2f}s, TTS: {tts_time:.2f}s, Total: {total_time:.2f}s")
            
            # Check if processing time is within acceptable limits (5-10 seconds)
            if total_time > 10:
                logger.warning(f"Processing time exceeded 10 seconds: {total_time:.2f}s")
            
            # Save to database (async, non-blocking)
            asyncio.create_task(self.save_conversation_message(
                transcribed_text, 
                translated_text, 
                source_lang.split('-')[0], 
                target_lang,
                audio_url
            ))
            
            # Send results directly to the client for better mobile compatibility
            await self.send(text_data=json.dumps({
                    'type': 'conversation_translation',
                    'transcribed_text': transcribed_text,
                    'translated_text': translated_text,
                    'audio_url': audio_url,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'user_id': user_id,
                    'username': username,
                    'timestamp': data.get('timestamp', ''),
                    'processing_time': total_time,
                'is_realtime': total_time <= 5,  # Mark as real-time if under 5 seconds
                'status': 'completed'
            }))
            
        except Exception as e:
            logger.error(f"Audio translation error: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Translation error: {str(e)}'
            }))

    async def handle_text_translation(self, data):
        """Handle direct text translation"""
        try:
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
            
            text = data.get('text')
            source_lang = data.get('source_lang', 'en')
            target_lang = data.get('target_lang', 'hi')
            
            if not text or not text.strip():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Text is required'
                }))
                return
            
            # Translate text
            translated_text = await self.translate_text_async(text, source_lang, target_lang)
            
            # Text to speech
            audio_url = await self.text_to_speech_async(translated_text, target_lang)
            
            # Save to database
            await self.save_conversation_message(
                text, 
                translated_text, 
                source_lang, 
                target_lang,
                audio_url
            )
            
            # Send results to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'translation_result',
                    'transcribed_text': text,
                    'translated_text': translated_text,
                    'audio_url': audio_url,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': data.get('timestamp', '')
                }
            )
            
        except Exception as e:
            logger.error(f"Text translation error: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Translation error: {str(e)}'
            }))

    async def handle_join_room(self, data):
        """Handle user joining the room"""
        try:
            if not self.user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
            
            room = await self.get_or_create_room()
            if room:
                await self.add_user_to_room(room)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
            
        except Exception as e:
            logger.error(f"Join room error: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error joining room: {str(e)}'
            }))

    async def handle_leave_room(self, data):
        """Handle user leaving the room"""
        try:
            if not self.user.is_authenticated:
                return
            
            room = await self.get_room()
            if room:
                await self.remove_user_from_room(room)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
            
        except Exception as e:
            logger.error(f"Leave room error: {str(e)}")

    async def handle_get_room_info(self, data):
        """Handle request for room information"""
        try:
            room = await self.get_room()
            if room:
                participants = await self.get_room_participants(room)
                await self.send(text_data=json.dumps({
                    'type': 'room_info',
                    'room_name': room.room_name,
                    'created_by': room.created_by.username,
                    'participants': participants,
                    'is_active': room.is_active
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Room not found'
                }))
                
        except Exception as e:
            logger.error(f"Get room info error: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error getting room info: {str(e)}'
            }))

    async def translation_result(self, event):
        """Send translation result to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'translation_result',
            'transcribed_text': event['transcribed_text'],
            'translated_text': event['translated_text'],
            'audio_url': event['audio_url'],
            'source_lang': event['source_lang'],
            'target_lang': event['target_lang'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def conversation_translation(self, event):
        """Send real-time conversation translation result"""
        await self.send(text_data=json.dumps({
            'type': 'conversation_translation',
            'transcribed_text': event['transcribed_text'],
            'translated_text': event['translated_text'],
            'audio_url': event['audio_url'],
            'source_lang': event['source_lang'],
            'target_lang': event['target_lang'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'processing_time': event.get('processing_time', 0),
            'is_realtime': event.get('is_realtime', False)
        }))

    async def processing_started(self, event):
        """Send processing started notification"""
        await self.send(text_data=json.dumps({
            'type': 'processing_started',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message']
        }))

    async def processing_error(self, event):
        """Send processing error notification"""
        await self.send(text_data=json.dumps({
            'type': 'processing_error',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message']
        }))

    async def user_joined(self, event):
        """Send user joined message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username']
        }))

    async def user_left(self, event):
        """Send user left message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username']
        }))

    # Database operations
    # Conversation room functions removed - models deleted
    @database_sync_to_async
    def get_or_create_room(self):
        """Conversation room functionality removed"""
        return None

    @database_sync_to_async
    def get_room(self):
        """Conversation room functionality removed"""
        return None

    @database_sync_to_async
    def add_user_to_room(self, room):
        """Conversation room functionality removed"""
        pass

    @database_sync_to_async
    def remove_user_from_room(self, room):
        """Conversation room functionality removed"""
        pass

    @database_sync_to_async
    def get_room_participants(self, room):
        """Conversation room functionality removed"""
        return []

    @database_sync_to_async
    def save_conversation_message(self, original_text, translated_text, source_lang, target_lang, audio_url):
        """Conversation message saving removed"""
        pass

    # Service operations
    @database_sync_to_async
    def speech_to_text_async(self, audio_bytes, language_code):
        """Convert speech to text asynchronously"""
        try:
            return speech_to_text_from_bytes(audio_bytes, language_code)
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return ""

    @database_sync_to_async
    def translate_text_async(self, text, source_lang, target_lang):
        """Translate text asynchronously"""
        try:
            return translate_text(text, source_lang, target_lang)
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text

    @database_sync_to_async
    def text_to_speech_async(self, text, language_code):
        """Convert text to speech asynchronously"""
        try:
            filepath = text_to_speech(text, language_code)
            # Return relative URL path
            return f"/media/audio/{os.path.basename(filepath)}"
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return None

            )

            

            # Send results to room

            await self.channel_layer.group_send(

                self.room_group_name,

                {

                    'type': 'translation_result',

                    'transcribed_text': text,

                    'translated_text': translated_text,

                    'audio_url': audio_url,

                    'source_lang': source_lang,

                    'target_lang': target_lang,

                    'user_id': self.user.id,

                    'username': self.user.username,

                    'timestamp': data.get('timestamp', '')

                }

            )

            

        except Exception as e:

            logger.error(f"Text translation error: {str(e)}")

            await self.send(text_data=json.dumps({

                'type': 'error',

                'message': f'Translation error: {str(e)}'

            }))



    async def handle_join_room(self, data):

        """Handle user joining the room"""

        try:

            if not self.user.is_authenticated:

                await self.send(text_data=json.dumps({

                    'type': 'error',

                    'message': 'Authentication required'

                }))

                return

            

            room = await self.get_or_create_room()

            if room:

                await self.add_user_to_room(room)

            

            await self.channel_layer.group_send(

                self.room_group_name,

                {

                    'type': 'user_joined',

                    'user_id': self.user.id,

                    'username': self.user.username

                }

            )

            

        except Exception as e:

            logger.error(f"Join room error: {str(e)}")

            await self.send(text_data=json.dumps({

                'type': 'error',

                'message': f'Error joining room: {str(e)}'

            }))



    async def handle_leave_room(self, data):

        """Handle user leaving the room"""

        try:

            if not self.user.is_authenticated:

                return

            

            room = await self.get_room()

            if room:

                await self.remove_user_from_room(room)

            

            await self.channel_layer.group_send(

                self.room_group_name,

                {

                    'type': 'user_left',

                    'user_id': self.user.id,

                    'username': self.user.username

                }

            )

            

        except Exception as e:

            logger.error(f"Leave room error: {str(e)}")



    async def handle_get_room_info(self, data):

        """Handle request for room information"""

        try:

            room = await self.get_room()

            if room:

                participants = await self.get_room_participants(room)

                await self.send(text_data=json.dumps({

                    'type': 'room_info',

                    'room_name': room.room_name,

                    'created_by': room.created_by.username,

                    'participants': participants,

                    'is_active': room.is_active

                }))

            else:

                await self.send(text_data=json.dumps({

                    'type': 'error',

                    'message': 'Room not found'

                }))

                

        except Exception as e:

            logger.error(f"Get room info error: {str(e)}")

            await self.send(text_data=json.dumps({

                'type': 'error',

                'message': f'Error getting room info: {str(e)}'

            }))



    async def translation_result(self, event):

        """Send translation result to WebSocket"""

        await self.send(text_data=json.dumps({

            'type': 'translation_result',

            'transcribed_text': event['transcribed_text'],

            'translated_text': event['translated_text'],

            'audio_url': event['audio_url'],

            'source_lang': event['source_lang'],

            'target_lang': event['target_lang'],

            'user_id': event['user_id'],

            'username': event['username'],

            'timestamp': event['timestamp']

        }))



    async def conversation_translation(self, event):

        """Send real-time conversation translation result"""

        await self.send(text_data=json.dumps({

            'type': 'conversation_translation',

            'transcribed_text': event['transcribed_text'],

            'translated_text': event['translated_text'],

            'audio_url': event['audio_url'],

            'source_lang': event['source_lang'],

            'target_lang': event['target_lang'],

            'user_id': event['user_id'],

            'username': event['username'],

            'timestamp': event['timestamp'],

            'processing_time': event.get('processing_time', 0),

            'is_realtime': event.get('is_realtime', False)

        }))



    async def processing_started(self, event):

        """Send processing started notification"""

        await self.send(text_data=json.dumps({

            'type': 'processing_started',

            'user_id': event['user_id'],

            'username': event['username'],

            'message': event['message']

        }))



    async def processing_error(self, event):

        """Send processing error notification"""

        await self.send(text_data=json.dumps({

            'type': 'processing_error',

            'user_id': event['user_id'],

            'username': event['username'],

            'message': event['message']

        }))



    async def user_joined(self, event):

        """Send user joined message to WebSocket"""

        await self.send(text_data=json.dumps({

            'type': 'user_joined',

            'user_id': event['user_id'],

            'username': event['username']

        }))



    async def user_left(self, event):

        """Send user left message to WebSocket"""

        await self.send(text_data=json.dumps({

            'type': 'user_left',

            'user_id': event['user_id'],

            'username': event['username']

        }))



    # Database operations

    # Conversation room functions removed - models deleted

    @database_sync_to_async

    def get_or_create_room(self):

        """Conversation room functionality removed"""

        return None



    @database_sync_to_async

    def get_room(self):

        """Conversation room functionality removed"""

        return None



    @database_sync_to_async

    def add_user_to_room(self, room):

        """Conversation room functionality removed"""

        pass



    @database_sync_to_async

    def remove_user_from_room(self, room):

        """Conversation room functionality removed"""

        pass



    @database_sync_to_async

    def get_room_participants(self, room):

        """Conversation room functionality removed"""

        return []



    @database_sync_to_async

    def save_conversation_message(self, original_text, translated_text, source_lang, target_lang, audio_url):

        """Conversation message saving removed"""

        pass



    # Service operations

    @database_sync_to_async

    def speech_to_text_async(self, audio_bytes, language_code):

        """Convert speech to text asynchronously"""

        try:

            return speech_to_text_from_bytes(audio_bytes, language_code)

        except Exception as e:

            logger.error(f"STT error: {str(e)}")

            return ""



    @database_sync_to_async

    def translate_text_async(self, text, source_lang, target_lang):

        """Translate text asynchronously"""

        try:

            return translate_text(text, source_lang, target_lang)

        except Exception as e:

            logger.error(f"Translation error: {str(e)}")

            return text



    @database_sync_to_async

    def text_to_speech_async(self, text, language_code):

        """Convert text to speech asynchronously"""

        try:

            filepath = text_to_speech(text, language_code)

            # Return relative URL path

            return f"/media/audio/{os.path.basename(filepath)}"

        except Exception as e:

            logger.error(f"TTS error: {str(e)}")

            return None


