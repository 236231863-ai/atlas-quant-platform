"""Autonomous Research Advisor v3 - generate questions, analyze experiments, suggest next steps."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

class AutonomousResearchAdvisor:
    @staticmethod
    def generate_questions(experiment_history: List[Dict[str, Any]]) -> List[str]:
        questions = []
        if not experiment_history:
            return ["What is the baseline performance of random selection?",
                    "How do gap-based strategies compare to frequency-based?",
                    "What is the impact of portfolio diversity on risk?"]
        metrics_list = [e.get("metrics", {}) for e in experiment_history]
        sharpe_ratios = [m.get("sharpe_ratio", 0) for m in metrics_list]
        if sharpe_ratios and max(sharpe_ratios) < 0.5:
            questions.append("Which parameter combination maximizes Sharpe ratio?")
        rois = [m.get("roi", 0) for m in metrics_list]
        if rois and min(rois) < -20:
            questions.append("How can we reduce downside risk?")
        questions.append("What is the optimal balance between gap and entropy features?")
        if len(experiment_history) >= 5:
            questions.append("Which strategy has been most consistent across experiments?")
        return questions

    @staticmethod
    def analyze_experiments(experiments: List[Dict[str, Any]]) -> str:
        if not experiments: return "No experiments to analyze."
        metrics_list = [e.get("metrics", {}) for e in experiments]
        avg_sharpe = sum(m.get("sharpe_ratio", 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0
        avg_roi = sum(m.get("roi", 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0
        best_idx = max(range(len(experiments)), key=lambda i: experiments[i].get("metrics", {}).get("sharpe_ratio", -999)) if experiments else 0
        best = experiments[best_idx] if experiments else {}
        return (f"Analyzed {len(experiments)} experiments. "
                f"Average Sharpe: {avg_sharpe:.2f}, Average ROI: {avg_roi:.1f}%. "
                f"Best experiment: {best.get('params', 'N/A')}")

    @staticmethod
    def suggest_next(experiment_history: List[Dict[str, Any]], model_registry_data: List[Dict[str, Any]]) -> List[str]:
        suggestions = []
        if not experiment_history:
            return ["Run a random strategy baseline", "Test cold number tracking", "Evaluate portfolio diversification"]
        metrics_list = [e.get("metrics", {}) for e in experiment_history]
        rois = [m.get("roi", 0) for m in metrics_list]
        if rois and max(rois) < 0:
            suggestions.append("Current strategies are all losing. Try completely different parameter ranges.")
        sharpe_list = [m.get("sharpe_ratio", 0) for m in metrics_list]
        if sharpe_list and max(sharpe_list) > 1.0:
            best_sharpe = max(sharpe_list)
            suggestions.append(f"Best Sharpe is {best_sharpe:.2f}. Fine-tune the best performing parameters.")
        if len(experiment_history) < 10:
            suggestions.append("Run more experiments to build statistically significant results.")
        if model_registry_data:
            suggestions.append(f"Review {len(model_registry_data)} registered models for additional insights.")
        if not suggestions:
            suggestions.append("Continue optimization with current best parameters.")
        return suggestions

    @staticmethod
    def summarize_evolution(experiment_history: List[Dict[str, Any]]) -> str:
        if not experiment_history: return "No experiment history available."
        metrics_list = [e.get("metrics", {}) for e in experiment_history]
        sharpe_values = [m.get("sharpe_ratio", 0) for m in metrics_list]
        roi_values = [m.get("roi", 0) for m in metrics_list]
        sharpe_trend = "improving" if len(sharpe_values) > 2 and sharpe_values[-1] > sharpe_values[0] else "stable" if len(sharpe_values) > 2 else "insufficient data"
        roi_trend = "improving" if len(roi_values) > 2 and roi_values[-1] > roi_values[0] else "stable" if len(roi_values) > 2 else "insufficient data"
        return (f"Experiment evolution: {len(experiment_history)} experiments completed. "
                f"Sharpe trend: {sharpe_trend}. ROI trend: {roi_trend}. "
                f"Range: Sharpe [{min(sharpe_values):.2f}, {max(sharpe_values):.2f}], "
                f"ROI [{min(roi_values):.1f}%, {max(roi_values):.1f}%]")
