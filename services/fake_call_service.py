"""
📞 Fake Call Service - Simulate incoming calls
"""

import threading
import time
from datetime import datetime

class FakeCallService:
    """Service to handle fake calls"""
    
    active_calls = {}
    
    @staticmethod
    def schedule_fake_call(user_id, caller_name, caller_number, delay=3):
        """Schedule a fake call after delay"""
        def make_call():
            time.sleep(delay)
            FakeCallService.trigger_fake_call(user_id, caller_name, caller_number)
        
        thread = threading.Thread(target=make_call)
        thread.daemon = True
        thread.start()
        
        return {
            'scheduled': True,
            'caller': caller_name,
            'delay': delay,
            'scheduled_time': datetime.now().isoformat()
        }
    
    @staticmethod
    def trigger_fake_call(user_id, caller_name, caller_number):
        """Trigger the fake call"""
        FakeCallService.active_calls[user_id] = {
            'caller_name': caller_name,
            'caller_number': caller_number,
            'start_time': datetime.now(),
            'status': 'ringing'
        }
        
        # This would be sent via WebSocket to the client
        return {
            'incoming_call': True,
            'caller_name': caller_name,
            'caller_number': caller_number
        }
    
    @staticmethod
    def answer_call(user_id):
        """Answer the fake call"""
        if user_id in FakeCallService.active_calls:
            FakeCallService.active_calls[user_id]['status'] = 'connected'
            return {
                'answered': True,
                'message': 'Call connected'
            }
        return {'answered': False}
    
    @staticmethod
    def end_call(user_id):
        """End the fake call"""
        if user_id in FakeCallService.active_calls:
            del FakeCallService.active_calls[user_id]
            return {'ended': True}
        return {'ended': False}
    
    @staticmethod
    def get_active_call(user_id):
        """Get active call status"""
        if user_id in FakeCallService.active_calls:
            return FakeCallService.active_calls[user_id]
        return None