from src.frame_analyzer import FrameAnalyzer
from src.density import DensityAnalyzer
from src.historical_baseline import HistoricalBaseline
from src.rag import RAGSummary


class RAGIntegration:
    def __init__(self):
        self.analyzer = FrameAnalyzer()
        self.density = DensityAnalyzer()
        self.baseline = HistoricalBaseline()
        self.rag = RAGSummary()
    
    def process_frame(self, frame, location, timestamp):
        detection = self.analyzer.analyze_frame(frame, timestamp=timestamp)
        
        if detection is None:
            return None
        
        person_count = detection['person_count']
        
        # Add to history
        self.baseline.add_frame_data(person_count)
        
        # Get density
        density_level = self.density.analyze(person_count)
        z_score = self.density.calculate_z_score(person_count)
        
        # Get real baseline pattern
        pattern = self.baseline.get_pattern(person_count)
        
        if pattern is None:
            baseline_mean = person_count
            context_text = "Establishing baseline..."
        else:
            baseline_mean = pattern['avg_people']
            context_text = (
                f"Baseline: {pattern['avg_people']:.0f}. "
                f"Current: {person_count} ({pattern['deviation_percent']:+.0f}%). "
                f"Peak: {pattern['peak_people']}"
            )
        
        # Generate LLM summary with context
        llm_summary = self.rag.generate_summary(
            zone=location,
            person_count=person_count,
            density_level=density_level,
            baseline_mean=baseline_mean,
            baseline_std=10,
            z_score=z_score
        )
        
        return {
            'detection': {
                'person_count': person_count,
                'centroids': detection['centroids'],
                'bboxes': detection['bboxes'],
                'confidences': detection['confidences'],
                'avg_confidence': detection['avg_confidence']
            },
            'density': {
                'level': density_level,
                'z_score': z_score
            },
            'pattern': pattern,
            'llm': llm_summary,
            'timestamp': timestamp
        }