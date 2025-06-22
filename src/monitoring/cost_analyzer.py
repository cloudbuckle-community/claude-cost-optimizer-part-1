from time import sleep

import boto3
import json
from collections import defaultdict
from datetime import datetime


class BedrockRealCostAnalyzer:
    def __init__(self, region='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.patterns = defaultdict(list)
        self.pricing = {
            'claude-3-5-haiku': {'input': 0.0008, 'output': 0.0024},
            'claude-3-5-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-4-sonnet': {'input': 0.01, 'output': 0.05}
        }

    def analyze_real_request(self, query, model_id='us.anthropic.claude-3-5-sonnet-20241022-v2:0'):
        """Make actual Bedrock API call and track real costs"""
        try:
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [
                        {'role': 'user', 'content': query}
                    ],
                    'max_tokens': 100
                })
            )

            result = json.loads(response['body'].read())
            usage = result.get('usage', {})

            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)

            cost = self.calculate_cost(model_id, input_tokens, output_tokens)
            query_type = self._classify_query(query)

            # Track the real request
            self.patterns['requests'].append({
                'query': query[:50] + "..." if len(query) > 50 else query,
                'model': model_id,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost,
                'type': query_type,
                'response_length': len(result.get('content', [{}])[0].get('text', '')),
                'timestamp': datetime.now().isoformat()
            })

            return {
                'cost': cost,
                'query_type': query_type,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'response': result.get('content', [{}])[0].get('text', '')[:100] + "..."
            }

        except Exception as e:
            print(f"Error processing query: {e}")
            return None

    def calculate_cost(self, model_id, input_tokens, output_tokens):
        # Extract model name for pricing lookup
        if 'haiku' in model_id:
            model_key = 'claude-3-5-haiku'
        elif 'claude-4' in model_id:
            model_key = 'claude-4-sonnet'
        else:
            model_key = 'claude-3-5-sonnet'

        pricing = self.pricing[model_key]
        return (input_tokens / 1000 * pricing['input']) + (output_tokens / 1000 * pricing['output'])

    def _classify_query(self, query):
        query_lower = query.lower()
        word_count = len(query.split())

        # Simple query patterns
        simple_patterns = ['what is', 'how do', 'where can', 'when does', 'price', 'cost', 'hours']
        if word_count < 10 or any(phrase in query_lower for phrase in simple_patterns):
            return 'simple'

        # Complex query patterns
        complex_patterns = ['analyze', 'explain', 'compare', 'evaluate', 'assess', 'detailed']
        if any(word in query_lower for word in complex_patterns):
            return 'complex'

        return 'medium'

    def get_cost_breakdown(self):
        if not self.patterns['requests']:
            return {
                'total_requests': 0,
                'total_cost': 0,
                'avg_cost_per_request': 0,
                'breakdown_by_type': {}
            }

        total_cost = sum(req['cost'] for req in self.patterns['requests'])
        by_type = defaultdict(lambda: {'count': 0, 'cost': 0, 'avg_tokens': {'input': 0, 'output': 0}})

        for req in self.patterns['requests']:
            req_type = req['type']
            by_type[req_type]['count'] += 1
            by_type[req_type]['cost'] += req['cost']
            by_type[req_type]['avg_tokens']['input'] += req['input_tokens']
            by_type[req_type]['avg_tokens']['output'] += req['output_tokens']

        # Calculate averages
        for req_type in by_type:
            count = by_type[req_type]['count']
            by_type[req_type]['avg_cost'] = round(by_type[req_type]['cost'] / count, 4)
            by_type[req_type]['avg_tokens']['input'] = round(by_type[req_type]['avg_tokens']['input'] / count, 1)
            by_type[req_type]['avg_tokens']['output'] = round(by_type[req_type]['avg_tokens']['output'] / count, 1)

        return {
            'total_requests': len(self.patterns['requests']),
            'total_cost': round(total_cost, 4),
            'avg_cost_per_request': round(total_cost / len(self.patterns['requests']), 4),
            'breakdown_by_type': dict(by_type)
        }


# Real production test
if __name__ == "__main__":
    analyzer = BedrockRealCostAnalyzer()

    # Real queries you might see in production
    test_queries = [
        "What are your business hours?",
        "How do I reset my password?",
        "What's the price of your premium plan?",
        "Analyze the performance implications of implementing a microservices architecture vs monolithic approach for our e-commerce platform",
        "Compare the benefits and drawbacks of React vs Vue.js for building our customer dashboard",
        "Explain the security considerations when implementing OAuth2 authentication in a distributed system"
    ]

    print("Making real Bedrock API calls to analyze cost patterns...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        sleep(5)
        result = analyzer.analyze_real_request(query)

        if result:
            print(f"   Cost: ${result['cost']:.4f}")
            print(f"   Type: {result['query_type']}")
            print(f"   Tokens: {result['input_tokens']} → {result['output_tokens']}")
            print(f"   Response preview: {result['response']}")

        print()

    print("REAL COST ANALYSIS:")
    breakdown = analyzer.get_cost_breakdown()

    if breakdown['total_requests'] == 0:
        print("No requests were processed successfully. Check your AWS credentials and permissions.")
    else:
        print(json.dumps(breakdown, indent=2))

        # Calculate potential savings with smart routing
        simple_requests = breakdown['breakdown_by_type'].get('simple', {}).get('count', 0)
        total_requests = breakdown['total_requests']

        if simple_requests > 0:
            simple_avg_cost = breakdown['breakdown_by_type']['simple']['avg_cost']
            haiku_cost = simple_avg_cost * 0.27  # Haiku is ~73% cheaper than Sonnet
            potential_savings = (simple_avg_cost - haiku_cost) * simple_requests

            print(f"\nOPTIMIZATION OPPORTUNITY:")
            print(
                f"   {simple_requests}/{total_requests} queries are simple ({simple_requests / total_requests * 100:.1f}%)")
            print(f"   Routing simple queries to Haiku could save: ${potential_savings:.4f}")
            print(f"   That's a {potential_savings / breakdown['total_cost'] * 100:.1f}% reduction in total costs!")
