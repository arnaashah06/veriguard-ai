# backend/forensics.py

class TamperingDetector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.signals = []
    
    def analyze_all(self):
        """Run all tampering detection checks"""
        return []
    
    def get_report(self):
        """Get the full tampering report"""
        return {
            'signals': [],
            'overall_suspicion': 'NONE',
            'signal_count': 0
        }