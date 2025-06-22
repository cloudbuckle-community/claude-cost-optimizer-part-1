import boto3
import json
import re
from textstat import flesch_reading_ease
from datetime import datetime


class EnhancedRouter:
    """
    Production-grade router that complements AWS Intelligent Prompt Routing
    with operational visibility and custom logic capabilities.
    """

    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.simple_patterns = [
            r'\b(what is|how do|where can|when does|can i)\b',
            r'\b(price|cost|pricing|fee|hours)\b',
            r'\b(cancel|refund|return|location)\b',
            r'\b(yes|no|thanks|hello|hi)\b'
        ]
        self.pricing = {
            'haiku': {'input': 0.0008, 'output': 0.0024},
            'sonnet': {'input': 0.003, 'output': 0.015}
        }

    def route_with_reasoning(self, query):
        """
        Enhanced routing with full transparency - unlike managed services,
        this shows you exactly why each routing decision was made.
        """
        # Quick pattern matching for obvious simple queries
        if self._is_simple_pattern(query):
            return 'haiku', 'pattern_match', 0.1

        # Multi-factor complexity analysis
        complexity_score = self._calculate_complexity(query)

        # Route based on customizable complexity threshold
        if complexity_score < 0.6:
            return 'haiku', 'complexity_analysis', complexity_score
        else:
            return 'sonnet', 'complexity_analysis', complexity_score

    def _is_simple_pattern(self, query):
        """Pattern matching for obviously simple queries"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.simple_patterns)

    def _calculate_complexity(self, query):
        """
        Multi-factor complexity scoring with full transparency.
        Production teams can audit and tune these weights for their domain.
        """
        word_count = len(query.split())

        # Reading complexity factor
        try:
            reading_ease = flesch_reading_ease(query)
            reading_complexity = max(0, (100 - reading_ease) / 100)
        except:
            reading_complexity = 0.5

        # Length complexity factor
        word_complexity = min(word_count / 50, 1.0)

        # Technical vocabulary factor
        technical_terms = ['analyze', 'compare', 'evaluate', 'implement', 'architecture',
                           'performance', 'security', 'optimization', 'framework', 'scalability']
        tech_factor = sum(1 for term in technical_terms if term in query.lower()) * 0.1

        # Weighted combination (fully customizable for your domain)
        complexity = (reading_complexity * 0.5 +
                      word_complexity * 0.3 +
                      min(tech_factor, 0.2) * 0.2)

        return min(complexity, 1.0)


class RoutingAnalyzer:
    """
    Provides operational intelligence that complements AWS CloudWatch
    with routing-specific cost insights and decision transparency.
    """

    def __init__(self):
        self.router = EnhancedRouter()
        self.results = []

    def analyze_query_with_enhanced_routing(self, query):
        """
        Analyze query with enhanced routing vs baseline approach.
        Provides the cost visibility that managed services don't expose.
        """
        # Enhanced routing with full reasoning
        optimal_model, routing_reason, complexity = self.router.route_with_reasoning(query)
        model_id = self._get_model_id(optimal_model)

        # Make actual API call with optimal model
        result = self._make_api_call(query, model_id, optimal_model)

        # Calculate baseline cost comparison
        baseline_cost = self._calculate_baseline_cost(result['input_tokens'], result['output_tokens'])
        savings = baseline_cost - result['actual_cost']
        savings_percent = (savings / baseline_cost * 100) if baseline_cost > 0 else 0

        analysis_result = {
            'query': query[:60] + "..." if len(query) > 60 else query,
            'routed_to': optimal_model,
            'routing_reason': routing_reason,
            'complexity_score': complexity,
            'actual_cost': result['actual_cost'],
            'baseline_cost': baseline_cost,
            'savings': savings,
            'savings_percent': savings_percent,
            'input_tokens': result['input_tokens'],
            'output_tokens': result['output_tokens'],
            'response_preview': result['response'][:80] + "..."
        }

        self.results.append(analysis_result)
        return analysis_result

    def _get_model_id(self, model_name):
        """Convert model name to AWS model ID"""
        model_ids = {
            'haiku': 'us.anthropic.claude-3-5-haiku-20241022-v1:0',
            'sonnet': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
        }
        return model_ids[model_name]

    def _make_api_call(self, query, model_id, model_name):
        """Make actual Bedrock API call with error handling"""
        try:
            response = self.router.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [{'role': 'user', 'content': query}],
                    'max_tokens': 200
                })
            )

            result = json.loads(response['body'].read())
            usage = result.get('usage', {})

            cost = self._calculate_cost(
                model_name,
                usage.get('input_tokens', 0),
                usage.get('output_tokens', 0)
            )

            return {
                'actual_cost': cost,
                'input_tokens': usage.get('input_tokens', 0),
                'output_tokens': usage.get('output_tokens', 0),
                'response': result.get('content', [{}])[0].get('text', '')
            }

        except Exception as e:
            print(f"   API call failed: {e}")
            return {
                'actual_cost': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'response': 'API call failed'
            }

    def _calculate_cost(self, model_name, input_tokens, output_tokens):
        """Calculate actual cost with transparent pricing"""
        pricing = self.router.pricing[model_name]
        return (input_tokens / 1000 * pricing['input']) + (output_tokens / 1000 * pricing['output'])

    def _calculate_baseline_cost(self, input_tokens, output_tokens):
        """Calculate what cost would be with always-Sonnet approach"""
        return self._calculate_cost('sonnet', input_tokens, output_tokens)

    def get_operational_summary(self):
        """
        Generate operational intelligence summary.
        This provides insights that help optimize beyond basic managed services.
        """
        if not self.results:
            return {"message": "No routing data to analyze"}

        total_actual_cost = sum(r['actual_cost'] for r in self.results)
        total_baseline_cost = sum(r['baseline_cost'] for r in self.results)
        total_savings = total_baseline_cost - total_actual_cost
        total_savings_percent = (total_savings / total_baseline_cost * 100) if total_baseline_cost > 0 else 0

        haiku_queries = [r for r in self.results if r['routed_to'] == 'haiku']
        sonnet_queries = [r for r in self.results if r['routed_to'] == 'sonnet']

        pattern_matches = [r for r in self.results if r['routing_reason'] == 'pattern_match']
        complexity_routes = [r for r in self.results if r['routing_reason'] == 'complexity_analysis']

        return {
            'total_queries_analyzed': len(self.results),
            'routing_distribution': {
                'haiku': len(haiku_queries),
                'sonnet': len(sonnet_queries)
            },
            'routing_methods': {
                'pattern_match': len(pattern_matches),
                'complexity_analysis': len(complexity_routes)
            },
            'cost_analysis': {
                'total_actual_cost': round(total_actual_cost, 4),
                'total_baseline_cost': round(total_baseline_cost, 4),
                'total_savings': round(total_savings, 4),
                'cost_reduction_percentage': round(total_savings_percent, 1)
            },
            'complexity_insights': {
                'avg_complexity_haiku': round(sum(r['complexity_score'] for r in haiku_queries) / len(haiku_queries),
                                              2) if haiku_queries else 0,
                'avg_complexity_sonnet': round(sum(r['complexity_score'] for r in sonnet_queries) / len(sonnet_queries),
                                               2) if sonnet_queries else 0
            }
        }


# Production routing analysis demo
if __name__ == "__main__":
    analyzer = RoutingAnalyzer()

    # Real-world query scenarios for production testing
    test_queries = [
        "What are your business hours?",
        "Hi, how are you today?",
        "What's the price of your premium plan?",
        "How do I cancel my subscription?",
        "Can you help me troubleshoot a login issue?",
        "Analyze the performance trade-offs between using Redis vs MongoDB for session storage in a high-traffic web application",
        "Compare the security implications of JWT vs traditional session-based authentication for a distributed microservices architecture"
    ]

    print("Enhanced Model Routing Analysis")
    print("Providing operational intelligence beyond AWS managed services\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        result = analyzer.analyze_query_with_enhanced_routing(query)

        if result['actual_cost'] > 0:  # Successful API call
            print(f"   Complexity Score: {result['complexity_score']:.2f}")
            print(f"   Routed to: {result['routed_to'].upper()} (reason: {result['routing_reason']})")
            print(f"   Cost: ${result['actual_cost']:.4f} (vs ${result['baseline_cost']:.4f} baseline)")
            print(f"   Savings: ${result['savings']:.4f} ({result['savings_percent']:.1f}%)")
            print(f"   Tokens: {result['input_tokens']} -> {result['output_tokens']}")
        print()

    print("OPERATIONAL ROUTING INTELLIGENCE:")
    summary = analyzer.get_operational_summary()
    print(json.dumps(summary, indent=2))

    if 'cost_analysis' in summary:
        cost_data = summary['cost_analysis']
        routing_data = summary['routing_distribution']

        print(f"\nENHANCED ROUTING VALUE:")
        print(f"   Total cost optimization: ${cost_data['total_savings']:.4f}")
        print(f"   Cost reduction achieved: {cost_data['cost_reduction_percentage']:.1f}%")
        print(
            f"   Routing efficiency: {routing_data['haiku']}/{summary['total_queries_analyzed']} queries optimized to Haiku")
        print(f"   Decision transparency: Full routing reasoning provided for operational debugging")