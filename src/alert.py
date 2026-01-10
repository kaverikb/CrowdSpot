import uuid
from datetime import datetime, timedelta


class AlertGenerator:
    def __init__(self, expiry_minutes=30):
        self.expiry_minutes = expiry_minutes
    
    def create_alert(self, anomaly_result, zone, person_count, baseline_mean):
        alert_id = str(uuid.uuid4())[:8]
        severity = anomaly_result['severity']
        
        if severity == "HIGH":
            anomaly_type = "ATYPICAL_DENSITY_INCREASE"
        elif severity == "MEDIUM":
            anomaly_type = "UNEXPECTED_SPATIAL_CONCENTRATION"
        else:
            anomaly_type = "MINOR_DEVIATION"
        
        message = f"{anomaly_type} detected in {zone}"
        
        if severity == "HIGH":
            operator_note = f"High density ({person_count} people, baseline {int(baseline_mean)}). Verify if event-related."
        elif severity == "MEDIUM":
            operator_note = f"Moderate density increase. Check zone for unusual activity."
        else:
            operator_note = f"Slight deviation from baseline."
        
        expiry = datetime.now() + timedelta(minutes=self.expiry_minutes)
        
        return {
            'alert_id': alert_id,
            'anomaly_type': anomaly_type,
            'severity': severity,
            'zone': zone,
            'timestamp': datetime.now(),
            'person_count': person_count,
            'baseline_density': baseline_mean,
            'message': message,
            'operator_note': operator_note,
            'expiry': expiry,
            'status': 'ACTIVE'
        }
    
    def should_alert(self, severity):
        if severity == "LOW":
            return False
        return True