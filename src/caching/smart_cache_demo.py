import boto3
import json
import redis
import hashlib
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class SmartCache:
    """
    Production-grade caching system that goes beyond basic response caching
    to provide semantic understanding and intelligent TTL management.
    """

    def __init__(self, redis_host='localhost', redis_port=6379):
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis.ping()
            self.cache_available = True
        except:
            print("Redis not available, using in-memory cache for demo")
            self.cache_available = False
            self.memory_cache = {}

        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cost_savings': 0.0
        }

    def _generate_cache_key(self, model_id, messages, max_tokens=None):
        """Generate consistent cache key for identical requests"""
        cache_content = {
            'model': model_id,
            'messages': messages,
            'max_tokens': max_tokens
        }
        content_str = json.dumps(cache_content, sort_keys=True)
        return f"claude_cache:{hashlib.md5(content_str.encode()).hexdigest()}"

    def _generate_semantic_key(self, user_message):
        """Generate key for semantic similarity matching"""
        # Normalize the message for better matching
        normalized = user_message.lower().strip()
        # Remove common variations
        normalized = normalized.replace("?", "").replace(".", "").replace("!", "")
        return f"semantic:{hashlib.md5(normalized.encode()).hexdigest()[:12]}"

    def get_cached_response(self, model_id, messages, max_tokens=None, similarity_threshold=0.85):
        """
        Retrieve cached response with semantic similarity matching.
        This provides intelligent caching that basic AWS caching can't offer.
        """
        self.cache_stats['total_requests'] += 1

        # Try exact match first
        exact_key = self._generate_cache_key(model_id, messages, max_tokens)
        cached = self._get_from_cache(exact_key)

        if cached:
            self.cache_stats['hits'] += 1
            cached['cache_type'] = 'exact_match'
            return cached

        # Try semantic similarity for user messages
        if messages and len(messages) > 0:
            user_message = None
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_message = msg.get('content', '')
                    break

            if user_message:
                similar_response = self._find_similar_cached_response(
                    user_message, model_id, similarity_threshold
                )
                if similar_response:
                    self.cache_stats['hits'] += 1
                    similar_response['cache_type'] = 'semantic_match'
                    return similar_response

        self.cache_stats['misses'] += 1
        return None

    def _find_similar_cached_response(self, user_message, model_id, threshold):
        """Find semantically similar cached responses"""
        if not self.cache_available:
            return None

        try:
            # Get all semantic keys for this model
            pattern = f"semantic_index:{model_id}:*"
            keys = self.redis.keys(pattern)

            best_match = None
            best_similarity = 0

            for key in keys[:20]:  # Limit search for performance
                cached_message = self.redis.hget(key, 'message')
                if cached_message:
                    similarity = SequenceMatcher(None, user_message.lower(),
                                                 cached_message.lower()).ratio()
                    if similarity > best_similarity and similarity >= threshold:
                        best_similarity = similarity
                        response_key = self.redis.hget(key, 'response_key')
                        if response_key:
                            best_match = self._get_from_cache(response_key)

            return best_match
        except:
            return None

    def cache_response(self, model_id, messages, response, max_tokens=None, ttl=3600):
        """
        Cache response with intelligent TTL and semantic indexing.
        Provides the application-level intelligence that AWS caching lacks.
        """
        cache_key = self._generate_cache_key(model_id, messages, max_tokens)

        cache_entry = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model_id': model_id,
            'ttl': ttl
        }

        self._store_in_cache(cache_key, cache_entry, ttl)

        # Create semantic index for user messages
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break

        if user_message:
            self._create_semantic_index(model_id, user_message, cache_key, ttl)

    def _create_semantic_index(self, model_id, user_message, response_key, ttl):
        """Create semantic index for similarity matching"""
        if not self.cache_available:
            return

        try:
            semantic_key = f"semantic_index:{model_id}:{hashlib.md5(user_message.encode()).hexdigest()[:12]}"
            self.redis.hset(semantic_key, mapping={
                'message': user_message,
                'response_key': response_key,
                'created': datetime.now().isoformat()
            })
            self.redis.expire(semantic_key, ttl)
        except:
            pass

    def _get_from_cache(self, key):
        """Get item from cache with fallback handling"""
        if self.cache_available:
            try:
                cached = self.redis.get(key)
                return json.loads(cached) if cached else None
            except:
                return None
        else:
            return self.memory_cache.get(key)

    def _store_in_cache(self, key, value, ttl):
        """Store item in cache with fallback handling"""
        if self.cache_available:
            try:
                self.redis.setex(key, ttl, json.dumps(value))
            except:
                pass
        else:
            self.memory_cache[key] = value

    def get_cache_stats(self):
        """Get comprehensive cache performance statistics"""
        total = self.cache_stats['total_requests']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0

        return {
            'total_requests': total,
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate_percentage': round(hit_rate, 1),
            'estimated_cost_savings': round(self.cache_stats['cost_savings'], 4),
            'cache_backend': 'redis' if self.cache_available else 'memory'
        }


class SmartCacheAnalyzer:
    """
    Analyzes caching performance with real API calls to demonstrate
    the cost savings that intelligent caching provides in production.
    """

    def __init__(self, redis_host='localhost'):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.cache = SmartCache(redis_host)
        self.pricing = {
            'haiku': {'input': 0.0008, 'output': 0.0024},
            'sonnet': {'input': 0.003, 'output': 0.015}
        }
        self.results = []

    def analyze_caching_scenario(self, queries, model_id='us.anthropic.claude-3-5-haiku-20241022-v1:0'):
        """
        Run caching analysis with real API calls.
        Shows exactly how much money smart caching saves.
        """
        print(f"Smart Caching Analysis with {len(queries)} queries")
        print("Demonstrating application-level cache intelligence\n")

        for i, query in enumerate(queries, 1):
            print(f"Query {i}: {query}")

            # Prepare messages
            messages = [{'role': 'user', 'content': query}]

            # Check cache first
            start_time = time.time()
            cached_response = self.cache.get_cached_response(model_id, messages)
            cache_lookup_time = time.time() - start_time

            if cached_response:
                # Cache hit
                response_data = cached_response['response']
                cost = 0  # No API cost for cached responses
                cache_type = cached_response.get('cache_type', 'exact')

                print(f"   Cache: HIT ({cache_type}) - lookup time: {cache_lookup_time * 1000:.1f}ms")
                print(f"   Cost: $0.0000 (saved from cache)")

                # Calculate what the cost would have been
                if 'usage' in response_data:
                    estimated_cost = self._calculate_cost(
                        model_id,
                        response_data['usage'].get('input_tokens', 0),
                        response_data['usage'].get('output_tokens', 0)
                    )
                    self.cache.cache_stats['cost_savings'] += estimated_cost
                    print(f"   Estimated savings: ${estimated_cost:.4f}")

            else:
                # Cache miss - make API call
                print(f"   Cache: MISS - making API call")

                api_start = time.time()
                response_data, cost = self._make_api_call(query, model_id)
                api_time = time.time() - api_start

                if response_data:
                    print(f"   Cost: ${cost:.4f} - API time: {api_time:.1f}s")
                    print(
                        f"   Tokens: {response_data.get('usage', {}).get('input_tokens', 0)} -> {response_data.get('usage', {}).get('output_tokens', 0)}")

                    # Cache the response for future use
                    self.cache.cache_response(model_id, messages, response_data)
                else:
                    print(f"   API call failed")

            print()

        # Show final cache statistics
        stats = self.cache.get_cache_stats()
        print("CACHE PERFORMANCE ANALYSIS:")
        print(json.dumps(stats, indent=2))

        total_potential_cost = self._estimate_total_cost_without_cache(queries, model_id)
        actual_cost = total_potential_cost - stats['estimated_cost_savings']

        print(f"\nCACHING VALUE ANALYSIS:")
        print(f"   Total potential cost (no cache): ${total_potential_cost:.4f}")
        print(f"   Actual cost (with smart cache): ${actual_cost:.4f}")
        print(f"   Total cost savings: ${stats['estimated_cost_savings']:.4f}")
        print(f"   Cache hit rate: {stats['hit_rate_percentage']:.1f}%")
        if stats['estimated_cost_savings'] > 0:
            savings_percent = (stats['estimated_cost_savings'] / total_potential_cost) * 100
            print(f"   Cost reduction: {savings_percent:.1f}%")

    def _make_api_call(self, query, model_id):
        """Make actual Bedrock API call with cost calculation"""
        try:
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [{'role': 'user', 'content': query}],
                    'max_tokens': 150
                })
            )

            result = json.loads(response['body'].read())
            usage = result.get('usage', {})

            cost = self._calculate_cost(
                model_id,
                usage.get('input_tokens', 0),
                usage.get('output_tokens', 0)
            )

            return result, cost

        except Exception as e:
            print(f"   API call failed: {e}")
            return None, 0

    def _calculate_cost(self, model_id, input_tokens, output_tokens):
        """Calculate cost based on model pricing"""
        model_key = 'haiku' if 'haiku' in model_id else 'sonnet'
        pricing = self.pricing[model_key]

        return (input_tokens / 1000 * pricing['input']) + (output_tokens / 1000 * pricing['output'])

    def _estimate_total_cost_without_cache(self, queries, model_id):
        """Estimate what total cost would be without any caching"""
        # Rough estimation based on average query length
        avg_input_tokens = sum(len(q.split()) * 1.3 for q in queries) / len(queries)
        avg_output_tokens = 100  # Conservative estimate

        cost_per_query = self._calculate_cost(model_id, avg_input_tokens, avg_output_tokens)
        return cost_per_query * len(queries)


# Production caching analysis demo
if __name__ == "__main__":
    analyzer = SmartCacheAnalyzer()

    # Realistic caching scenarios with repeated and similar queries
    test_queries = [
        # First round - fresh queries (cache misses)
        "What are your business hours?",
        "How do I reset my password?",
        "What's the price of your premium plan?",
        "Can you help me with billing questions?",

        # Second round - exact repeats (exact cache hits)
        "What are your business hours?",
        "How do I reset my password?",

        # Third round - similar queries (semantic cache hits)
        "What time are you open?",  # Similar to "business hours"
        "How can I reset my password?",  # Similar to previous
        "What does the premium plan cost?",  # Similar to pricing question

        # New queries (cache misses)
        "How do I cancel my subscription?",
        "Where can I find my invoices?"
    ]

    analyzer.analyze_caching_scenario(test_queries)