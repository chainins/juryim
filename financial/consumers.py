from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import WithdrawalRequest

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