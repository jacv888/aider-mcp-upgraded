# 📋 Bootstrap Output Format Specification

## **Preferred Bootstrap Output Format**

When responding to "BOOTSTRAP SESSION" or similar commands, always use this concise format:

```
🔄 Context Loading...
--------------------------------------------------
📂 Found: {WORKSPACE_DIR}/ai-logs/active/[latest].md
📋 Last activity: [Previous session summary]

💾 Aider History Status...
--------------------------------------------------
📊 Backed up: [X] sessions, $[X] total cost
📏 Current size: [X]MB (healthy)
🏥 System Health: [healthy/degraded/unhealthy]

💰 Cost Optimization
--------------------------------------------------
💸 Costs: $[X] today, $[X] this month
⚡ Savings: $[X] estimated savings this month ([X]% efficiency)
🎯 Target elements identified: [X] functions/classes
🚀 Token efficiency: Strategic model selection working ([X] sessions optimized)

⚡ Auto-Detection Performance (Real Metrics) ⚡
--------------------------------------------------
📊 Total Optimizations: [X] (measured)
🎯 Average Token Reduction: [X]% (measured)
🔧 Elements Detected: [X] (measured)
📅 Sessions Today: Active development ongoing
✅ Ready to continue with [project-name]
```

## **Key Requirements**

- **Concise**: No verbose explanations or multiple sections
- **Data-focused**: Show real metrics, no placeholders
- **Action-ready**: End with "Ready to continue with [project-name]"
- **Consistent format**: Always use this exact structure

## **Implementation**

1. **Script updated**: `app/scripts/bootstrap_with_template.py` generates this format
2. **Documentation updated**: `prompts/bootstrap-context_v1.md` includes format spec
3. **Validation**: Template validation ensures real data is used

## **Benefits**

- Quick scan of system status
- Real metrics at a glance
- Ready state confirmation
- Consistent user experience
