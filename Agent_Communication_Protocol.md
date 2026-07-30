# Agent Communication Protocol

## Overview
Standard communication layer for multi-agent research teams.

## Data Types
- ResearchTask: task_id, type, objective, params
- ResearchMessage: message_id, sender, recipient, content
- AgentResult: agent_id, task_id, result, confidence
- AgentFeedback: agent_id, target_id, feedback_type, content

## Protocol API
- create_task(), get_task()
- send_message(), receive_messages()
- trace_history(), validate_message()
- All communication is recorded and traceable
