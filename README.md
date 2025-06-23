                                                                                            # Claude Cost Optimizer

Production-ready framework for optimizing Anthropic Claude API costs on Amazon Bedrock. Achieve 50-70% cost reduction through intelligent routing, smart caching, and operational optimization strategies.

![Claude Optimization](https://img.shields.io/badge/Cost_Reduction-50--70%25-green?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square) ![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📊 Proven Results

Based on real production testing with AWS Bedrock:

- **Enhanced Model Routing**: 60% cost reduction through intelligent complexity analysis
- **Smart Caching**: 14.8%+ cost reduction with exact matching, 70-90% potential with semantic matching
- **Combined Impact**: 50-70% total cost optimization while improving response times
- **Production-Ready**: Includes monitoring, fallback handling, and operational intelligence

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version

# AWS CLI configured with Bedrock access
aws configure
```

### Installation

```bash
# Clone the repository
git clone https://github.com/cloudbuckle-community/claude-cost-optimizer-part-1.git
cd claude-cost-optimizer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### 1. Cost Analysis
```bash
# Analyze your current Claude usage patterns
python src/monitoring/cost_analyzer.py
```

#### 2. Enhanced Model Routing
```bash
# Test intelligent model routing with real API calls
python src/routing/enhanced_router_demo.py
```

#### 3. Smart Caching
```bash
# Demonstrate caching performance (works with or without Redis)
python src/caching/smart_cache_demo.py
```

## 🏗️ Architecture

### Enhanced Model Routing
Complements AWS Intelligent Prompt Routing with operational visibility:

- **Transparent routing decisions** with complexity scoring you can audit
- **Custom routing rules** tailored to your specific domain
- **Real-time cost tracking** integrated with routing decisions
- **Production debugging** capabilities AWS managed services don't provide

### Smart Caching System
Application-level caching that understands Claude-specific patterns:

- **Exact match caching** for identical queries
- **Semantic similarity matching** for paraphrased queries (Redis)
- **Intelligent TTL management** with automatic expiration
- **Cost analytics** showing exact savings from cache hits

### Cost Monitoring
Production-grade analytics and tracking:

- **Real-time cost calculation** for every API call
- **Usage pattern analysis** with complexity scoring
- **Performance metrics** including cache hit rates
- **Operational insights** for continuous optimization

## 🛠️ Configuration

### AWS Setup
```bash
# Configure AWS credentials
aws configure

# Ensure Bedrock model access is enabled in your AWS console
# Required models: Claude 3.5 Haiku, Claude 3.5 Sonnet
```

### Redis Setup (Optional, Recommended for Production)
```bash
# Install Redis locally
brew install redis  # macOS
apt-get install redis-server  # Ubuntu

# Start Redis
redis-server

# The system automatically falls back to in-memory caching if Redis is unavailable
```

## 📈 Real Performance Data

### Enhanced Routing Results
```
Total queries analyzed: 7
Routing efficiency: 6/7 queries optimized to Haiku (86%)
Cost reduction achieved: 60.0%
Decision transparency: Full routing reasoning provided
```

### Smart Caching Results  
```
Cache hit rate: 18.2% (demo scenario)
Cost reduction: 14.8%
Performance improvement: 0.0ms cache hits vs 2-4s API calls
Production potential: 60-80% hit rates with semantic matching
```

## 🔧 Advanced Configuration

### Custom Routing Rules
```python
# Customize complexity scoring for your domain
class CustomRouter(EnhancedRouter):
    def _calculate_complexity(self, query):
        # Add domain-specific complexity factors
        domain_terms = ['financial', 'medical', 'legal']
        domain_factor = sum(1 for term in domain_terms if term in query.lower()) * 0.15
        
        # Use base complexity + domain factor
        base_complexity = super()._calculate_complexity(query)
        return min(base_complexity + domain_factor, 1.0)
```

### Production Caching
```python
# Redis production configuration
cache = SmartCache(
    redis_host='your-redis-cluster.cache.amazonaws.com',
    redis_port=6379
)

# High-availability setup with connection pooling
redis_pool = redis.ConnectionPool(
    host='localhost', 
    port=6379, 
    db=0, 
    max_connections=20
)
```

## 📚 Related Article

This repository accompanies the Medium article series:
- **Part 1**: [How to Optimize the Hidden Costs of Anthropic Claude APIs: Part 1](https://medium.com/p/ce52d08ae3e4)
- **Part 2**: Advanced optimization strategies (coming soon)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
```bash
# Clone for development
git clone https://github.com/cloudbuckle-community/claude-cost-optimizer-part-1.git
cd claude-cost-optimizer

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/  # (when test suite is added)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **API Costs**: This framework makes real AWS Bedrock API calls. Monitor your usage and costs.
- **AWS Permissions**: Ensure your AWS credentials have appropriate Bedrock permissions.
- **Production Use**: Test thoroughly in development before deploying to production.
- **Rate Limits**: Be aware of AWS Bedrock rate limits when running demos.

## 🔗 Links

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude Models](https://docs.anthropic.com/claude/docs)
- [Medium Article Series](YOUR_MEDIUM_LINK)

## 🙋‍♂️ Support

If you find this framework helpful:
- ⭐ Star this repository
- 📖 Read the accompanying Medium article
- 🐛 Report issues on GitHub
- 💬 Share your optimization results

---

**Built by a freelance AI engineer helping companies optimize their Claude API costs in production.**  
