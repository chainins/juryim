from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import WithdrawalRequest
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ManagementConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Check permissions
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
            
        if not self.scope['user'].has_perm('financial.manage_withdrawals'):
            await self.close()
            return
            
        await self.accept()
        await self.channel_layer.group_add(
            'management_notifications',
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'management_notifications',
            self.channel_name
        )

    async def receive_json(self, content):
        """Handle incoming messages"""
        message_type = content.get('type')
        if message_type == 'subscribe_withdrawal':
            withdrawal_id = content.get('withdrawal_id')
            if withdrawal_id:
                await self.channel_layer.group_add(
                    f'withdrawal_{withdrawal_id}',
                    self.channel_name
                )

    async def withdrawal_update(self, event):
        """Send withdrawal update to client"""
        await self.send_json({
            'type': 'withdrawal_update',
            'withdrawal_id': event['withdrawal_id'],
            'status': event['status'],
            'updated_at': event['updated_at']
        })

    async def notification(self, event):
        """Send notification to client"""
        await self.send_json({
            'type': 'notification',
            'message': event['message'],
            'level': event['level']
        })

class WithdrawalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # Get withdrawal ID from URL path
        self.withdrawal_id = self.scope['url_route']['kwargs']['withdrawal_id']
        
        # Verify withdrawal belongs to user
        if not await self.can_access_withdrawal():
            await self.close()
            return

        self.room_name = f"withdrawal_{self.withdrawal_id}"
        self.room_group_name = f"withdrawal_updates_{self.withdrawal_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages (if needed)"""
        pass

    async def withdrawal_update(self, event):
        """Handle withdrawal update message"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'withdrawal_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def can_access_withdrawal(self):
        """Check if user can access this withdrawal"""
        try:
            withdrawal = WithdrawalRequest.objects.get(
                id=self.withdrawal_id,
                account__user=self.user
            )
            return True
        except WithdrawalRequest.DoesNotExist:
            return False

class DepositConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = f"deposit_{self.user.id}"
        self.room_group_name = f"deposit_updates_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def deposit_update(self, event):
        """Handle deposit update message"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'deposit_update',
            'data': event['data']
        }))

class BalanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            f'user_balance_{self.scope["user"].id}',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f'user_balance_{self.scope["user"].id}',
            self.channel_name
        )

    async def balance_update(self, event):
        # Send balance update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'balance_update',
            'balance': event['balance']
        })) 