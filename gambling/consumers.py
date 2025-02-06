import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .models import GamblingGame

class GamblingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.game_groups = set()
        
        # Add user to their personal group
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove from all game groups
        for group in self.game_groups:
            await self.channel_layer.group_discard(
                group,
                self.channel_name
            )
        
        # Remove from user group
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'watch_game':
                await self.handle_watch_game(data)
            elif message_type == 'unwatch_game':
                await self.handle_unwatch_game(data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def handle_watch_game(self, data):
        """Handle request to watch a game"""
        game_id = data.get('game_id')
        if not game_id:
            return
        
        try:
            # Verify game exists
            await self.get_game(game_id)
            
            # Add to game group
            group_name = f"game_{game_id}"
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
            self.game_groups.add(group_name)
            
            await self.send(text_data=json.dumps({
                'type': 'watch_confirmation',
                'game_id': game_id
            }))
            
        except ObjectDoesNotExist:
            await self.send(text_data=json.dumps({
                'error': 'Game not found'
            }))
    
    async def handle_unwatch_game(self, data):
        """Handle request to unwatch a game"""
        game_id = data.get('game_id')
        if not game_id:
            return
            
        group_name = f"game_{game_id}"
        if group_name in self.game_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )
            self.game_groups.remove(group_name)
    
    async def game_update(self, event):
        """Handle game update event"""
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game_id': event['game_id'],
            'data': event['data']
        }))
    
    async def bet_placed(self, event):
        """Handle bet placed event"""
        await self.send(text_data=json.dumps({
            'type': 'bet_placed',
            'game_id': event['game_id'],
            'data': event['data']
        }))
    
    async def game_completed(self, event):
        """Handle game completed event"""
        await self.send(text_data=json.dumps({
            'type': 'game_completed',
            'game_id': event['game_id'],
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_game(self, game_id):
        """Get game from database"""
        return GamblingGame.objects.get(id=game_id) 