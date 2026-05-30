# Desi Cine Bot 🎬

A daily notification bot that tracks local movie schedules, filters for Indian cinema, and alerts you with direct ticket links.

<div style="margin-bottom: 20px;"></div>

<h2>🔄 Process Workflow</h2>

<div style="margin-top: 0px; margin-bottom: -35px;">

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1e293b',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#38bdf8',
    'lineColor': '#94a3b8',
    'secondaryColor': '#0f172a',
    'tertiaryColor': '#1e293b',
    'mainBkg': '#1e293b',
    'actorBkg': '#1e293b'
  },
  'flowchart': {
    'htmlLabels': true,
    'curve': 'linear',
    'padding': 10
  }
}}%%
graph LR
    A[Every Morning] --> B[Fetch Local Movies List]
    B --> C[Extract Details & Theater Links]
    C --> D([Is Language Indian & Nearby?])
    
    D --->|Yes| E[Send Notification Alert]
    D --->|No| F[Skip Movie]
    
    style A fill:#0284c7,stroke:#0ea5e9,stroke-width:2px
    style B fill:#0d9488,stroke:#2dd4bf,stroke-width:2px
    style C fill:#c2410c,stroke:#f97316,stroke-width:2px
    style D fill:#475569,stroke:#e2e8f0,stroke-width:2px
    style E fill:#16a34a,stroke:#4ade80,stroke-width:2px
    style F fill:#dc2626,stroke:#f87171,stroke-width:2px
