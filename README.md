```
kubectl port-forward svc/ai-agent-head-svc 8265:8265
```
```
kubectl port-forward svc/ai-agent-serve-svc 8000:8000
```
```
for i in {1..20}; do   curl -X POST http://localhost:8000/chat     -H "Content-Type: application/json"     -d '{"message":"hai"}' & done
```
